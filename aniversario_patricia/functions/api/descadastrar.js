// Cloudflare Pages Function: GET/POST /api/descadastrar
// Descadastro funcional exigido por LGPD e pelas ferramentas de envio.
//  - GET  ?e=<email>&t=<token>  → descadastra e devolve página de confirmação
//  - POST ?e=<email>&t=<token>  → one-click do cliente de e-mail (RFC 8058), responde 200
// O token é HMAC-SHA256(email, RESEND_API_KEY), o mesmo gerado em inscrever.js.
// ⚠️ unsubToken aqui e em inscrever.js têm que ficar idênticas.

const SITE = 'https://aniversario-patricia.scorasacademy.com.br';

async function unsubToken(email, secret) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(email.trim().toLowerCase()));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 32);
}

// Comparação em tempo constante, pra não vazar o token por timing.
function safeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

async function unsubscribe(env, email) {
  if (!env.RESEND_API_KEY || !env.AUDIENCE_ID) return { ok: false, reason: 'missing_env' };
  const r = await fetch(
    `https://api.resend.com/audiences/${env.AUDIENCE_ID}/contacts/${encodeURIComponent(email)}`,
    {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ unsubscribed: true }),
    },
  );
  return { ok: r.ok, status: r.status };
}

// Registra o opt-out no KV também, pra ter trilha própria de auditoria LGPD
// mesmo que um dia a base saia do Resend.
async function logOptOut(env, email, resultado) {
  if (!env.INSCRITOS) return;
  const ts = new Date().toISOString();
  await env.INSCRITOS.put(
    `optout:${ts}:${email}`,
    JSON.stringify({ email, timestamp: ts, resend: resultado }),
  );
}

function pagina(titulo, mensagem, sucesso) {
  return `<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<meta name="robots" content="noindex,nofollow" />
<title>${titulo} · Scoras Academy</title></head>
<body style="margin:0;background:#000;color:#f6f6f6;font-family:Inter,Helvetica,Arial,sans-serif;
             display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px;">
  <div style="max-width:520px;background:#0a0a0d;border:1px solid rgba(101,44,242,0.25);
              border-radius:16px;padding:40px 32px;text-align:center;">
    <div style="font-size:11px;letter-spacing:0.18em;color:#33d9d5;text-transform:uppercase;font-weight:600;">
      Scoras Academy
    </div>
    <h1 style="margin:16px 0 12px;font-size:23px;line-height:1.3;color:${sucesso ? '#f6f6f6' : '#ffb4b4'};">
      ${titulo}
    </h1>
    <p style="margin:0;font-size:15px;line-height:1.7;color:rgba(246,246,246,0.7);">${mensagem}</p>
    <a href="${SITE}" style="display:inline-block;margin-top:26px;background:#13131a;
       border:1px solid rgba(255,255,255,0.1);color:#f6f6f6;text-decoration:none;
       padding:13px 26px;border-radius:999px;font-size:14px;">Voltar ao site</a>
  </div>
</body></html>`;
}

function htmlResponse(body, status = 200) {
  return new Response(body, {
    status,
    headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' },
  });
}

async function processar(request, env) {
  const url = new URL(request.url);
  const email = (url.searchParams.get('e') || '').trim().toLowerCase();
  const token = (url.searchParams.get('t') || '').trim();

  if (!email) return { ok: false, titulo: 'Link incompleto', msg: 'O link de descadastro veio sem o e-mail. Escreva para <a href="mailto:suporte@scorasacademy.com.br" style="color:#33d9d5;">suporte@scorasacademy.com.br</a> que resolvemos manualmente.' };

  if (env.RESEND_API_KEY) {
    const esperado = await unsubToken(email, env.RESEND_API_KEY);
    if (!safeEqual(token, esperado)) {
      return { ok: false, titulo: 'Link inválido ou expirado', msg: 'Não conseguimos validar este link de descadastro. Escreva para <a href="mailto:suporte@scorasacademy.com.br" style="color:#33d9d5;">suporte@scorasacademy.com.br</a> que tiramos você da lista na hora.' };
    }
  }

  const r = await unsubscribe(env, email);
  await logOptOut(env, email, r);

  if (!r.ok) {
    return { ok: false, titulo: 'Não foi possível concluir agora', msg: `Houve uma falha ao processar o descadastro de <strong>${esc(email)}</strong>. Escreva para <a href="mailto:suporte@scorasacademy.com.br" style="color:#33d9d5;">suporte@scorasacademy.com.br</a> que fazemos manualmente.` };
  }

  return { ok: true, titulo: 'Pronto, você foi descadastrado', msg: `<strong>${esc(email)}</strong> não vai mais receber nossos e-mails. Se foi engano, é só se cadastrar de novo no site.` };
}

export async function onRequestGet({ request, env }) {
  const r = await processar(request, env);
  return htmlResponse(pagina(r.titulo, r.msg, r.ok), r.ok ? 200 : 400);
}

// One-click do Gmail/Outlook: precisa responder 200 sem corpo HTML.
export async function onRequestPost({ request, env }) {
  const r = await processar(request, env);
  return new Response(null, { status: r.ok ? 200 : 400 });
}

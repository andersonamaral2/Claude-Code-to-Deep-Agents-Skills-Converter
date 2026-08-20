// Cloudflare Pages Function: POST /api/inscrever
// Aniversário de 2 anos da Scoras Academy — aniversario.scorasacademy.com.br
// Recebe { nome, email, whatsapp?, lead_magnet?, origem?, utm_*?, referrer? }
// Promise.allSettled em 4 paths (se um falhar, os outros continuam):
//  1) Adiciona contato na audience Resend (env.AUDIENCE_ID — base única Scoras,
//     compartilhada com as outras landings de propósito; a origem se separa
//     pelo KV próprio e pelo campo lead_magnet/origem do payload)
//  2) Envia o e-book surpresa de IA por e-mail (Resend)
//  3) Backup completo em KV (env.INSCRITOS) sob chave inscrito:<timestamp>:<email>
//  4) Notificação interna pro time

const FROM = 'Cora da Scoras Academy <cora@scorasacademy.com.br>';
// E-mail de entrega é no-reply: quem quiser falar com o time vai pro suporte.
const REPLY_TO = 'suporte@scorasacademy.com.br';
const SITE = 'https://aniversario.scorasacademy.com.br';
const NOTIFY_TO = ['anderson@scoras.com.br', 'patricia@scoras.com.br'];

// Entrega do lead magnet: URL fixa no próprio domínio (nunca anexo — anexo é
// gatilho de spam, e link permite trocar o arquivo sem reenviar e-mail).
const UTM_ENTREGA = 'utm_source=email&utm_medium=entrega&utm_campaign=aniversario_2anos';
const EBOOK_URL = `${SITE}/downloads/ebook-ia-scoras.pdf?${UTM_ENTREGA}&utm_content=ebook_pdf`;

// Menção à promoção no e-mail de entrega: a condição de 19/09 expira, então o
// bloco some sozinho depois do prazo — e-mail perene não promete o que já venceu.
const PROMO = {
  url: `${SITE}/?utm_source=email&utm_medium=ebook&utm_campaign=aniversario_2anos#condicoes`,
  expiraEm: Date.parse('2026-09-19T23:59:59-03:00'),
};
const promoAtiva = () => Date.now() <= PROMO.expiraEm;

// Canais oficiais no rodapé do e-mail de entrega.
const REDES = [
  ['Canal no WhatsApp', 'https://whatsapp.com/channel/0029VbCTFQL90x2yWrk9zp0y'],
  ['YouTube da Scoras', 'https://www.youtube.com/@ScorasAcademy'],
  ['Instagram da Patricia', 'https://www.instagram.com/patricia_costa.ia/'],
  ['LinkedIn da Patricia', 'https://www.linkedin.com/in/patricia-figueiredo-costa/'],
];

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

function badRequest(msg) {
  return jsonResponse({ ok: false, error: msg }, 400);
}

function isValidEmail(e) {
  return typeof e === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
}

function splitName(full) {
  const parts = (full || '').trim().split(/\s+/);
  return { first: parts[0] || '', last: parts.slice(1).join(' ') };
}

// Nome do lead entra em HTML de e-mail: escapa pra não quebrar o template nem virar injeção.
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function rodapeLegal(unsubUrl, motivo) {
  return `      <tr><td style="padding:20px 32px 26px;border-top:1px solid rgba(255,255,255,0.06);font-size:12px;line-height:1.6;color:rgba(246,246,246,0.45);">
        ${motivo}
        <br /><br />
        Este e-mail não recebe respostas. Para falar com o time, escreva para
        <a href="mailto:suporte@scorasacademy.com.br" style="color:rgba(51,217,213,0.8);text-decoration:none;">suporte@scorasacademy.com.br</a>.
        <br /><br />
        <a href="${unsubUrl}" style="color:rgba(246,246,246,0.6);text-decoration:underline;">Descadastrar destes e-mails</a>
        <br /><br />
        Scoras Academy · Scoras Tecnologia Ltda · CNPJ 59.526.498/0001-73 · Complexo Madeira, Alphaville — Barueri/SP
      </td></tr>`;
}

function ebookEmailHtml(nome, unsubUrl) {
  const first = esc(splitName(nome).first) || 'olá';
  const redes = REDES.map(([nomeRede, href]) => `
            <td style="padding:6px 6px 6px 0;">
              <a href="${href}"
                 style="display:inline-block;background:#13131a;border:1px solid rgba(255,255,255,0.1);
                        color:#f6f6f6;text-decoration:none;padding:10px 16px;border-radius:8px;font-size:13px;">
                ${nomeRede}
              </a>
            </td>`).join('');

  // Só aparece enquanto a condição de 19/09 estiver de pé (ver PROMO acima).
  const blocoPromo = promoAtiva() ? `
      <tr><td style="padding:8px 32px 18px;">
        <div style="background:#13131a;border:1px solid rgba(101,44,242,0.25);border-radius:12px;padding:18px 20px;">
          <div style="font-size:11px;letter-spacing:0.16em;color:#33d9d5;text-transform:uppercase;font-weight:600;">E tem mais, só até 19 de setembro</div>
          <div style="margin-top:10px;font-size:14.5px;line-height:1.7;color:rgba(246,246,246,0.85);">
            A promoção de 2 anos da Scoras Academy está no ar: a <strong style="color:#fff;">Formação Continuada</strong>
            por <strong style="color:#33d9d5;">3.999 à vista</strong> (ou 12x de 413,59), com garantia de renovação
            gratuita do segundo ano pra quem concluir 70% dos cursos e não conquistar vaga na área em 12 meses.
          </div>
        </div>
      </td></tr>
      <tr><td style="padding:2px 32px 20px;text-align:center;">
        <a href="${PROMO.url}"
           style="display:inline-block;background:#13131a;border:1px solid rgba(51,217,213,0.4);color:#33d9d5;
                  text-decoration:none;padding:13px 28px;border-radius:999px;font-weight:600;font-size:14px;">
          Ver a promoção de 2 anos
        </a>
      </td></tr>` : '';

  return `<!doctype html>
<html><body style="margin:0;padding:0;background:#000000;font-family:Inter,Helvetica,Arial,sans-serif;color:#f6f6f6;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#000000;">
  <tr><td align="center" style="padding:40px 20px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#0a0a0d;border:1px solid rgba(101,44,242,0.25);border-radius:16px;overflow:hidden;">
      <tr><td style="background:linear-gradient(135deg,#13131a 0%,#0a0a0d 100%);padding:32px 32px 24px;border-bottom:1px solid rgba(255,255,255,0.06);">
        <div style="font-size:11px;letter-spacing:0.18em;color:#33d9d5;text-transform:uppercase;font-weight:600;">— Scoras Academy · 2 anos</div>
        <div style="margin-top:14px;font-size:22px;font-weight:700;line-height:1.25;color:#f6f6f6;">
          O presente é <span style="color:#33d9d5;">seu</span>.
        </div>
        <div style="margin-top:6px;font-size:14px;color:rgba(246,246,246,0.65);">Seu e-book surpresa de IA chegou</div>
      </td></tr>

      <tr><td style="padding:28px 32px 8px;font-size:16px;line-height:1.6;color:#e8e8e8;">
        Oi, <strong style="color:#ffffff;">${first}</strong>!
      </td></tr>
      <tr><td style="padding:0 32px 18px;font-size:15px;line-height:1.7;color:rgba(246,246,246,0.78);">
        Quem faz aniversário é a Scoras Academy, mas o presente é seu: o e-book surpresa é o
        <strong style="color:#fff;">Engenharia de Harness: o que é, o que não é, e por que a confusão custa caro</strong> —
        o e-book técnico sobre a disciplina que decide se um agente de IA entrega ou não. Por que comparar
        ferramentas não é engenharia, de onde vem a crítica recorrente ao termo e onde mora a variável que
        separa demo bonita de agente em produção.
      </td></tr>

      <tr><td style="padding:8px 32px 22px;text-align:center;">
        <a href="${EBOOK_URL}"
           style="display:inline-block;background:linear-gradient(135deg,#652cf2 0%,#7340ff 100%);
                  color:#fff;text-decoration:none;padding:16px 32px;border-radius:999px;
                  font-weight:600;font-size:15px;">
          Baixar o e-book (PDF)
        </a>
      </td></tr>

${blocoPromo}

      <tr><td style="padding:4px 32px 10px;font-size:13px;letter-spacing:0.14em;text-transform:uppercase;color:#33d9d5;font-weight:600;">
        Siga a gente
      </td></tr>
      <tr><td style="padding:0 32px 26px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>${redes}</tr></table>
      </td></tr>

${rodapeLegal(unsubUrl, 'Você recebeu este e-mail porque pediu o e-book surpresa de IA em <strong>aniversario.scorasacademy.com.br</strong>.')}
    </table>
  </td></tr>
</table>
</body></html>`;
}

async function addToResendAudience(env, { nome, email }) {
  if (!env.RESEND_API_KEY || !env.AUDIENCE_ID) return { skipped: true, reason: 'missing_env' };
  const { first, last } = splitName(nome);
  const r = await fetch(`https://api.resend.com/audiences/${env.AUDIENCE_ID}/contacts`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, first_name: first, last_name: last, unsubscribed: false }),
  });
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, body: j };
}

// Token de descadastro: HMAC do e-mail com a própria RESEND_API_KEY como segredo.
// Evita que qualquer um descadastre terceiros e não exige nova env var no projeto.
// ⚠️ Tem que ficar IDÊNTICA à cópia em descadastrar.js.
export async function unsubToken(email, secret) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(email.trim().toLowerCase()));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 32);
}

async function buildUnsubUrl(email, secret) {
  if (!secret) return `${SITE}/api/descadastrar?e=${encodeURIComponent(email)}`;
  const t = await unsubToken(email, secret);
  return `${SITE}/api/descadastrar?e=${encodeURIComponent(email)}&t=${t}`;
}

async function sendEbookEmail(env, { nome, email }) {
  if (!env.RESEND_API_KEY) return { skipped: true, reason: 'missing_env' };
  const unsubUrl = await buildUnsubUrl(email, env.RESEND_API_KEY);
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: FROM,
      to: [email],
      reply_to: REPLY_TO,
      subject: 'Seu e-book surpresa de IA chegou',
      html: ebookEmailHtml(nome, unsubUrl),
      headers: {
        'List-Unsubscribe': `<${unsubUrl}>`,
        'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
      },
    }),
  });
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, body: j };
}

async function backupToKv(env, payload) {
  if (!env.INSCRITOS) return { skipped: true, reason: 'missing_kv_binding' };
  const ts = new Date().toISOString();
  const key = `inscrito:${ts}:${payload.email}`;
  await env.INSCRITOS.put(key, JSON.stringify(payload));
  return { ok: true, key };
}

function notifyHtml(payload) {
  const row = (label, value) => value
    ? `<tr><td style="padding:6px 12px 6px 0;color:#888;font-size:13px;white-space:nowrap;">${label}</td><td style="padding:6px 0;color:#111;font-size:14px;">${value}</td></tr>`
    : '';
  const local = new Date(payload.timestamp).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  return `<!doctype html>
<html><body style="margin:0;padding:0;background:#f5f5f7;font-family:Inter,Helvetica,Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e5e5ea;">
      <tr><td style="background:linear-gradient(135deg,#652cf2 0%,#33d9d5 100%);padding:18px 24px;">
        <div style="font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#fff;opacity:0.85;font-weight:600;">— Novo lead</div>
        <div style="margin-top:4px;font-size:18px;font-weight:700;color:#fff;">Aniversário 2 anos · e-book surpresa</div>
      </td></tr>
      <tr><td style="padding:22px 24px 8px;">
        <div style="font-size:20px;font-weight:700;color:#111;">${esc(payload.nome)}</div>
        <div style="font-size:14px;color:#444;margin-top:2px;"><a href="mailto:${esc(payload.email)}" style="color:#652cf2;text-decoration:none;">${esc(payload.email)}</a></div>
      </td></tr>
      <tr><td style="padding:8px 24px 20px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
          ${row('WhatsApp', payload.whatsapp ? `<a href="https://wa.me/${payload.whatsapp}" style="color:#652cf2;text-decoration:none;">+${payload.whatsapp}</a>` : '')}
          ${row('Origem', payload.lead_magnet || payload.origem)}
          ${row('Quando', local + ' (BRT)')}
          ${row('UTM source', payload.utm_source)}
          ${row('UTM medium', payload.utm_medium)}
          ${row('UTM campaign', payload.utm_campaign)}
          ${row('UTM term', payload.utm_term)}
          ${row('UTM content', payload.utm_content)}
          ${row('Referrer', payload.referrer)}
          ${row('País / cidade', [payload.country, payload.city].filter(Boolean).join(' / '))}
          ${row('IP', payload.ip)}
        </table>
      </td></tr>
      <tr><td style="padding:14px 24px 22px;border-top:1px solid #eee;color:#666;font-size:12px;line-height:1.55;">
        Notificação automática · Scoras Academy. KV: <code style="background:#f0f0f3;padding:1px 6px;border-radius:4px;font-size:11px;">${payload.kv_key || 'inscrito:' + payload.timestamp + ':' + payload.email}</code>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>`;
}

async function notifyTeam(env, payload) {
  if (!env.RESEND_API_KEY) return { skipped: true, reason: 'missing_env' };
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: FROM,
      to: NOTIFY_TO,
      reply_to: payload.email,
      subject: `Novo lead · ${payload.nome} <${payload.email}> · Aniversário 2 anos`,
      html: notifyHtml(payload),
    }),
  });
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, status: r.status, body: j };
}

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return badRequest('JSON inválido');
  }

  const nome = (body.nome || '').toString().trim();
  const email = (body.email || '').toString().trim().toLowerCase();

  if (!nome || nome.length < 2) return badRequest('Nome obrigatório.');
  if (!isValidEmail(email)) return badRequest('E-mail inválido.');

  // WhatsApp é opcional no backend. O front manda '55' + DDD + número;
  // guardamos só os dígitos.
  const whatsapp = (body.whatsapp || '').toString().replace(/\D/g, '') || null;

  const cf = request.cf || {};
  const payload = {
    nome,
    email,
    whatsapp,
    lead_magnet: (body.lead_magnet || '').toString().trim() || null,
    origem: (body.origem || '').toString().trim() || null,
    referrer: body.referrer || request.headers.get('referer') || null,
    utm_source: body.utm_source || null,
    utm_medium: body.utm_medium || null,
    utm_campaign: body.utm_campaign || null,
    utm_term: body.utm_term || null,
    utm_content: body.utm_content || null,
    ip: request.headers.get('cf-connecting-ip') || null,
    country: cf.country || null,
    city: cf.city || null,
    user_agent: request.headers.get('user-agent') || null,
    timestamp: new Date().toISOString(),
  };

  const [audience, emailResult, kv, notify] = await Promise.allSettled([
    addToResendAudience(env, { nome, email }),
    sendEbookEmail(env, { nome, email }),
    backupToKv(env, payload),
    notifyTeam(env, payload),
  ]);

  return jsonResponse({
    ok: true,
    audience: audience.status === 'fulfilled' ? audience.value : { error: String(audience.reason) },
    email: emailResult.status === 'fulfilled' ? { ok: emailResult.value.ok ?? false } : { error: String(emailResult.reason) },
    kv: kv.status === 'fulfilled' ? kv.value : { error: String(kv.reason) },
    notify: notify.status === 'fulfilled' ? { ok: notify.value.ok ?? false } : { error: String(notify.reason) },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    },
  });
}

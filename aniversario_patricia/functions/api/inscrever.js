// Cloudflare Pages Function: POST /api/inscrever
// Campanha de aniversário da Patricia (29/07/2026) — landing aniversario-patricia.scorasacademy.com.br
// Recebe { nome, email, whatsapp?, lead_magnet?, origem?, utm_* , referrer? }
// Promise.allSettled em 4 paths (se um falhar, os outros continuam):
//  1) Adiciona contato na audience Resend (env.AUDIENCE_ID) — a mesma da lista do curso,
//     porque o cupom foi prometido pra lista inteira, não só pra quem veio por esta página
//  2) Dispara o e-mail de entrega dos TRÊS presentes via Resend (manual + skill + cupom).
//     Desde 29/07 o cupom sai na hora do cadastro, num único e-mail, não mais em disparo
//     manual separado no dia.
//  3) Backup completo em KV (env.INSCRITOS) sob chave inscrito:<timestamp>:<email>
//  4) Notifica o time

const FROM = 'Patricia Costa · Scoras Academy <cora@scorasacademy.com.br>';
// E-mail de entrega é no-reply: quem quiser falar com o time vai pro suporte.
const REPLY_TO = 'suporte@scorasacademy.com.br';
const SITE = 'https://aniversario-patricia.scorasacademy.com.br';
const CURSO = 'https://gargalos.scorasacademy.com.br';
const NOTIFY_TO = ['anderson@scoras.com.br', 'patricia@scoras.com.br'];

// Entrega do lead magnet: URL fixa no próprio domínio (nunca anexo — zip anexado é
// gatilho de spam, e link permite trocar o arquivo sem reenviar e-mail).
// utm_content separa os dois botões, que é o que responde "qual fatia da base usa Claude".
const UTM_ENTREGA = 'utm_source=email&utm_medium=entrega&utm_campaign=aniversario_29_07';
const EBOOK_URL = `${SITE}/downloads/automacao-com-criterio.pdf?${UTM_ENTREGA}&utm_content=manual_pdf`;
const SKILL_URL = `${SITE}/downloads/automacao-com-criterio.zip?${UTM_ENTREGA}&utm_content=skill_zip`;

// Presente 03. Até 28/07 era disparo manual no dia do aniversário; desde 29/07 o cupom
// vai junto no mesmo e-mail de entrega, na hora do cadastro.
const CUPOM = {
  codigo: 'ANIVERSARIOPATI',
  desconto: '50%',
  de: 'R$ 2.599',
  por: 'R$ 1.299,50',
  checkout: 'https://pay.hotmart.com/B105645116P?checkoutMode=6&off=pr633rv3'
    + '&offDiscount=ANIVERSARIOPATI&src=email_cupom_aniversario',
  // Fim da janela: 31/07/2026 23h59 BRT, a mesma data do countdown da landing.
  // Passou disso, o e-mail deixa de prometer desconto pra quem chegar depois.
  expiraEm: Date.parse('2026-07-31T23:59:59-03:00'),
};

const cupomAtivo = () => Date.now() <= CUPOM.expiraEm;

// "hoje é meu aniversário" só é verdade no dia 29; nos dias 30 e 31 o cupom ainda vale,
// então a abertura muda em vez de mentir a data.
const ehDiaDoAniversario = () =>
  new Date().toLocaleDateString('en-CA', { timeZone: 'America/Sao_Paulo' }) === '2026-07-29';

// Canais oficiais no rodapé do e-mail de entrega.
const REDES = [
  ['Instagram da Patricia', 'https://www.instagram.com/patricia_costa.ia/'],
  ['LinkedIn da Patricia', 'https://www.linkedin.com/in/patricia-figueiredo-costa/'],
  ['Canal no WhatsApp', 'https://whatsapp.com/channel/0029VbCTFQL90x2yWrk9zp0y'],
  ['YouTube da Scoras', 'https://www.youtube.com/@ScorasAcademy'],
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

const SANS = 'Arial,Helvetica,sans-serif';
const P = `font-family:${SANS};font-size:16px;line-height:1.6;color:#1a1a1a;`;
const RUBRICA = `font-family:${SANS};font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:#4400A5;font-weight:bold;`;

function rodapeLegal(unsubUrl, motivo) {
  return `      <tr><td style="padding:22px 40px 30px;border-top:1px solid #eeeeee;">
        <p style="font-family:${SANS};font-size:11px;line-height:1.6;color:#999999;margin:0;">
          ${motivo}
          Se não quiser mais receber conteúdos, <a href="${unsubUrl}" style="color:#4400A5;">descadastre-se aqui</a>.
          <br /><br />
          Este e-mail não recebe respostas. Para falar com o time, escreva para
          <a href="mailto:suporte@scorasacademy.com.br" style="color:#4400A5;">suporte@scorasacademy.com.br</a>.
          <br /><br />
          Scoras Academy &middot; Scoras Tecnologia Ltda &middot; CNPJ 59.526.498/0001-73 &middot; Complexo Madeira, Alphaville, Barueri/SP
        </p>
      </td></tr>`;
}

// E-mail de entrega da campanha: desde 29/07 os TRÊS presentes chegam no mesmo e-mail.
// Manual e skill por link fixo (nunca anexo), e o cupom com o desconto já aplicado no botão.
function presentesEmailHtml(nome, unsubUrl) {
  const first = esc(splitName(nome).first) || 'olá';
  const comCupom = cupomAtivo();

  // Precisa devolver <tr>, não <table>: solto dentro da tabela externa o cliente
  // de e-mail joga o botão pra fora do card e o resto do conteúdo vaza junto.
  const botao = (href, label, primario) => `
    <tr><td align="center" style="padding:2px 40px 24px;">
      <table role="presentation" cellpadding="0" cellspacing="0" align="center" style="margin:0 auto;">
        <tr><td align="center" style="background-color:${primario ? '#4400A5' : '#ffffff'};border:1px solid #4400A5;border-radius:100px;">
          <a href="${href}" target="_blank" style="display:inline-block;padding:15px 34px;font-family:${SANS};font-size:15px;font-weight:bold;color:${primario ? '#ffffff' : '#4400A5'};text-decoration:none;border-radius:100px;">${label}</a>
        </td></tr>
      </table>
    </td></tr>`;

  // Botões de rede em inline-block dentro de um td só, pra quebrarem linha
  // sozinhos no mobile em vez de estourar a largura de uma <tr> de 4 colunas.
  const redes = REDES.map(([nomeRede, href]) => `<a href="${href}" target="_blank"
             style="display:inline-block;background-color:#f7f5fc;border:1px solid #e3dcf5;color:#4400A5;
                    text-decoration:none;padding:9px 14px;border-radius:8px;font-family:${SANS};
                    font-size:12.5px;margin:0 8px 8px 0;">${nomeRede}</a>`).join('');

  // Fora da janela do cupom (depois de 31/07 23h59) o e-mail para de prometer desconto:
  // melhor um convite honesto ao curso do que um código que não passa no checkout.
  const presente03 = comCupom ? `
      <tr><td style="padding:8px 40px 4px;${RUBRICA}">Presente 03 &middot; seu cupom de aniversário</td></tr>
      <tr><td style="padding:8px 40px 0;">
        <p style="${P}margin:0 0 18px;">Quem está nesta lista tem <strong>${CUPOM.desconto} de desconto</strong> no curso <strong>De Gargalos a Agentes: Como Mapear, Priorizar e Automatizar Fluxos com IA</strong>. O manual que você acabou de baixar é a porta de entrada do método; o curso é o método completo, com a Ferramenta de Diagnóstico que pontua as 7 variáveis, compara processos e calcula o ROI de cada automação.</p>

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;">
          <tr><td style="background-color:#f7f5fc;border:1px solid #e3dcf5;border-radius:12px;padding:20px 24px;">
            <p style="font-family:${SANS};font-size:14px;line-height:1.6;color:#555555;margin:0;">Valor do curso: <span style="text-decoration:line-through;">${CUPOM.de}</span></p>
            <p style="font-family:${SANS};font-size:22px;line-height:1.4;color:#4400A5;margin:4px 0 0;"><strong>Com o cupom de aniversário: ${CUPOM.por}</strong></p>
            <p style="font-family:${SANS};font-size:13px;line-height:1.6;color:#777777;margin:10px 0 0;">Em at&eacute; 12x no cart&atilde;o, ou Pix, boleto e parcelamento sem comprometer o limite.</p>
            <p style="font-family:${SANS};font-size:13px;line-height:1.6;color:#555555;margin:12px 0 0;">Seu c&oacute;digo: <span style="font-family:'Courier New',Courier,monospace;font-size:15px;font-weight:bold;color:#4400A5;background-color:#ffffff;border:1px dashed #b9a6ec;border-radius:6px;padding:4px 10px;">${CUPOM.codigo}</span></p>
            <p style="font-family:${SANS};font-size:13px;line-height:1.6;color:#777777;margin:8px 0 0;">J&aacute; vem aplicado no bot&atilde;o abaixo. Se preferir, digite no campo de cupom do checkout.</p>
          </td></tr>
        </table>
      </td></tr>
${botao(CUPOM.checkout, `Garantir minha vaga com ${CUPOM.desconto}`, true)}
      <tr><td style="padding:0 40px 26px;">
        <p style="font-family:${SANS};font-size:13px;line-height:1.6;color:#777777;text-align:center;margin:0;">V&aacute;lido at&eacute; <strong>31/07, 23h59</strong> (hor&aacute;rio de Bras&iacute;lia). Depois disso, expira.</p>
      </td></tr>` : `
      <tr><td style="padding:8px 40px 4px;${RUBRICA}">Presente 03 &middot; a janela do cupom fechou</td></tr>
      <tr><td style="padding:8px 40px 22px;">
        <p style="${P}margin:0 0 18px;">O cupom de aniversário valeu até 31/07 e já expirou, mas o curso continua de pé: <strong>De Gargalos a Agentes</strong> é o método completo do qual o manual é a porta de entrada, com a Ferramenta de Diagnóstico que pontua as 7 variáveis, compara processos e calcula o ROI de cada automação.</p>
      </td></tr>
${botao(CURSO, 'Conhecer o curso completo', true)}`;

  return `<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Seus três presentes chegaram</title></head>
<body style="margin:0;padding:0;background-color:#f4f4f5;">
<div style="display:none;font-size:1px;color:#f4f4f5;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">
  Manual, skill e ${comCupom ? `${CUPOM.desconto} de desconto no curso De Gargalos a Agentes, válido até 31/07 às 23h59. Cupom já aplicado no link.` : 'o método completo no curso De Gargalos a Agentes.'}
</div>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5;">
<tr><td align="center" style="padding:32px 16px;">

  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;">

    <tr><td style="background-color:#4400A5;padding:22px 40px;">
      <span style="font-family:${SANS};font-size:12px;letter-spacing:2px;color:#33D9D5;text-transform:uppercase;">29 de julho &middot; anivers&aacute;rio da Patricia</span>
    </td></tr>

    <tr><td style="padding:36px 40px 8px;">
      <p style="${P}margin:0 0 18px;">Olá, <strong>${first}</strong>,</p>
      <p style="${P}margin:0 0 18px;">${
        !comCupom
          ? 'obrigada por entrar para a lista da campanha de aniversário. Seus presentes estão logo abaixo.'
          : ehDiaDoAniversario()
            ? 'hoje é meu aniversário, e como prometido, o presente é seu. Na verdade são três, e os três chegam agora, sem espera.'
            : 'a campanha do meu aniversário ainda está de pé, e como prometido, o presente é seu. São três, e os três chegam agora, sem espera.'
      }</p>
    </td></tr>

    <tr><td style="padding:8px 40px 4px;${RUBRICA}">Presente 01 &middot; o manual</td></tr>
    <tr><td style="padding:8px 40px 20px;">
      <p style="${P}margin:0;">O primeiro é o seu exemplar do <strong>Automação com Critério</strong>: o manual mínimo antes de colocar IA em qualquer processo, com as 5 decisões na ordem certa, as 7 perguntas que eu aplico em diagnósticos reais, e o checklist de uma página para a próxima reunião em que alguém disser "a gente precisa de IA".</p>
    </td></tr>
${botao(EBOOK_URL, 'Baixar o manual (PDF)', false)}

    <tr><td style="padding:8px 40px 4px;${RUBRICA}">Presente 02 &middot; a skill no seu Claude</td></tr>
    <tr><td style="padding:8px 40px 18px;">
      <p style="${P}margin:0 0 16px;">O segundo é o método instalado no seu Claude. Eu transformei o manual em uma <strong>skill</strong>: você instala uma vez e, sempre que descrever um processo da sua empresa, o Claude conduz o diagnóstico completo pelas 5 decisões e entrega um relatório executivo de uma página, com veredito e lista de tarefas.</p>

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="background-color:#f7f5fc;border:1px solid #e3dcf5;border-radius:12px;padding:18px 22px;">
          <p style="font-family:${SANS};font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#4400A5;font-weight:bold;margin:0;">Para instalar</p>
          <ol style="margin:12px 0 0;padding:0 0 0 18px;font-family:${SANS};font-size:14px;line-height:1.75;color:#333333;">
            <li>Baixe o arquivo da skill no botão abaixo.</li>
            <li>No claude.ai, abra Configurações e vá até a seção de Skills.</li>
            <li>Envie o arquivo baixado e confirme que a skill está ativada.</li>
            <li>Abra uma conversa nova e diga: "faça o diagnóstico de automação do meu processo de [exemplo]".</li>
          </ol>
          <p style="font-family:${SANS};font-size:13px;line-height:1.6;color:#777777;margin:12px 0 0;">A skill funciona nos planos pagos do Claude, com execução de código habilitada.</p>
        </td></tr>
      </table>
    </td></tr>
${botao(SKILL_URL, 'Baixar a skill (.zip)', false)}
${presente03}

    <tr><td style="padding:4px 40px 8px;">
      <p style="${P}margin:0 0 18px;">Se você já aplicou as 5 decisões do manual em algum processo da sua empresa, sabe o que elas revelam. O curso é onde isso vira instrumento: 7 módulos para mapear, priorizar e automatizar com critério, e o argumento executivo pronto para levar à sua liderança.</p>
      <p style="${P}margin:0 0 6px;font-style:italic;color:#4400A5;">Antes da IA, vem o pensamento certo.</p>
      <p style="${P}margin:14px 0 4px;"><strong>Patricia Costa</strong></p>
      <p style="font-family:${SANS};font-size:13px;line-height:1.5;color:#777777;margin:0 0 22px;">CPO da Scoras Digital &middot; Co-fundadora da Scoras Academy</p>
    </td></tr>

    <tr><td style="padding:0 40px 6px;${RUBRICA}">Siga a gente</td></tr>
    <tr><td style="padding:10px 40px 26px;">${redes}</td></tr>

${rodapeLegal(unsubUrl, `Você recebeu este e-mail porque entrou para a lista da campanha de aniversário em <strong>aniversario-patricia.scorasacademy.com.br</strong>. O curso completo está em <a href="${CURSO}" style="color:#4400A5;">gargalos.scorasacademy.com.br</a>.`)}
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
// ⚠️ A cópia em descadastrar.js tem que ficar idêntica a esta.
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

async function sendEntregaEmail(env, { nome, email }) {
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
      subject: cupomAtivo()
        ? `Seus 3 presentes: o manual, a skill e ${CUPOM.desconto} no curso`
        : 'Seus presentes: o manual e a skill do método',
      html: presentesEmailHtml(nome, unsubUrl),
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
        <div style="font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#fff;opacity:0.85;font-weight:600;">Novo cadastro na lista do dia 29</div>
        <div style="margin-top:4px;font-size:18px;font-weight:700;color:#fff;">Campanha de aniversário · Patricia</div>
      </td></tr>
      <tr><td style="padding:22px 24px 8px;">
        <div style="font-size:20px;font-weight:700;color:#111;">${esc(payload.nome)}</div>
        <div style="font-size:14px;color:#444;margin-top:2px;"><a href="mailto:${esc(payload.email)}" style="color:#652cf2;text-decoration:none;">${esc(payload.email)}</a></div>
      </td></tr>
      <tr><td style="padding:8px 24px 20px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
          ${row('WhatsApp', payload.whatsapp ? `<a href="https://wa.me/${esc(payload.whatsapp)}" style="color:#652cf2;text-decoration:none;">+${esc(payload.whatsapp)}</a>` : '')}
          ${row('Origem', esc(payload.origem || payload.lead_magnet))}
          ${row('Quando', local + ' (BRT)')}
          ${row('UTM source', esc(payload.utm_source))}
          ${row('UTM medium', esc(payload.utm_medium))}
          ${row('UTM campaign', esc(payload.utm_campaign))}
          ${row('UTM term', esc(payload.utm_term))}
          ${row('UTM content', esc(payload.utm_content))}
          ${row('Referrer', esc(payload.referrer))}
          ${row('País / cidade', esc([payload.country, payload.city].filter(Boolean).join(' / ')))}
          ${row('IP', esc(payload.ip))}
          ${row('User-agent', payload.user_agent ? `<span style="font-family:ui-monospace,monospace;font-size:12px;color:#555;">${esc(payload.user_agent)}</span>` : '')}
        </table>
      </td></tr>
      <tr><td style="padding:14px 24px 22px;border-top:1px solid #eee;color:#666;font-size:12px;line-height:1.55;">
        Notificação automática · Scoras Academy. KV: <code style="background:#f0f0f3;padding:1px 6px;border-radius:4px;font-size:11px;">inscrito:${esc(payload.timestamp)}:${esc(payload.email)}</code>
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
      subject: `Novo cadastro · ${payload.nome} <${payload.email}> · Aniversário 29/07`,
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

  const nome = (body.nome || '').toString().trim().slice(0, 120);
  const email = (body.email || '').toString().trim().toLowerCase();

  if (!nome || nome.length < 2) return badRequest('Nome obrigatório.');
  if (!isValidEmail(email)) return badRequest('E-mail inválido.');

  // O front manda '55' + DDD + 9 dígitos; guardamos só os dígitos.
  const whatsapp = (body.whatsapp || '').toString().replace(/\D/g, '').slice(0, 15) || null;

  const cf = request.cf || {};
  const url = new URL(request.url);
  const qs = (k) => {
    // A landing manda a URL cheia em `pagina`; de lá tiramos as UTMs quando o
    // front não mandou o campo separado (ads antigos, encurtadores).
    try {
      return new URL(body.pagina || url.href).searchParams.get(k) || null;
    } catch {
      return null;
    }
  };
  const payload = {
    nome,
    email,
    whatsapp,
    lead_magnet: (body.lead_magnet || '').toString().trim() || null,
    origem: (body.origem || '').toString().trim() || 'campanha_aniversario_29_07',
    pagina: (body.pagina || '').toString().trim() || null,
    referrer: body.referrer || request.headers.get('referer') || null,
    utm_source: body.utm_source || qs('utm_source'),
    utm_medium: body.utm_medium || qs('utm_medium'),
    utm_campaign: body.utm_campaign || qs('utm_campaign'),
    utm_term: body.utm_term || qs('utm_term'),
    utm_content: body.utm_content || qs('utm_content'),
    ip: request.headers.get('cf-connecting-ip') || null,
    country: cf.country || null,
    city: cf.city || null,
    user_agent: request.headers.get('user-agent') || null,
    timestamp: new Date().toISOString(),
  };

  const [audience, emailResult, kv, notify] = await Promise.allSettled([
    addToResendAudience(env, { nome, email }),
    sendEntregaEmail(env, { nome, email }),
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

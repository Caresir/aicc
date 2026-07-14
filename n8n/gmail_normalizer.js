/**
 * Gmail Trigger Normalizer — n8n Code Node
 * ────────────────────────────────────────
 * Place this Code node immediately after the Gmail Trigger node,
 * before the AI Agent node.
 *
 * Handles both Simplify ON and Simplify OFF output formats:
 *
 *   Simplify ON  — From/To are mailparser objects, body is base64 in payload
 *   Simplify OFF — headers are in payload.headers[], body is base64 in payload
 *
 * Output fields (always plain strings):
 *   from        — sender email address
 *   fromName    — sender display name
 *   to          — recipient email address
 *   subject     — email subject
 *   body        — decoded plain-text body
 *   messageId   — Gmail message ID
 *   threadId    — Gmail thread ID
 *   date        — date header string
 */

const item = $input.first().json;

// ── Email address extraction ──────────────────────────────────────────────────
// Simplify ON:  From = mailparser object { value: [{address, name}], text, html }
// Simplify OFF: From = string "Name <email>" pulled from payload.headers
function extractEmail(field) {
  if (!field) return '';

  // Plain string — "Name <email>" or bare email
  if (typeof field === 'string') {
    const match = field.match(/<([^>\s]+@[^>\s]+)>/);
    return match ? match[1].trim() : field.trim();
  }

  // Mailparser structured object: { value: [{ address, name }] }
  if (field.value && Array.isArray(field.value) && field.value[0]?.address) {
    return field.value[0].address;
  }

  // Object with .text = '"Name" <email>'
  if (typeof field.text === 'string') {
    const match = field.text.match(/<([^>\s]+@[^>\s]+)>/);
    return match ? match[1].trim() : field.text.trim();
  }

  // Direct .address key
  if (field.address) return String(field.address);

  return '';
}

function extractDisplayName(field) {
  if (!field) return '';

  if (typeof field === 'string') {
    const match = field.match(/^"?([^"<]+)"?\s*</);
    return match ? match[1].trim() : field.split('@')[0];
  }

  if (field.value && Array.isArray(field.value) && field.value[0]?.name) {
    return field.value[0].name;
  }

  if (typeof field.text === 'string') {
    const match = field.text.match(/^"?([^"<]+)"?\s*</);
    return match ? match[1].trim() : '';
  }

  return '';
}

// ── Subject extraction ────────────────────────────────────────────────────────
// Simplify ON:  $json.Subject (capital S, plain string)
// Simplify OFF: buried in payload.headers array
function extractSubject(item) {
  if (item.Subject) return String(item.Subject);
  if (item.subject) return String(item.subject);

  const headers = item.payload?.headers;
  if (Array.isArray(headers)) {
    const h = headers.find(h => h.name?.toLowerCase() === 'subject');
    if (h?.value) return h.value;
  }

  return '(no subject)';
}

// ── Body extraction ───────────────────────────────────────────────────────────
// Gmail always base64url-encodes body data.
// Simplify ON:  payload.body.data (simple) or payload.parts[].body.data (multipart)
// Simplify OFF: same structure under payload
function decodeBase64url(data) {
  if (!data) return '';
  // base64url uses - and _ instead of + and /
  const standard = data.replace(/-/g, '+').replace(/_/g, '/');
  return Buffer.from(standard, 'base64').toString('utf-8');
}

function searchParts(parts) {
  if (!Array.isArray(parts)) return '';

  // Prefer text/plain
  for (const part of parts) {
    if (part.mimeType === 'text/plain' && part.body?.data) {
      return decodeBase64url(part.body.data);
    }
  }

  // Recurse into nested multipart (e.g. multipart/alternative inside multipart/mixed)
  for (const part of parts) {
    if (Array.isArray(part.parts)) {
      const found = searchParts(part.parts);
      if (found) return found;
    }
  }

  // Last resort: strip HTML from text/html part
  for (const part of parts) {
    if (part.mimeType === 'text/html' && part.body?.data) {
      return decodeBase64url(part.body.data)
        .replace(/<style[\s\S]*?<\/style>/gi, '')
        .replace(/<[^>]+>/g, ' ')
        .replace(/&nbsp;/g, ' ')
        .replace(/\s{2,}/g, ' ')
        .trim();
    }
  }

  return '';
}

function extractBody(item) {
  const payload = item.payload;
  if (!payload) return '';

  // Non-multipart: body data is directly on payload.body
  if (payload.body?.data) {
    return decodeBase64url(payload.body.data);
  }

  // Multipart: walk parts tree
  if (Array.isArray(payload.parts)) {
    return searchParts(payload.parts);
  }

  return '';
}

// ── Fallback header lookup (Simplify OFF) ─────────────────────────────────────
function headerValue(item, name) {
  const headers = item.payload?.headers;
  if (!Array.isArray(headers)) return '';
  const h = headers.find(h => h.name?.toLowerCase() === name.toLowerCase());
  return h?.value || '';
}

// ── Build normalized output ───────────────────────────────────────────────────
const fromRaw  = item.From  || item.from  || headerValue(item, 'from');
const toRaw    = item.To    || item.to    || headerValue(item, 'to');

const from     = extractEmail(fromRaw);
const fromName = extractDisplayName(fromRaw) || from.split('@')[0];
const to       = extractEmail(toRaw);
const subject  = extractSubject(item);
const body     = extractBody(item);
const date     = item.Date || item.date || headerValue(item, 'date') || '';
const messageId = item.id || item.messageId || item.message_id || '';
const threadId  = item.threadId || item.thread_id || '';

return {
  json: {
    from,
    fromName,
    to,
    subject,
    body,
    date,
    messageId,
    threadId,
  }
};

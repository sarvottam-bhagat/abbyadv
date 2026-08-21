import { supabase } from './supabase';

export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const session = (await supabase?.auth.getSession())?.data.session;
  if (session?.access_token) headers.set('Authorization', `Bearer ${session.access_token}`);
  else if (import.meta.env.DEV) headers.set('X-User-Id', 'local-dev-user');
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || body.message || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const jsonBody = (value: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(value) });

export async function downloadFile(path: string): Promise<{ blob: Blob; filename: string }> {
  const headers = new Headers(); const session = (await supabase?.auth.getSession())?.data.session;
  if (session?.access_token) headers.set('Authorization', `Bearer ${session.access_token}`);
  else if (import.meta.env.DEV) headers.set('X-User-Id', 'local-dev-user');
  const response = await fetch(`${API_URL}${path}`, { headers });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || `Download failed (${response.status})`); }
  const disposition = response.headers.get('content-disposition') || ''; const filename = disposition.match(/filename="?([^";]+)"?/i)?.[1] || 'abbyadv-draft';
  return { blob: await response.blob(), filename };
}

export async function streamJson(path: string, value: unknown, onEvent: (event: string, data: Record<string, string>) => void): Promise<void> {
  const headers = new Headers({ 'Content-Type': 'application/json', Accept: 'text/event-stream' });
  const session = (await supabase?.auth.getSession())?.data.session;
  if (session?.access_token) headers.set('Authorization', `Bearer ${session.access_token}`);
  else if (import.meta.env.DEV) headers.set('X-User-Id', 'local-dev-user');
  const response = await fetch(`${API_URL}${path}`, { method: 'POST', headers, body: JSON.stringify(value) });
  if (!response.ok || !response.body) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || `Request failed (${response.status})`); }
  const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = '';
  while (true) {
    const { done, value: chunk } = await reader.read(); if (done) break;
    buffer += decoder.decode(chunk, { stream: true }); const events = buffer.split('\n\n'); buffer = events.pop() || '';
    for (const block of events) { const event = block.match(/^event: (.+)$/m)?.[1] || 'message'; const raw = block.match(/^data: (.+)$/m)?.[1]; if (raw) onEvent(event, JSON.parse(raw)); }
  }
}

import { getBrowserSupabaseClient } from '@/lib/supabase/client';

async function accessToken(): Promise<string> {
  const { data } = await getBrowserSupabaseClient().auth.getSession();
  const token = data.session?.access_token;
  if (!token) throw new Error('Tu sesión expiró. Vuelve a iniciar sesión.');
  return token;
}

export async function callApi(path: string, body: object) {
  const token = await accessToken();
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  const json = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(json.error || `Error ${response.status}`);
  return json;
}

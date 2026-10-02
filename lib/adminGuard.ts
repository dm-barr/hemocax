import { NextResponse } from 'next/server';
import { SupabaseClient, User } from '@supabase/supabase-js';
import { bearerToken, createServiceRoleClient, createUserScopedClient } from '@/lib/supabase/server';

type Guard = { caller: SupabaseClient; service: SupabaseClient; user: User } | { error: NextResponse };

/** Comprueba que quien llama sea administrador. Devuelve su cliente (con RLS), el de servicio y su usuario. */
export async function requireAdmin(request: Request): Promise<Guard> {
  let token: string;
  try {
    token = bearerToken(request);
  } catch (e) {
    return { error: NextResponse.json({ error: e instanceof Error ? e.message : 'No autorizado' }, { status: 401 }) };
  }
  const caller = createUserScopedClient(token);
  const { data } = await caller.auth.getUser();
  if (!data.user) return { error: NextResponse.json({ error: 'Sesión inválida.' }, { status: 401 }) };
  const { data: role } = await caller.rpc('current_role');
  if (role !== 'ADMIN') return { error: NextResponse.json({ error: 'Se requiere rol administrador.' }, { status: 403 }) };
  return { caller, service: createServiceRoleClient(), user: data.user };
}

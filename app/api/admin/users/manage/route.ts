import { NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/adminGuard';

const CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789';
const generatePassword = () => Array.from(crypto.getRandomValues(new Uint32Array(14)), (n) => CHARS[n % CHARS.length]).join('');

export async function POST(request: Request) {
  const guard = await requireAdmin(request);
  if ('error' in guard) return guard.error;
  const { service, user } = guard;

  const body = await request.json().catch(() => ({}));
  const userId = String(body.user_id || '');
  const action = String(body.action || '');
  if (!userId) return NextResponse.json({ error: 'Falta la cuenta.' }, { status: 400 });

  const { data: target } = await service.from('profiles').select('user_id,dni,role,active').eq('user_id', userId).single();
  if (!target) return NextResponse.json({ error: 'Cuenta no encontrada.' }, { status: 404 });

  const log = (name: string, detail: object) => service.from('audit_logs').insert({
    actor_id: user.id, actor_dni: user.user_metadata?.dni ?? null, action: name, entity: 'profile', detail: { dni: target.dni, ...detail },
  });

  if (action === 'reset_password') {
    const password = generatePassword();
    const { error } = await service.auth.admin.updateUserById(userId, { password });
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    await log('USER_PASSWORD_RESET', {});
    return NextResponse.json({ password });
  }

  if (action === 'set_active') {
    const active = body.active === true;
    if (!active) {
      if (userId === user.id) return NextResponse.json({ error: 'No puedes desactivar tu propia cuenta.' }, { status: 400 });
      if (target.role === 'ADMIN') {
        const { count } = await service.from('profiles').select('user_id', { count: 'exact', head: true }).eq('role', 'ADMIN').eq('active', true);
        if ((count ?? 0) <= 1) return NextResponse.json({ error: 'Debe quedar al menos un administrador activo.' }, { status: 400 });
      }
    }
    const { error } = await service.auth.admin.updateUserById(userId, { ban_duration: active ? 'none' : '876000h' });
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    await service.from('profiles').update({ active }).eq('user_id', userId);
    await log(active ? 'USER_ACTIVATED' : 'USER_DEACTIVATED', {});
    return NextResponse.json({ ok: true });
  }

  if (action === 'set_release') {
    if (target.role === 'DONOR') return NextResponse.json({ error: 'Una cuenta de donante no puede liberar resultados.' }, { status: 400 });
    const value = body.value === true;
    await service.from('profiles').update({ can_release_results: value }).eq('user_id', userId);
    await log('USER_PERMISSION_CHANGED', { can_release_results: value });
    return NextResponse.json({ ok: true });
  }

  return NextResponse.json({ error: 'Acción no válida.' }, { status: 400 });
}

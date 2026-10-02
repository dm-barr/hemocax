import { NextResponse } from 'next/server';
import { bearerToken, createServiceRoleClient, createUserScopedClient } from '@/lib/supabase/server';

export async function POST(request: Request) {
  let token: string;
  try {
    token = bearerToken(request);
  } catch (e) {
    return NextResponse.json({ error: e instanceof Error ? e.message : 'No autorizado' }, { status: 401 });
  }

  const caller = createUserScopedClient(token);
  const { data: callerUser } = await caller.auth.getUser();
  if (!callerUser.user) return NextResponse.json({ error: 'Sesión inválida.' }, { status: 401 });
  const { data: callerRole } = await caller.rpc('current_role');
  if (callerRole !== 'ADMIN') return NextResponse.json({ error: 'Se requiere rol administrador.' }, { status: 403 });

  const body = await request.json().catch(() => ({}));
  const dni = String(body.dni || '').trim();
  const fullName = String(body.full_name || '').trim();
  const role = String(body.role || '');
  const password = String(body.password || '');
  const canReleaseResults = body.can_release_results === true && role !== 'DONOR';
  const donorId = body.donor_id ? Number(body.donor_id) : null;

  if (!/^\d{8}$/.test(dni)) return NextResponse.json({ error: 'El DNI debe contener ocho dígitos.' }, { status: 400 });
  if (!fullName) return NextResponse.json({ error: 'El nombre completo es obligatorio.' }, { status: 400 });
  if (!['ADMIN', 'STAFF', 'DONOR'].includes(role)) return NextResponse.json({ error: 'Rol no permitido.' }, { status: 400 });
  if (password.length < 12) return NextResponse.json({ error: 'La contraseña debe tener al menos 12 caracteres.' }, { status: 400 });
  if (role === 'DONOR' && !donorId) return NextResponse.json({ error: 'Indica el donante a vincular con esta cuenta.' }, { status: 400 });

  const service = createServiceRoleClient();
  const email = `dni-${dni}@login.hemocax.org`;

  const { data: created, error: createError } = await service.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
    user_metadata: { dni, full_name: fullName },
  });
  if (createError || !created.user) {
    const status = createError?.status === 422 || /already registered/i.test(createError?.message || '') ? 409 : 500;
    return NextResponse.json({ error: createError?.message || 'No se pudo crear la cuenta.' }, { status });
  }
  const userId = created.user.id;

  const { error: profileError } = await service.from('profiles').insert({
    user_id: userId,
    dni,
    full_name: fullName,
    role,
    can_release_results: canReleaseResults,
    active: true,
  });
  if (profileError) {
    await service.auth.admin.deleteUser(userId);
    return NextResponse.json({ error: profileError.message }, { status: 409 });
  }

  if (role === 'DONOR') {
    const { data: linked, error: linkError } = await service
      .from('donors')
      .update({ auth_user_id: userId })
      .eq('id', donorId)
      .is('auth_user_id', null)
      .select('id')
      .single();
    if (linkError || !linked) {
      await service.from('profiles').delete().eq('user_id', userId);
      await service.auth.admin.deleteUser(userId);
      return NextResponse.json({ error: 'El donante no existe o ya tiene una cuenta vinculada.' }, { status: 409 });
    }
  }

  await service.from('audit_logs').insert({
    actor_id: callerUser.user.id,
    actor_dni: callerUser.user.user_metadata?.dni || null,
    action: 'USER_CREATED',
    entity: 'profile',
    entity_id: null,
    detail: { dni, role, can_release_results: canReleaseResults, donor_id: donorId },
  });

  return NextResponse.json({ user_id: userId, dni, full_name: fullName, role, can_release_results: canReleaseResults }, { status: 201 });
}

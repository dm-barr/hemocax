import { NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/adminGuard';

export async function POST(request: Request) {
  const guard = await requireAdmin(request);
  if ('error' in guard) return guard.error;
  const { caller, service } = guard;

  const body = await request.json().catch(() => ({}));
  const donorId = Number(body.donor_id);
  if (!donorId) return NextResponse.json({ error: 'Falta el donante.' }, { status: 400 });

  const { data: donor } = await service.from('donors').select('id,auth_user_id').eq('id', donorId).single();
  if (!donor) return NextResponse.json({ error: 'Donante no encontrado.' }, { status: 404 });

  const { error } = await caller.rpc('anonymize_donor', { p_donor_id: donorId });
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  if (donor.auth_user_id) await service.auth.admin.deleteUser(donor.auth_user_id);
  return NextResponse.json({ ok: true });
}

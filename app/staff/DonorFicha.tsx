'use client';

import { useEffect, useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { Params } from '@/lib/params';
import { Eligibility, formatDate, limaToday } from '@/lib/eligibility';
import { ConsentModal, DataModal, DonationModal, DonorForm } from './DonorModals';
import { DonationRow } from './useDirectory';
import { Badge, Donor, Modal, Notify, RESULT_LABEL, fullName, isAuthorized } from './ui';

type DonationWithResult = DonationRow & { notes: string | null; result: { status: string; critical: boolean } | null };

const ageOf = (birth: string) => {
  const today = limaToday();
  let age = Number(today.slice(0, 4)) - Number(birth.slice(0, 4));
  if (today.slice(5) < birth.slice(5)) age -= 1;
  return age;
};

export default function DonorFicha({ donor, donations, params, eligibility, isAdmin, notify, onClose, onChanged }: {
  donor: Donor; donations: DonationRow[]; params: Params; eligibility: Eligibility; isAdmin: boolean; notify: Notify; onClose: () => void; onChanged: () => void;
}) {
  const [sub, setSub] = useState<null | 'donate' | 'consent' | 'edit' | 'data'>(null);
  const [history, setHistory] = useState<DonationWithResult[]>([]);
  const mine = donations.filter((d) => d.donor_id === donor.id);

  useEffect(() => {
    (async () => {
      const { data } = await getBrowserSupabaseClient()
        .from('donations')
        .select('id,donor_id,donation_date,notes,donation_results(status,critical)')
        .eq('donor_id', donor.id)
        .order('donation_date', { ascending: false });
      setHistory((data || []).map((d) => {
        const r = (d as { donation_results: unknown }).donation_results;
        const result = (Array.isArray(r) ? r[0] : r) as { status: string; critical: boolean } | null | undefined;
        return { ...(d as unknown as DonationRow), notes: (d as { notes: string | null }).notes, result: result ?? null };
      }));
    })();
  }, [donor.id, mine.length]);

  const authorized = isAuthorized(donor);
  const done = () => { setSub(null); onChanged(); };

  return (
    <>
      <Modal title="Ficha del donante" wide onClose={onClose}>
        <div className="ficha-head">
          <div>
            <h3>{fullName(donor)}</h3>
            <p>DNI {donor.dni} · {ageOf(donor.birth_date)} años · {donor.gender === 'F' ? 'Mujer' : 'Hombre'}</p>
            <p className="muted">{donor.phone} · {donor.email || 'sin correo registrado'}</p>
          </div>
          <div className="blood-big">{donor.blood_type ? `${donor.blood_type}${donor.rh_factor}` : <small>Sin dato</small>}<span>GRUPO</span></div>
        </div>

        <div className="ficha-cards">
          <div className={`ficha-card ${eligibility.state === 'APTO' ? 'ok' : eligibility.state === 'INACTIVO' ? '' : 'warn'}`}>
            <span>¿Puede donar hoy?</span>
            <b>{eligibility.state === 'APTO' ? 'Sí, está apto' : eligibility.state === 'ESPERA' ? 'Todavía no' : eligibility.state === 'MAXIMO' ? 'Llegó al máximo anual' : 'Donante inactivo'}</b>
            <small>
              {eligibility.state === 'APTO' && (eligibility.lastDate ? `Cumplió el intervalo de ${eligibility.intervalDays} días.` : 'Aún no tiene donaciones registradas.')}
              {eligibility.state === 'ESPERA' && `Podrá donar desde el ${formatDate(eligibility.eligibleFrom!)}.`}
              {eligibility.state === 'MAXIMO' && `Podrá donar desde el ${formatDate(eligibility.eligibleFrom!)}.`}
              {eligibility.state === 'INACTIVO' && 'Actívalo en «Editar datos» para volver a registrarle donaciones.'}
            </small>
          </div>
          <div className={`ficha-card ${donor.opted_out ? 'warn' : authorized ? 'ok' : ''}`}>
            <span>Correos del Banco de Sangre</span>
            <b>{donor.opted_out ? 'Pidió no recibirlos' : authorized ? 'Autorizados' : 'Sin autorizar'}</b>
            <small>{authorized ? 'Recibirá avisos y recordatorios.' : 'Pídele su aceptación para poder escribirle.'}</small>
          </div>
          <div className="ficha-card">
            <span>Donaciones este año</span>
            <b>{eligibility.thisYear} de {eligibility.limit}</b>
            <small>Última: {eligibility.lastDate ? formatDate(eligibility.lastDate) : 'ninguna'}</small>
          </div>
        </div>

        <div className="ficha-actions">
          <button className="primary big" onClick={() => setSub('donate')}>Registrar donación</button>
          <button className="secondary" onClick={() => setSub('consent')}>{authorized ? 'Correos y consentimiento' : 'Registrar su autorización de correos'}</button>
          <button className="secondary" onClick={() => setSub('edit')}>Editar datos</button>
          <button className="secondary" onClick={() => setSub('data')}>Datos y privacidad</button>
        </div>

        <h4 className="ficha-title">Historial de donaciones</h4>
        {history.length === 0 ? <p className="muted">Todavía no tiene donaciones registradas.</p> : (
          <ul className="ficha-history">
            {history.map((h) => {
              const label = h.result ? (h.result.critical ? RESULT_LABEL.CRITICAL_PENDING : RESULT_LABEL[h.result.status]) : null;
              return (
                <li key={h.id}>
                  <span>{formatDate(h.donation_date)}</span>
                  {label ? <Badge tone={label.tone}>Resultado: {label.text.toLowerCase()}</Badge> : <Badge>Sin resultado</Badge>}
                </li>
              );
            })}
          </ul>
        )}
        <div className="modal-actions"><button className="secondary" onClick={onClose}>Cerrar</button></div>
      </Modal>

      {sub === 'donate' && <DonationModal donor={donor} donations={donations} params={params} notify={notify} onClose={() => setSub(null)} onSaved={done} />}
      {sub === 'consent' && <ConsentModal donor={donor} notify={notify} onClose={() => setSub(null)} onSaved={done} />}
      {sub === 'edit' && <DonorForm donor={donor} notify={notify} onClose={() => setSub(null)} onSaved={done} />}
      {sub === 'data' && <DataModal donor={donor} isAdmin={isAdmin} notify={notify} onClose={() => setSub(null)} onChanged={done} />}
    </>
  );
}

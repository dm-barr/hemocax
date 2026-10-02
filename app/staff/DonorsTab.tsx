'use client';

import { useState } from 'react';
import { formatDate } from '@/lib/eligibility';
import { BLOOD_GROUPS, DonationModal, DonorForm } from './DonorModals';
import DonorFicha from './DonorFicha';
import ImportDonors from './ImportDonors';
import { normalizeText, useDirectory } from './useDirectory';
import { Badge, Donor, Empty, Notify, PageHeader, fullName, isAuthorized } from './ui';

type Filter = 'all' | 'apto' | 'authorized' | 'unauthorized';

export default function DonorsTab({ notify, intent, isAdmin }: { notify: Notify; intent?: string; isAdmin: boolean }) {
  const { donors, donations, params, eligibility, loading, reload } = useDirectory(notify);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<Filter>('all');
  const [group, setGroup] = useState('');
  const [creating, setCreating] = useState(intent === 'new' || (intent?.startsWith('new:') ?? false));
  const [newDni] = useState(intent?.startsWith('new:') ? intent.slice(4) : '');
  const [fichaId, setFichaId] = useState<number | null>(null);
  const [donating, setDonating] = useState<Donor | null>(null);
  const [importing, setImporting] = useState(false);

  const q = normalizeText(query.trim());
  const filtered = donors.filter((d) => {
    if (q && !normalizeText(`${fullName(d)} ${d.dni} ${d.email ?? ''}`).includes(q)) return false;
    if (group && `${d.blood_type ?? ''}${d.rh_factor ?? ''}` !== group) return false;
    if (filter === 'apto') return eligibility.get(d.id)?.state === 'APTO';
    if (filter === 'authorized') return isAuthorized(d);
    if (filter === 'unauthorized') return !isAuthorized(d);
    return true;
  });
  const ficha = fichaId !== null ? donors.find((d) => d.id === fichaId) : undefined;

  return (
    <>
      <PageHeader
        title="Donantes"
        help="Todas las personas registradas como donantes. Busca a alguien, ábrele su ficha para ver si puede donar y registrar su donación, o registra a una persona nueva."
        action={(
          <div className="head-actions">
            <button className="secondary" onClick={() => setImporting(true)}>Importar desde Excel</button>
            <button className="primary" onClick={() => setCreating(true)}>+ Registrar donante</button>
          </div>
        )}
      />

      <div className="toolbar">
        <input className="search" placeholder="Buscar por nombre, DNI o correo" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Buscar donante" />
        <select className="select-inline" value={group} onChange={(e) => setGroup(e.target.value)} aria-label="Filtrar por grupo sanguíneo">
          <option value="">Todos los grupos</option>
          {BLOOD_GROUPS.map((g) => <option key={g}>{g}</option>)}
        </select>
        <div className="chips" role="group" aria-label="Filtrar">
          {([['all', 'Todos'], ['apto', 'Pueden donar hoy'], ['authorized', 'Con correo autorizado'], ['unauthorized', 'Sin autorizar']] as [Filter, string][]).map(([key, label]) => (
            <button key={key} className={filter === key ? 'chip active' : 'chip'} onClick={() => setFilter(key)}>{label}</button>
          ))}
        </div>
      </div>

      {loading ? <p className="muted">Cargando donantes…</p> : filtered.length === 0 ? (
        <div className="card">
          <Empty
            title={donors.length === 0 ? 'Todavía no hay donantes registrados' : 'No encontramos donantes con ese filtro'}
            hint={donors.length === 0 ? 'Registra al primero, o importa el padrón que ya tienen desde un archivo de Excel.' : 'Prueba con otro nombre o cambia el filtro.'}
            action={donors.length === 0 ? <button className="primary" onClick={() => setCreating(true)}>Registrar el primer donante</button> : undefined}
          />
        </div>
      ) : (
        <div className="card table-card">
          <div className="table-wrap">
            <table className="table clickable">
              <thead><tr><th>Donante</th><th>Sangre</th><th>¿Puede donar?</th><th>Correos</th><th>Acciones</th></tr></thead>
              <tbody>
                {filtered.map((d) => {
                  const e = eligibility.get(d.id)!;
                  return (
                    <tr key={d.id} onClick={() => setFichaId(d.id)}>
                      <td><b>{fullName(d)}</b><br /><small>DNI {d.dni}</small></td>
                      <td>{d.blood_type ? <span className="blood-type">{d.blood_type}{d.rh_factor}</span> : <span className="muted">Sin dato</span>}</td>
                      <td>
                        {e.state === 'APTO' && <Badge tone="ok">Puede donar</Badge>}
                        {e.state === 'ESPERA' && <Badge tone="warn">Desde {formatDate(e.eligibleFrom!)}</Badge>}
                        {e.state === 'MAXIMO' && <Badge tone="warn">Máximo anual</Badge>}
                        {e.state === 'INACTIVO' && <Badge>Inactivo</Badge>}
                      </td>
                      <td>{d.opted_out ? <Badge tone="warn">No quiere correos</Badge> : d.consent_email ? <Badge tone="ok">Autorizado</Badge> : <Badge>Sin autorizar</Badge>}</td>
                      <td className="actions" onClick={(ev) => ev.stopPropagation()}>
                        <button className="primary small" onClick={() => setDonating(d)}>Registrar donación</button>
                        <button className="secondary small" onClick={() => setFichaId(d.id)}>Ver ficha</button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {creating && <DonorForm donor={null} initialDni={newDni} notify={notify} onClose={() => setCreating(false)} onSaved={(id) => { setCreating(false); reload(); if (id) setFichaId(id); }} />}
      {donating && <DonationModal donor={donating} donations={donations} params={params} notify={notify} onClose={() => setDonating(null)} onSaved={() => { setDonating(null); reload(); }} />}
      {ficha && <DonorFicha donor={ficha} donations={donations} params={params} eligibility={eligibility.get(ficha.id)!} isAdmin={isAdmin} notify={notify} onClose={() => setFichaId(null)} onChanged={reload} />}
      {importing && <ImportDonors notify={notify} onClose={() => setImporting(false)} onDone={() => { setImporting(false); reload(); }} />}
    </>
  );
}

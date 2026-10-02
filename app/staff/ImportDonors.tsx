'use client';

import { useState } from 'react';
import { getBrowserSupabaseClient } from '@/lib/supabase/client';
import { mapDonorRows, parseCsv } from '@/lib/csv';
import { Modal, Notify, downloadFile, friendlyError } from './ui';

const TEMPLATE = 'dni,nombres,apellidos,sexo,fecha_nacimiento,telefono,correo,grupo_sanguineo\r\n12345678,Ana María,Quispe Rojas,F,15/03/1990,987654321,ana@ejemplo.com,O+\r\n';

export default function ImportDonors({ notify, onClose, onDone }: { notify: Notify; onClose: () => void; onDone: () => void }) {
  const [text, setText] = useState('');
  const [progress, setProgress] = useState<{ done: number; total: number } | null>(null);
  const [failed, setFailed] = useState<{ line: number; message: string }[]>([]);

  const parsed = text.trim() ? mapDonorRows(parseCsv(text)) : null;

  async function readFile(file: File | undefined) {
    if (file) setText(await file.text());
  }

  async function run() {
    if (!parsed) return;
    const supabase = getBrowserSupabaseClient();
    const problems: { line: number; message: string }[] = [];
    let ok = 0;
    setProgress({ done: 0, total: parsed.valid.length });
    for (const item of parsed.valid) {
      const { error } = await supabase.from('donors').insert(item.row);
      if (error) problems.push({ line: item.line, message: friendlyError(error.message) });
      else ok += 1;
      setProgress({ done: ok + problems.length, total: parsed.valid.length });
    }
    setFailed(problems);
    notify(`Se importaron ${ok} donante(s).${problems.length ? ` ${problems.length} no se pudieron importar.` : ''}`, problems.length ? 'error' : 'ok');
    if (!problems.length) { onDone(); return; }
    setProgress(null);
  }

  return (
    <Modal title="Importar donantes desde Excel/CSV" onClose={progress ? () => undefined : onClose}>
      <p className="muted">
        Sube un archivo CSV (en Excel: Guardar como → CSV) con una fila por donante. Las columnas obligatorias son
        <b> dni, nombres, apellidos, sexo, fecha_nacimiento, telefono</b>; opcionales: <b>correo, grupo_sanguineo</b>.
        Importar no autoriza correos: el consentimiento se registra aparte.
      </p>
      <div className="modal-actions" style={{ justifyContent: 'flex-start', marginTop: 8 }}>
        <button className="secondary small" onClick={() => downloadFile('plantilla_donantes.csv', '﻿' + TEMPLATE, 'text/csv;charset=utf-8')}>Descargar plantilla</button>
        <input type="file" accept=".csv,text/csv" onChange={(e) => readFile(e.target.files?.[0])} aria-label="Elegir archivo CSV" />
      </div>
      <textarea className="import-box" rows={6} placeholder="…o pega aquí el contenido del CSV" value={text} onChange={(e) => setText(e.target.value)} />

      {parsed && (
        <p className={parsed.errors.length ? 'notice-box warn' : 'notice-box ok'}>
          {parsed.valid.length} fila(s) listas para importar{parsed.errors.length ? ` · ${parsed.errors.length} con problemas (se omitirán)` : ''}.
        </p>
      )}
      {parsed && parsed.errors.length > 0 && (
        <ul className="problems">{parsed.errors.slice(0, 8).map((e) => <li key={e.line}>Fila {e.line}: {e.message}</li>)}{parsed.errors.length > 8 && <li>…y {parsed.errors.length - 8} más.</li>}</ul>
      )}
      {failed.length > 0 && (
        <ul className="problems">{failed.slice(0, 8).map((e) => <li key={e.line}>Fila {e.line}: {e.message}</li>)}</ul>
      )}
      {progress && <p className="muted">Importando… {progress.done} de {progress.total}</p>}

      <div className="modal-actions">
        <button className="secondary" onClick={onClose} disabled={!!progress}>Cerrar</button>
        <button className="primary" disabled={!!progress || !parsed || parsed.valid.length === 0} onClick={run}>
          {progress ? 'Importando…' : `Importar ${parsed?.valid.length ?? 0} donante(s)`}
        </button>
      </div>
    </Modal>
  );
}

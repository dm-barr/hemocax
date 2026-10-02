import { SupabaseClient } from '@supabase/supabase-js';

export type Params = {
  limits: { M: number; F: number };
  intervals: { M: number; F: number };
  recommendations: string;
};

export const DEFAULT_RECOMMENDATIONS =
  'Después de donar: hidrátate bien, evita esfuerzos físicos intensos durante 24 horas y mantén una alimentación equilibrada. Si presentas algún malestar, comunícate con el Banco de Sangre.';

/** Lee los parámetros del sistema. Funciona con la sesión del personal, del donante o con la clave de servicio. */
export async function loadParams(supabase: SupabaseClient): Promise<Params> {
  const { data } = await supabase.from('system_config').select('key,value');
  const map: Record<string, unknown> = Object.fromEntries((data || []).map((r) => [r.key, r.value]));
  const num = (key: string, fallback: number) => {
    const n = Number(map[key]);
    return Number.isFinite(n) && n > 0 ? n : fallback;
  };
  const base = num('donation_interval_days', 90);
  return {
    limits: { M: num('male_annual_limit', 4), F: num('female_annual_limit', 3) },
    intervals: { M: num('male_interval_days', base), F: num('female_interval_days', base) },
    recommendations: typeof map.result_recommendations === 'string' ? map.result_recommendations : DEFAULT_RECOMMENDATIONS,
  };
}

import { ReactNode } from 'react';

export type IconName = 'drop' | 'check' | 'clock' | 'calendar' | 'pin' | 'bell' | 'heart' | 'result' | 'sliders' | 'alert';

const PATHS: Record<IconName, ReactNode> = {
  drop: <path d="M12 3c3.6 4.3 6 7.2 6 10.2a6 6 0 1 1-12 0C6 10.2 8.4 7.3 12 3z" />,
  check: <><circle cx="12" cy="12" r="9" /><path d="m8.2 12.4 2.6 2.6 5-5.4" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7.4V12l3.2 2" /></>,
  calendar: <><rect x="4" y="5.5" width="16" height="14.5" rx="3" /><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4" /></>,
  pin: <><path d="M12 21s6.2-5.3 6.2-10.2a6.2 6.2 0 1 0-12.4 0C5.8 15.7 12 21 12 21z" /><circle cx="12" cy="10.8" r="2.2" /></>,
  bell: <><path d="M6 16.5V11a6 6 0 1 1 12 0v5.5l1.6 2H4.4L6 16.5z" /><path d="M10 21a2 2 0 0 0 4 0" /></>,
  heart: <path d="M12 20.2s-7.2-4.6-7.2-10.1A4.1 4.1 0 0 1 12 7.6a4.1 4.1 0 0 1 7.2 2.5c0 5.5-7.2 10.1-7.2 10.1z" />,
  result: <><path d="M7 3.5h7.5L19 8v12.5H7V3.5z" /><path d="M14.5 3.5V8H19M10.2 14.2l1.9 1.9 3.5-3.9" /></>,
  sliders: <><path d="M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1" /><circle cx="15" cy="7" r="2" /><circle cx="9" cy="12" r="2" /><circle cx="17" cy="17" r="2" /></>,
  alert: <><path d="M12 4 3.5 19h17L12 4z" /><path d="M12 10v4M12 16.8v.2" /></>,
};

export function Icon({ name, size = 24 }: { name: IconName; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {PATHS[name]}
    </svg>
  );
}

/** Gota de sangre con el grupo sanguíneo adentro. */
export function DropBadge({ label }: { label: string }) {
  return (
    <div className="dp-drop" role="img" aria-label={`Tu grupo de sangre: ${label}`}>
      <svg viewBox="0 0 100 120" aria-hidden="true">
        <defs>
          <linearGradient id="dropGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#e5667c" />
            <stop offset="1" stopColor="#c93f58" />
          </linearGradient>
        </defs>
        <path d="M50 6C70 32 90 54 90 77a40 40 0 0 1-80 0C10 54 30 32 50 6z" fill="url(#dropGrad)" />
        <path d="M30 78a20 20 0 0 0 14 19" stroke="#ffffff66" strokeWidth="5" strokeLinecap="round" fill="none" />
      </svg>
      <b>{label}</b>
    </div>
  );
}

import type { Metadata, Viewport } from 'next';
import { DM_Sans, Manrope } from 'next/font/google';
import './portal.css';

// Las tipografías se descargan al compilar y se sirven desde el mismo sitio: sin pedidos externos que frenen la carga.
const body = DM_Sans({ subsets: ['latin'], weight: ['400', '500', '600', '700'], display: 'swap', variable: '--nf-body' });
const head = Manrope({ subsets: ['latin'], weight: ['600', '700', '800'], display: 'swap', variable: '--nf-head' });

export const metadata: Metadata = {
  title: 'HEMOCAX | Banco de Sangre',
  description: 'Portal seguro de donantes y gestión del Banco de Sangre.',
};

export const viewport: Viewport = { width: 'device-width', initialScale: 1 };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es" className={`${body.variable} ${head.variable}`}><body>{children}</body></html>;
}

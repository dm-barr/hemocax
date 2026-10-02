import type { Metadata } from 'next';
import './portal.css';

export const metadata: Metadata = {
  title: 'HEMOCAX | Banco de Sangre',
  description: 'Portal seguro de donantes y gestión del Banco de Sangre.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es"><body>{children}</body></html>;
}

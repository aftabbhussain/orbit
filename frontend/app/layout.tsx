import type { Metadata } from 'next';
//import './globals.css';

export const metadata: Metadata = {
  title: 'Orbit Research',
  description: 'AI-powered research assistant for arXiv papers',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}

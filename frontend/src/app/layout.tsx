import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Ivy Homes Voice Assistant',
  description: 'AI-powered voice assistant for property inquiries',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

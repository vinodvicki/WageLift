import type { Metadata } from 'next';
import { ErrorBoundary } from '@/components/ui/error-boundary';
import { ToastProvider } from '@/components/ui/toast';
import './globals.css';

export const metadata: Metadata = {
  title: 'WageLift - Professional Salary Increase Platform',
  description: 'Get the salary increase you deserve with AI-powered raise letters and market data analysis.',
  keywords: 'salary increase, raise letter, wage lift, career advancement, salary negotiation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <ErrorBoundary>
          <ToastProvider>
            {children}
          </ToastProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
} 
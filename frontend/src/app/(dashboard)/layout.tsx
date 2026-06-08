"use client";

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { Sidebar } from '@/components/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const token = useAuthStore((state) => state.token);
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Give Zustand persist a moment to rehydrate
    const timeout = setTimeout(() => {
      if (!useAuthStore.getState().token && pathname !== '/login') {
        router.push('/login');
      }
    }, 100);
    return () => clearTimeout(timeout);
  }, [pathname, router]);

  if (!mounted) return null;
  if (!token) return null;

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden" suppressHydrationWarning>
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="py-6 px-8">
          {children}
        </div>
      </main>
    </div>
  );
}
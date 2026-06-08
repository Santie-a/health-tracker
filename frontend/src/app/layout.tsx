import type { Metadata } from "next";

import "./globals.css";

import { AppNav } from "@/components/layout/app-nav";
import { AsyncBoundary } from "@/components/async/async-boundary";
import { Providers } from "@/components/providers";

// System fonts (globals.css) — no network font fetch, so the arm64/offline build is
// self-contained.
export const metadata: Metadata = {
  title: "Health Tracker",
  description: "Personal training, nutrition, and telemetry dashboard.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <Providers>
          <AppNav />
          {/* pb-20 leaves room for the fixed mobile bottom nav. */}
          <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 pb-20 sm:pb-6">
            <AsyncBoundary>{children}</AsyncBoundary>
          </main>
        </Providers>
      </body>
    </html>
  );
}

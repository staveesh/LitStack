import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Paper Tracker",
  description: "Personal research knowledge base",
};

const nav = [
  { href: "/inbox", label: "Inbox" },
  { href: "/projects", label: "Projects" },
  { href: "/research-questions", label: "Questions" },
  { href: "/claims", label: "Claims" },
  { href: "/open-questions", label: "Open Questions" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen">
          {/* Sidebar */}
          <aside className="w-48 bg-gray-900 text-gray-100 flex flex-col py-6 px-4 shrink-0">
            <Link href="/inbox" className="text-lg font-semibold text-white mb-8 hover:text-gray-300">
              Paper Tracker
            </Link>
            <nav className="flex flex-col gap-1">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-3 py-2 rounded text-sm text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="mt-auto">
              <Link
                href="/settings"
                className="px-3 py-2 rounded text-xs text-gray-500 hover:text-gray-300 block"
              >
                Settings
              </Link>
            </div>
          </aside>

          {/* Main */}
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

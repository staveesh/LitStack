import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "LitStack",
  description: "Personal research knowledge base",
};

const nav = [
  { href: "/inbox", label: "Inbox", icon: "📥" },
  { href: "/projects", label: "Projects", icon: "🗂" },
  { href: "/research-questions", label: "Questions", icon: "❓" },
  { href: "/claims", label: "Claims", icon: "💡" },
  { href: "/open-questions", label: "Open Questions", icon: "🔍" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen">
          {/* Sidebar */}
          <aside className="w-56 bg-slate-950 flex flex-col py-7 px-4 shrink-0 border-r border-slate-800/60">
            {/* Logo */}
            <Link href="/inbox" className="flex items-baseline gap-0.5 mb-8 px-2 group">
              <span className="text-xl font-bold tracking-tight text-white group-hover:text-slate-200 transition-colors">Lit</span>
              <span className="text-xl font-bold tracking-tight text-indigo-400 group-hover:text-indigo-300 transition-colors">Stack</span>
            </Link>

            {/* Nav */}
            <nav className="flex flex-col gap-0.5">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-slate-400 hover:bg-slate-800 hover:text-slate-100 transition-all duration-150"
                >
                  <span className="text-base leading-none opacity-70">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className="mt-auto pt-4 border-t border-slate-800">
              <Link
                href="/settings"
                className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs text-slate-600 hover:text-slate-400 transition-colors"
              >
                <span className="text-sm leading-none">⚙️</span>
                Settings
              </Link>
            </div>
          </aside>

          {/* Main */}
          <main className="flex-1 overflow-y-auto bg-slate-50">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

import type { ReactNode } from 'react';
import { Link } from './SimpleRouter';
import { usePathname } from '../hooks/usePathname';
import { NAV_ITEMS } from '../styles/theme';

export default function Layout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-[#2171B5]">LinkD Agent</h1>
              <span className="text-xs text-gray-400 hidden sm:inline">Multi-Evidence Supported Drug Discovery Platform</span>
            </div>
            <div className="flex gap-1">
              {NAV_ITEMS.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    pathname === item.path
                      ? 'bg-[#2171B5] text-white'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}

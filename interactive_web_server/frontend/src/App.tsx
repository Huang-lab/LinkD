import { Component, lazy, Suspense } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import Layout from './components/Layout';
import { Link } from './components/SimpleRouter';
import { usePathname } from './hooks/usePathname';

const ROUTES = {
  '/': lazy(() => import('./pages/Home')),
  '/overview': lazy(() => import('./pages/Overview')),
  '/binding': lazy(() => import('./pages/Binding')),
  '/selectivity': lazy(() => import('./pages/Selectivity')),
  '/ehr': lazy(() => import('./pages/EHR')),
  '/agent': lazy(() => import('./pages/Agent')),
  '/about': lazy(() => import('./pages/About')),
  '/documentation': lazy(() => import('./pages/Documentation')),
};

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error('React error:', error, info); }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 40, fontFamily: 'Arial' }}>
          <h1 style={{ color: 'red' }}>Something went wrong</h1>
          <p>Please reload the page. If the problem continues, contact the LinkD maintainers.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

function RoutedApplication() {
  const pathname = usePathname();
  const Page = ROUTES[pathname as keyof typeof ROUTES];
  return (
    <Layout>
      {Page ? (
        <Page />
      ) : (
        <div className="py-20 text-center">
          <h2 className="text-xl font-bold text-gray-800 mb-3">Page not found</h2>
          <Link to="/" className="text-[#2171B5] hover:underline">Return home</Link>
        </div>
      )}
    </Layout>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<div className="p-10 text-center text-gray-500">Loading…</div>}>
        <RoutedApplication />
      </Suspense>
    </ErrorBoundary>
  );
}

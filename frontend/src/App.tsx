import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryProvider } from './contexts/QueryProvider';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Rules } from './pages/Rules';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/rules" element={<Rules />} />
              {/* Add more routes here as we build them */}
              <Route path="/notifications" element={<div>Notifications Page (Coming Soon)</div>} />
              <Route path="/settings" element={<div>Settings Page (Coming Soon)</div>} />
            </Routes>
          </Layout>
        </Router>
      </QueryProvider>
    </ErrorBoundary>
  );
}

export default App;

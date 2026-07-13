import React, { useState, useEffect, lazy, Suspense } from 'react';
import { useAuthStore } from './store/authStore';
import { Sidebar } from './components/Sidebar';
import './App.css';

const Login = lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const WearerProfile = lazy(() => import('./pages/WearerProfile').then(m => ({ default: m.WearerProfile })));
const GeofenceEditor = lazy(() => import('./pages/GeofenceEditor').then(m => ({ default: m.GeofenceEditor })));
const CommAssistLogs = lazy(() => import('./pages/CommAssistLogs').then(m => ({ default: m.CommAssistLogs })));
const Reports = lazy(() => import('./pages/Reports').then(m => ({ default: m.Reports })));
const TeamPortal = lazy(() => import('./pages/TeamPortal').then(m => ({ default: m.TeamPortal })));
const Settings = lazy(() => import('./pages/Settings').then(m => ({ default: m.Settings })));
const ResponderQRView = lazy(() => import('./pages/ResponderQRView').then(m => ({ default: m.ResponderQRView })));

function App() {
  const { isAuthenticated } = useAuthStore();
  const [currentPage, setCurrentPage] = useState<string>('dashboard');

  // Simple location pathname-based router for public scanner links
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    const handleLocationChange = () => {
      setPath(window.location.pathname);
    };
    
    // Add custom helper to trigger state update if router is manually triggered
    const originalPushState = window.history.pushState;
    window.history.pushState = function (...args) {
      const result = originalPushState.apply(this, args);
      handleLocationChange();
      return result;
    };

    window.addEventListener('popstate', handleLocationChange);
    return () => {
      window.history.pushState = originalPushState;
      window.removeEventListener('popstate', handleLocationChange);
    };
  }, []);

  // 1. Unauthenticated Public Emergency QR Resolution Routing
  if (path.includes('/qr/resolve/')) {
    const parts = path.split('/qr/resolve/');
    const token = parts[parts.length - 1];
    return (
      <Suspense fallback={<div className="h-screen w-screen flex items-center justify-center bg-aws-dark text-black font-mono text-xs">LOADING EMERGENCY INTERFACE...</div>}>
        <ResponderQRView token={token} />
      </Suspense>
    );
  }

  // 2. Caregiver Console Routing (Authenticated Gate)
  if (!isAuthenticated) {
    return (
      <Suspense fallback={<div className="h-screen w-screen flex items-center justify-center bg-aws-dark text-black font-mono text-xs">LOADING PORTAL...</div>}>
        <Login />
      </Suspense>
    );
  }

  const renderActivePage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'profile':
        return <WearerProfile />;
      case 'geofence':
        return <GeofenceEditor />;
      case 'comms':
        return <CommAssistLogs />;
      case 'reports':
        return <Reports />;
      case 'team':
        return <TeamPortal />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-aws-dark">
      {/* Sidebar Nav */}
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      
      {/* Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Suspense fallback={<div className="flex-1 flex items-center justify-center bg-aws-dark text-black font-mono text-xs">LOADING COMPONENT...</div>}>
          {renderActivePage()}
        </Suspense>
      </div>
    </div>
  );
}

export default App;

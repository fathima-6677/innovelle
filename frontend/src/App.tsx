import { useState, useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import { Sidebar } from './components/Sidebar';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { WearerProfile } from './pages/WearerProfile';
import { GeofenceEditor } from './pages/GeofenceEditor';
import { CommAssistLogs } from './pages/CommAssistLogs';
import { Reports } from './pages/Reports';
import { TeamPortal } from './pages/TeamPortal';
import { Settings } from './pages/Settings';
import { ResponderQRView } from './pages/ResponderQRView';
import './App.css';

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
    return <ResponderQRView token={token} />;
  }

  // 2. Caregiver Console Routing (Authenticated Gate)
  if (!isAuthenticated) {
    return <Login />;
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
        {renderActivePage()}
      </div>
    </div>
  );
}

export default App;

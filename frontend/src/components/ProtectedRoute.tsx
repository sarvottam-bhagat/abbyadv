import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../auth/AuthProvider';
export default function ProtectedRoute() {
  const { loading, session, demo } = useAuth();
  if (loading) return <div className="full-loader"><span className="loader" />Loading AbbyAdv</div>;
  if (!session && !demo) return <Navigate to="/auth" replace />;
  return <Outlet />;
}

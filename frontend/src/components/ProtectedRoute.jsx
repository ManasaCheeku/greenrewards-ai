import { Navigate } from 'react-router-dom';
import { auth } from '../utils/auth';

export default function ProtectedRoute({ element }) {
  return auth.isAuthenticated() ? element : <Navigate to="/login" replace />;
}

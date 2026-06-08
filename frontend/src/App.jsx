import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Assessment from './pages/Assessment';
import Dashboard from './pages/Dashboard';
import Rewards from './pages/Rewards';
import Profile from './pages/Profile';
import Transportation from './pages/Transportation';

// Main layout with navbar
function MainLayout() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen w-full bg-background">
        <div className="animate-fade-in">
          <Outlet />
        </div>
      </main>
    </>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Protected Routes */}
          <Route element={<MainLayout />}>
            <Route path="/assessment" element={<ProtectedRoute element={<Assessment />} />} />
            <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
            <Route path="/rewards" element={<ProtectedRoute element={<Rewards />} />} />
            <Route path="/profile" element={<ProtectedRoute element={<Profile />} />} />
            <Route path="/transportation" element={<ProtectedRoute element={<Transportation />} />} />
          </Route>
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;

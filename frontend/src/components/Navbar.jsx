import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Zap, Menu, X, LogOut, User } from 'lucide-react';
import { auth } from '../utils/auth';

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileDropdown, setIsProfileDropdown] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const user = auth.getCurrentUser();

  const handleLogout = () => {
    auth.logout();
    setIsProfileDropdown(false);
    setIsMobileMenuOpen(false);
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  const navLinks = user ? [
    { name: 'Home', path: '/' },
    { name: 'Assessment', path: '/assessment' },
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Rewards', path: '/rewards' },
  ] : [
    { name: 'Home', path: '/' },
  ];

  return (
    <nav className="sticky top-0 z-50 w-full glass-card border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-3 group focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg px-2 py-1"
            aria-label="GreenRewards AI Home"
          >
            <div className="bg-primary-500 p-2 rounded-lg text-white group-hover:scale-110 transition-transform">
              <Zap size={24} />
            </div>
            <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200 hidden sm:inline">
              GreenRewards AI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8 flex-1 ml-12">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-2 py-1 ${
                  isActive(link.path)
                    ? 'text-primary-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Right Side - Auth Actions */}
          <div className="flex items-center gap-4">
            {user ? (
              <>
                {/* Desktop Profile Dropdown */}
                <div className="hidden md:flex relative">
                  <button
                    onClick={() => setIsProfileDropdown(!isProfileDropdown)}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-500/10 hover:bg-primary-500/20 border border-primary-500/20 text-primary-400 transition-all focus:outline-none focus:ring-2 focus:ring-primary-500"
                    aria-label={`User menu for ${user.name}`}
                    aria-expanded={isProfileDropdown}
                  >
                    <User size={18} />
                    <span className="text-sm font-medium">{user.name.split(' ')[0]}</span>
                  </button>

                  {/* Dropdown Menu */}
                  {isProfileDropdown && (
                    <div className="absolute top-full right-0 mt-2 w-48 bg-surface border border-white/10 rounded-xl shadow-xl z-50 animate-slide-up">
                      <div className="p-4 border-b border-white/10">
                        <div className="text-sm font-semibold text-white">{user.name}</div>
                        <div className="text-xs text-gray-400">{user.email}</div>
                      </div>
                      <Link
                        to="/profile"
                        onClick={() => setIsProfileDropdown(false)}
                        className="block px-4 py-3 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors first:rounded-t-xl"
                      >
                        Profile
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-3 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/5 transition-colors flex items-center gap-2 last:rounded-b-xl"
                      >
                        <LogOut size={16} />
                        Logout
                      </button>
                    </div>
                  )}
                </div>

                {/* Mobile Logout Button */}
                <button
                  onClick={handleLogout}
                  className="md:hidden p-2 text-gray-400 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
                  aria-label="Logout"
                >
                  <LogOut size={20} />
                </button>
              </>
            ) : (
              <div className="hidden md:flex gap-3">
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-white border border-white/20 rounded-lg hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-500 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  Register
                </Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 text-gray-400 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
              aria-label="Toggle mobile menu"
              aria-expanded={isMobileMenuOpen}
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden mt-4 pt-4 border-t border-white/10 space-y-3 animate-slide-up">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`block px-4 py-2 rounded-lg transition-colors ${
                  isActive(link.path)
                    ? 'text-primary-400 bg-primary-500/10'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                {link.name}
              </Link>
            ))}
            {user ? (
              <>
                <Link
                  to="/profile"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="block px-4 py-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                >
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-500/5 rounded-lg transition-colors flex items-center gap-2"
                >
                  <LogOut size={18} />
                  Logout
                </button>
              </>
            ) : (
              <div className="flex gap-2 pt-2">
                <Link
                  to="/login"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="flex-1 text-center px-4 py-2 text-sm font-medium text-white border border-white/20 rounded-lg hover:bg-white/5 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="flex-1 text-center px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-500 rounded-lg transition-colors"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}

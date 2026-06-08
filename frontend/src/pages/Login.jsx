import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Zap, ArrowRight, AlertCircle, CheckCircle2, Loader2, Eye, EyeOff } from 'lucide-react';
import { auth } from '../utils/auth';

export default function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.email) newErrors.email = 'Email is required';
    else if (!formData.email.includes('@')) newErrors.email = 'Invalid email format';
    if (!formData.password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setTimeout(() => {
      const result = auth.login(formData.email, formData.password);
      if (result.success) {
        setMessage({ type: 'success', text: 'Login successful! Redirecting...' });
        setTimeout(() => navigate('/dashboard'), 1500);
      } else {
        setMessage({ type: 'error', text: result.error });
        setIsLoading(false);
      }
    }, 800);
  };

  return (
    <div className="min-h-screen w-full bg-background flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-10 space-y-4">
          <div className="inline-flex items-center justify-center p-3 bg-primary-500/10 rounded-2xl">
            <Zap size={40} className="text-primary-400" />
          </div>
          <h1 className="text-4xl font-bold text-white">Welcome Back</h1>
          <p className="text-gray-400">Login to track your environmental impact</p>
        </div>

        {/* Messages */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-xl border flex items-center gap-3 animate-slide-up ${
              message.type === 'error'
                ? 'bg-red-500/10 border-red-500/20 text-red-400'
                : 'bg-primary-500/10 border-primary-500/20 text-primary-400'
            }`}
            role="alert"
          >
            {message.type === 'error' ? (
              <AlertCircle size={20} />
            ) : (
              <CheckCircle2 size={20} />
            )}
            <p className="font-medium">{message.text}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6" noValidate>
          {/* Email Field */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              aria-label="Email address"
              aria-invalid={!!errors.email}
              aria-describedby={errors.email ? 'email-error' : undefined}
              className={`glass-input w-full ${
                errors.email ? 'border-red-500 focus:ring-red-500/50 focus:border-red-500' : ''
              }`}
            />
            {errors.email && (
              <p id="email-error" className="mt-1 text-sm text-red-400 flex items-center gap-1" role="alert">
                <AlertCircle size={16} />
                {errors.email}
              </p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                aria-label="Password"
                aria-invalid={!!errors.password}
                aria-describedby={errors.password ? 'password-error' : undefined}
                className={`glass-input w-full pr-12 ${
                  errors.password ? 'border-red-500 focus:ring-red-500/50 focus:border-red-500' : ''
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded p-1"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {errors.password && (
              <p id="password-error" className="mt-1 text-sm text-red-400 flex items-center gap-1" role="alert">
                <AlertCircle size={16} />
                {errors.password}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            aria-busy={isLoading}
            className="btn-primary w-full py-3 text-lg mt-8 disabled:opacity-70 disabled:cursor-wait"
          >
            {isLoading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                <span>Logging in...</span>
              </>
            ) : (
              <>
                <span>Login</span>
                <ArrowRight size={20} />
              </>
            )}
          </button>
        </form>

        {/* Register Link */}
        <p className="text-center text-gray-400 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
            Register here
          </Link>
        </p>

        {/* Demo Credentials */}
        <div className="mt-8 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
          <p className="text-xs text-blue-400 font-medium mb-2">Demo Credentials:</p>
          <p className="text-xs text-blue-300">Email: demo@example.com</p>
          <p className="text-xs text-blue-300">Password: demo123</p>
        </div>
      </div>
    </div>
  );
}

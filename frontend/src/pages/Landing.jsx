import { Link } from 'react-router-dom';
import { ArrowRight, Leaf, Shield, Zap, Target } from 'lucide-react';
import { auth } from '../utils/auth';

export default function Landing() {
  const user = auth.getCurrentUser();

  return (
    <div className="min-h-[calc(100vh-80px)] w-full bg-background flex flex-col items-center justify-center px-4 py-20 relative overflow-hidden">
      {/* Abstract Background Shapes */}
      <div className="absolute top-1/4 -left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-[100px]" />
      <div className="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-[100px]" />
      
      <div className="max-w-6xl mx-auto z-10 w-full animate-fade-in text-center space-y-8">
        
        {/* Header Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 font-medium tracking-wide shadow-lg shadow-primary-500/10 mx-auto">
          <Leaf size={16} />
          <span>The Future of Sustainability Tracking</span>
        </div>

        {/* Hero Text */}
        <div className="space-y-6">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white leading-tight">
            Track Green. <br className="hidden md:block" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-emerald-200">
              Live Green. Earn Green.
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto font-light">
            AI-powered sustainability tracking that rewards you for reducing your carbon footprint. 
            Join the movement toward a cleaner, greener planet.
          </p>
        </div>

        {/* Call to Action */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
          {user ? (
            <>
              <Link 
                to="/assessment"
                className="group relative inline-flex items-center justify-center gap-3 bg-gradient-to-r from-primary-600 to-primary-400 text-white font-semibold text-lg px-8 py-4 rounded-full shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] transition-all duration-300 hover:-translate-y-1 w-full sm:w-auto overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
                <span className="relative z-10">Take Assessment</span>
                <ArrowRight size={20} className="relative z-10 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <Link 
                to="/dashboard"
                className="inline-flex items-center justify-center gap-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium text-lg px-8 py-4 rounded-full transition-all duration-300 w-full sm:w-auto"
              >
                View Dashboard
              </Link>
            </>
          ) : (
            <>
              <Link 
                to="/register"
                className="group relative inline-flex items-center justify-center gap-3 bg-gradient-to-r from-primary-600 to-primary-400 text-white font-semibold text-lg px-8 py-4 rounded-full shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_40px_rgba(16,185,129,0.5)] transition-all duration-300 hover:-translate-y-1 w-full sm:w-auto overflow-hidden"
              >
                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
                <span className="relative z-10">Get Started</span>
                <ArrowRight size={20} className="relative z-10 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <Link 
                to="/login"
                className="inline-flex items-center justify-center gap-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium text-lg px-8 py-4 rounded-full transition-all duration-300 w-full sm:w-auto"
              >
                Login
              </Link>
            </>
          )}
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-20 text-left">
          <div className="glass-card p-6 border-white/5 hover:border-primary-500/30 transition-colors group">
            <div className="w-12 h-12 bg-primary-500/10 rounded-xl flex items-center justify-center text-primary-400 mb-4 group-hover:scale-110 transition-transform">
              <Zap size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Automated Insights</h3>
            <p className="text-gray-400 text-sm">AI Coach analyzes your habits to provide personalized, actionable tips for a greener lifestyle.</p>
          </div>
          
          <div className="glass-card p-6 border-white/5 hover:border-primary-500/30 transition-colors group">
            <div className="w-12 h-12 bg-primary-500/10 rounded-xl flex items-center justify-center text-primary-400 mb-4 group-hover:scale-110 transition-transform">
              <Target size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Goal Tracking</h3>
            <p className="text-gray-400 text-sm">Set personal reduction goals across transport, electricity, food, and plastic usage.</p>
          </div>
          
          <div className="glass-card p-6 border-white/5 hover:border-primary-500/30 transition-colors group">
            <div className="w-12 h-12 bg-primary-500/10 rounded-xl flex items-center justify-center text-primary-400 mb-4 group-hover:scale-110 transition-transform">
              <Shield size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Earn Eco Points</h3>
            <p className="text-gray-400 text-sm">Log sustainable activities to earn points that translate to real-world rewards.</p>
          </div>
        </div>

      </div>
    </div>
  );
}

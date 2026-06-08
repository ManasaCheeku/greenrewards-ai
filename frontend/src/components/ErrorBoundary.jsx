import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
          <div className="max-w-md w-full glass-card p-8 border-red-500/20 text-center flex flex-col items-center gap-6">
            <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center text-red-400">
              <AlertTriangle size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-2">Something went wrong</h2>
              <p className="text-gray-400 text-sm">
                We encountered an unexpected error. Don't worry, your data is safe. Let's get you back on track.
              </p>
            </div>
            <button
              onClick={() => window.location.href = '/'}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <RefreshCw size={18} />
              Return to Home
            </button>
            {import.meta.env.DEV && this.state.error && (
              <div className="mt-4 p-4 bg-black/40 rounded-lg text-left overflow-auto w-full">
                <p className="text-red-400 text-xs font-mono break-all">
                  {this.state.error.toString()}
                </p>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

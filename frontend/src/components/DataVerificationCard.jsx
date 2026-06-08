import { Shield, CheckCircle2, AlertCircle, Smartphone, Zap, Train, Leaf, Receipt, Eye } from 'lucide-react';

export default function DataVerificationCard() {
  // Verification methods with icons
  const verificationMethods = [
    {
      id: 'transport',
      title: 'Public Transport Verification',
      icon: <Train size={20} />,
      methods: [
        { name: 'Metro QR Ticket Upload', status: 'coming-soon' },
        { name: 'Bus Ticket Upload', status: 'coming-soon' },
        { name: 'Smart Transit Card Integration', status: 'coming-soon' }
      ]
    },
    {
      id: 'walking',
      title: 'Walking Verification',
      icon: <Leaf size={20} />,
      methods: [
        { name: 'Google Fit Integration', status: 'coming-soon' },
        { name: 'Apple Health Integration', status: 'coming-soon' },
        { name: 'Smartwatch Integration', status: 'coming-soon' }
      ]
    },
    {
      id: 'electricity',
      title: 'Electricity Verification',
      icon: <Zap size={20} />,
      methods: [
        { name: 'Electricity Bill Upload', status: 'coming-soon' },
        { name: 'Smart Meter Integration', status: 'coming-soon' }
      ]
    },
    {
      id: 'plastic',
      title: 'Plastic Reduction Verification',
      icon: <Receipt size={20} />,
      methods: [
        { name: 'Receipt Scanning', status: 'coming-soon' },
        { name: 'Reusable Bottle Tracking', status: 'coming-soon' }
      ]
    }
  ];

  const confidenceLevels = [
    { level: 'Self Reported', score: '50%', color: 'text-yellow-400', bgColor: 'bg-yellow-500/10', borderColor: 'border-yellow-500/20' },
    { level: 'Partially Verified', score: '75%', color: 'text-blue-400', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/20' },
    { level: 'Fully Verified', score: '100%', color: 'text-green-400', bgColor: 'bg-green-500/10', borderColor: 'border-green-500/20' }
  ];

  return (
    <div className="space-y-6">
      {/* Main Verification Status Card */}
      <div className="glass-card p-6 md:p-8 border-blue-500/20">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0 mt-1">
              <Shield size={24} />
            </div>
            <div>
              <h3 className="text-2xl md:text-3xl font-bold">Data Verification Status</h3>
              <p className="text-gray-400 text-sm mt-1">Track the confidence level of your sustainability data</p>
            </div>
          </div>
          
          {/* Prototype Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 font-medium text-sm whitespace-nowrap shrink-0">
            <AlertCircle size={16} />
            <span>Prototype Version</span>
          </div>
        </div>

        {/* Current Status Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Current Status */}
          <div className="glass-card p-6 bg-white/5 border-blue-500/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center">
                <Eye size={16} />
              </div>
              <h4 className="font-semibold text-white">Current Status</h4>
            </div>
            <p className="text-2xl font-bold text-blue-300">Self-Reported Data</p>
            <p className="text-xs text-gray-500 mt-2">All data provided by user</p>
          </div>

          {/* Trust Score */}
          <div className="glass-card p-6 bg-white/5 border-yellow-500/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-yellow-500/20 text-yellow-400 flex items-center justify-center">
                <Shield size={16} />
              </div>
              <h4 className="font-semibold text-white">Trust Score</h4>
            </div>
            <p className="text-2xl font-bold text-yellow-300">50% Confidence</p>
            <p className="text-xs text-gray-500 mt-2">Medium confidence level</p>
          </div>

          {/* Verification Progress */}
          <div className="glass-card p-6 bg-white/5 border-gray-500/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-gray-500/20 text-gray-400 flex items-center justify-center">
                <CheckCircle2 size={16} />
              </div>
              <h4 className="font-semibold text-white">Future Ready</h4>
            </div>
            <p className="text-2xl font-bold text-gray-300">Coming Soon</p>
            <p className="text-xs text-gray-500 mt-2">Verification features</p>
          </div>
        </div>

        {/* Explanation */}
        <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20 mb-8">
          <p className="text-blue-100 text-sm leading-relaxed">
            Current sustainability calculations are based on user-provided information. Future versions will support automatic verification for greater accuracy, allowing you to connect your devices and accounts for real-time data synchronization.
          </p>
        </div>
      </div>

      {/* Confidence Score Levels */}
      <div className="glass-card p-6 md:p-8 border-gray-500/20">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Smartphone size={24} className="text-primary-400" />
          Carbon Confidence Score Levels
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {confidenceLevels.map((item, idx) => (
            <div key={idx} className={`p-4 rounded-lg border ${item.bgColor} ${item.borderColor} transition-all hover:shadow-lg hover:shadow-${item.color}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-white">{item.level}</span>
                <span className={`text-sm font-bold ${item.color}`}>{item.score}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${item.color} transition-all`}
                  style={{ width: item.score }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Future Verification Methods */}
      <div className="glass-card p-6 md:p-8 border-green-500/20">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <CheckCircle2 size={24} className="text-primary-400" />
          Future Verification Methods
        </h3>
        <p className="text-gray-400 text-sm mb-6">
          Coming in future versions, integrate these methods to automatically verify your sustainability data:
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {verificationMethods.map((category) => (
            <div key={category.id} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-primary-500/30 transition-colors">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary-500/20 text-primary-400 flex items-center justify-center">
                  {category.icon}
                </div>
                <h4 className="font-semibold text-white">{category.title}</h4>
              </div>
              
              <ul className="space-y-2">
                {category.methods.map((method, idx) => (
                  <li key={idx} className="flex items-center gap-3 text-sm">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary-500/50"></div>
                    <span className="text-gray-300">{method.name}</span>
                    <span className="ml-auto text-xs text-gray-600 bg-gray-800/50 px-2 py-1 rounded">
                      {method.status === 'coming-soon' ? '🔜 Soon' : '✓'}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Coming Soon Banner */}
      <div className="glass-card p-6 md:p-8 bg-gradient-to-r from-orange-500/5 to-red-500/5 border border-orange-500/30">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-orange-500/20 text-orange-400 flex items-center justify-center shrink-0 mt-1">
            <AlertCircle size={20} />
          </div>
          <div>
            <h4 className="font-bold text-white mb-2">Prototype Version – Verification Features Coming Soon</h4>
            <p className="text-orange-100 text-sm">
              We're building automatic verification capabilities to give you more accurate carbon footprint calculations. 
              In the meantime, your self-reported data helps us learn about sustainable practices in your community. 
              Your feedback will help shape these verification features!
            </p>
            <button className="mt-4 px-4 py-2 rounded-lg bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/30 text-orange-400 font-medium text-sm transition-colors">
              Send Feedback
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

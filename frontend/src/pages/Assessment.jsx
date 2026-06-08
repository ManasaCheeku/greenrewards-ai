import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Leaf, Navigation, Zap, Utensils, Droplet, ArrowRight, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import { auth } from '../utils/auth';

const InputField = ({ label, name, placeholder, unit, value, onChange, error }) => {
  const hasError = !!error;
  const id = `input-${name}`;
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium text-gray-300">{label}</label>
      <div className="relative">
        <input
          id={id}
          type="number"
          min="0"
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          aria-label={label}
          aria-invalid={hasError}
          aria-describedby={hasError ? `${id}-error` : undefined}
          className={`glass-input w-full ${hasError ? 'border-red-500 focus:ring-red-500/50 focus:border-red-500' : 'focus:ring-2 focus:ring-primary-500 focus:border-primary-500'}`}
        />
        {unit && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-sm pointer-events-none" aria-hidden="true">
            {unit}
          </span>
        )}
      </div>
      {hasError && <span id={`${id}-error`} className="text-xs text-red-400 font-medium flex items-center gap-1" role="alert"><AlertCircle size={16} />{error}</span>}
    </div>
  );
};

export default function Assessment() {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    busTrips: '',
    metroTrips: '',
    personalVehicleDays: '',
    walkingSteps: '',
    cyclingMinutes: '',
    electricityUnits: '',
    vegetarianDays: '',
    nonVegetarianMeals: '',
    waterBottles: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (value === '' || (/^\d+$/.test(value) && Number(value) >= 0)) {
      setFormData(prev => ({ ...prev, [name]: value }));
      if (errors[name]) {
        setErrors(prev => ({ ...prev, [name]: '' }));
      }
    }
  };

  const validateForm = () => {
    const newErrors = {};
    const requiredFields = [
      'busTrips', 'metroTrips', 'personalVehicleDays', 'walkingSteps', 
      'cyclingMinutes', 'electricityUnits', 'vegetarianDays', 
      'nonVegetarianMeals', 'waterBottles'
    ];

    requiredFields.forEach(field => {
      if (formData[field] === '') {
        newErrors[field] = 'Value required';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const calculateEcoScore = () => {
    let score = 50; 
    score += Number(formData.walkingSteps) > 5000 ? 5 : 0;
    score += Number(formData.cyclingMinutes) > 30 ? 5 : 0;
    score += Number(formData.busTrips) > 0 ? 2 : 0;
    score += Number(formData.metroTrips) > 0 ? 3 : 0;
    score -= Number(formData.personalVehicleDays) * 2;

    const units = Number(formData.electricityUnits);
    if (units < 100) score += 10;
    else if (units > 200) score -= 10;
    else if (units > 300) score -= 20;

    score += Number(formData.vegetarianDays) * 2;
    score -= Number(formData.nonVegetarianMeals);
    score -= Number(formData.waterBottles) * 2;

    return Math.max(0, Math.min(100, score));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      setIsSubmitting(true);
      setTimeout(() => {
        const score = calculateEcoScore();
        const user = auth.getCurrentUser();
        if (user) {
          auth.updateAssessmentData(score, 50, formData);
        }
        navigate('/dashboard', { state: { newScore: score, message: 'Assessment completed successfully!', assessmentData: formData } });
      }, 1500);
    } else {
      const firstInvalid = document.querySelector('[aria-invalid="true"]');
      if (firstInvalid) firstInvalid.focus();
    }
  };

  return (
    <div className="min-h-screen w-full bg-background pt-24 px-4 md:px-8 pb-12">
      <div className="max-w-3xl mx-auto z-10 relative">
        <div className="text-center mb-10 space-y-4 animate-fade-in" role="banner">
          <div className="inline-flex items-center justify-center p-3 bg-primary-500/10 rounded-2xl mb-2" aria-hidden="true">
            <Leaf size={32} className="text-primary-400" />
          </div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-emerald-200">
            Initial Sustainability Assessment
          </h1>
          <p className="text-gray-400 text-lg">
            Let's establish your baseline Eco Score. Be honest—this helps your AI Coach personalize your journey.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8 animate-slide-up" noValidate aria-label="Sustainability Assessment Form">
          <div className="glass-card p-8 border-primary-500/20" role="group" aria-labelledby="transport-heading">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400" aria-hidden="true"><Navigation size={24} /></div>
              <h2 id="transport-heading" className="text-2xl font-semibold">Weekly Transportation</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField label="Bus Trips" name="busTrips" placeholder="0" unit="trips" value={formData.busTrips} onChange={handleInputChange} error={errors.busTrips} />
              <InputField label="Metro Trips" name="metroTrips" placeholder="0" unit="trips" value={formData.metroTrips} onChange={handleInputChange} error={errors.metroTrips} />
              <InputField label="Personal Vehicle Usage" name="personalVehicleDays" placeholder="0" unit="days" value={formData.personalVehicleDays} onChange={handleInputChange} error={errors.personalVehicleDays} />
              <InputField label="Average Daily Steps" name="walkingSteps" placeholder="0" unit="steps" value={formData.walkingSteps} onChange={handleInputChange} error={errors.walkingSteps} />
              <InputField label="Average Daily Cycling" name="cyclingMinutes" placeholder="0" unit="mins" value={formData.cyclingMinutes} onChange={handleInputChange} error={errors.cyclingMinutes} />
            </div>
          </div>

          <div className="glass-card p-8 border-yellow-500/20" role="group" aria-labelledby="electricity-heading">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-yellow-500/20 text-yellow-400" aria-hidden="true"><Zap size={24} /></div>
              <h2 id="electricity-heading" className="text-2xl font-semibold">Monthly Electricity</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField label="Electricity Usage" name="electricityUnits" placeholder="0" unit="units (kWh)" value={formData.electricityUnits} onChange={handleInputChange} error={errors.electricityUnits} />
            </div>
          </div>

          <div className="glass-card p-8 border-green-500/20" role="group" aria-labelledby="food-heading">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-green-500/20 text-green-400" aria-hidden="true"><Utensils size={24} /></div>
              <h2 id="food-heading" className="text-2xl font-semibold">Weekly Food Habits</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField label="Vegetarian Days" name="vegetarianDays" placeholder="0" unit="days" value={formData.vegetarianDays} onChange={handleInputChange} error={errors.vegetarianDays} />
              <InputField label="Non-Vegetarian Meals" name="nonVegetarianMeals" placeholder="0" unit="meals" value={formData.nonVegetarianMeals} onChange={handleInputChange} error={errors.nonVegetarianMeals} />
            </div>
          </div>

          <div className="glass-card p-8 border-cyan-500/20" role="group" aria-labelledby="plastic-heading">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-cyan-500/20 text-cyan-400" aria-hidden="true"><Droplet size={24} /></div>
              <h2 id="plastic-heading" className="text-2xl font-semibold">Weekly Plastic Usage</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField label="Water Bottles Purchased" name="waterBottles" placeholder="0" unit="bottles" value={formData.waterBottles} onChange={handleInputChange} error={errors.waterBottles} />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row justify-center sm:justify-end gap-4 pt-4 pb-12">
            <button 
              type="submit" 
              disabled={isSubmitting}
              aria-busy={isSubmitting}
              className={`btn-primary px-10 py-4 text-lg w-full sm:w-auto focus:ring-4 focus:ring-primary-500/50 outline-none ${isSubmitting ? 'opacity-70 cursor-wait' : ''}`}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin" size={20} aria-hidden="true" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 size={20} aria-hidden="true" />
                  <span>Submit Assessment & Generate Score</span>
                  <ArrowRight size={20} className="ml-2" aria-hidden="true" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

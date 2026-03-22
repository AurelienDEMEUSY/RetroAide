import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Landmark, ArrowLeft, ArrowRight, ThumbsUp, Ban } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const OnboardingStep3 = () => {
  const navigate = useNavigate();
  const [currentlyEmployed, setCurrentlyEmployed] = useState(null);
  const [currentIncomeAnnual, setCurrentIncomeAnnual] = useState('');
  const [validatedQuarters, setValidatedQuarters] = useState('');

  const canProceed = currentlyEmployed !== null && currentIncomeAnnual !== '' && validatedQuarters !== '';

  const handleNext = () => {
    const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
    localStorage.setItem('retroaide_onboarding', JSON.stringify({ 
      ...data, 
      currentlyEmployed, 
      currentIncomeAnnual: parseInt(currentIncomeAnnual, 10) || 0, 
      validatedQuarters: parseInt(validatedQuarters, 10) || 0 
    }));
    navigate('/onboarding/4');
  };

  return (
    <div className="min-h-screen bg-slate-50/30 font-sans text-slate-900 flex flex-col">
      {/* Header */}
      <header className="px-6 py-4 flex justify-between items-center bg-white border-b border-transparent">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
          <Landmark className="w-5 h-5 text-slate-800" />
          <span className="font-bold text-xl tracking-tight">RetroAide</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-12">
        {/* Progress Bar */}
        <div className="flex gap-2 mb-14 px-4 sm:px-0">
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-slate-200 rounded-full"></div>
        </div>

        {/* Title Section */}
        <div className="mb-12 text-center sm:text-left">
          <span className="text-sm font-bold text-slate-400 uppercase tracking-widest block mb-3">ÉTAPE 3 SUR 4</span>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-5 tracking-tight">Votre Bilan Actuel</h1>
          <p className="text-slate-600 text-lg leading-relaxed max-w-2xl">
            Regardez votre dernier Relevé de Situation Individuelle (RIS) pour remplir ces informations.
          </p>
        </div>

        <div className="bg-white rounded-[2rem] p-8 sm:p-10 shadow-sm border border-slate-100 mb-12 space-y-12">

          {/* Currently Employed */}
          <div>
            <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
              Êtes-vous actuellement en activité ?
            </h3>
            <div className="grid grid-cols-2 gap-5">
              <button
                onClick={() => setCurrentlyEmployed(true)}
                className={cn(
                  "flex items-center justify-center gap-3 py-4 rounded-xl border-2 transition-all duration-300 font-bold text-[16px]",
                  currentlyEmployed === true
                    ? "border-[#0f172a] bg-[#f8fafc] text-[#0f172a]"
                    : "border-transparent bg-slate-50 text-slate-600 hover:bg-slate-100"
                )}
              >
                <ThumbsUp size={20} strokeWidth={2.5} />
                Oui
              </button>
              <button
                onClick={() => setCurrentlyEmployed(false)}
                className={cn(
                  "flex items-center justify-center gap-3 py-4 rounded-xl border-2 transition-all duration-300 font-bold text-[16px]",
                  currentlyEmployed === false
                    ? "border-[#0f172a] bg-[#f8fafc] text-[#0f172a]"
                    : "border-transparent bg-slate-50 text-slate-600 hover:bg-slate-100"
                )}
              >
                <Ban size={20} strokeWidth={2.5} />
                Non
              </button>
            </div>
          </div>

          {/* Exact Annual Income */}
          {currentlyEmployed !== null && (
            <div className="animate-in fade-in slide-in-from-top-4 duration-500">
              <h3 className="text-xl font-bold text-[#0f172a] mb-2 tracking-tight">
                {currentlyEmployed 
                  ? "Votre revenu brut annuel actuel" 
                  : "Le salaire moyen de vos 25 meilleures années"}
              </h3>
              <p className="text-sm text-slate-500 mb-5 font-medium">
                Veuillez indiquer le montant exact annuel (brut) en euros.
              </p>
              <div className="relative w-full sm:w-1/2">
                <input
                  type="number"
                  placeholder="Ex: 45000"
                  min="0" max="300000"
                  value={currentIncomeAnnual}
                  onChange={(e) => {
                    const v = parseInt(e.target.value, 10);
                    if (e.target.value === '' || (v >= 0 && v <= 300000)) setCurrentIncomeAnnual(e.target.value);
                  }}
                  className="w-full p-5 pr-12 bg-slate-50 rounded-xl border border-slate-200 text-xl font-medium focus:ring-2 focus:ring-[#0f172a] transition-all placeholder:text-slate-300"
                />
                <span className="absolute right-5 top-1/2 -translate-y-1/2 text-xl font-bold text-slate-400">€</span>
              </div>
            </div>
          )}

          {/* Validated Quarters */}
          <div>
            <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
              Nombre de trimestres validés à ce jour
            </h3>
            <input
              type="number"
              placeholder="Ex: 110"
              min="0" max="172"
              value={validatedQuarters}
              onChange={(e) => {
                const v = parseInt(e.target.value, 10);
                if (e.target.value === '' || (v >= 0 && v <= 172)) setValidatedQuarters(e.target.value);
              }}
              className="w-full sm:w-1/2 p-5 bg-slate-50 rounded-xl border border-slate-200 text-xl font-medium focus:ring-2 focus:ring-[#0f172a] transition-all placeholder:text-slate-300"
            />
            <p className="text-sm text-slate-500 mt-3 font-medium">
              Ce nombre figure sur votre dernier relevé de carrière (max : 172).
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div className="px-2 sm:px-0 flex gap-4">
          <button
            onClick={() => navigate('/onboarding/2')}
            className="w-1/3 py-5 bg-white border-2 border-slate-200 text-slate-600 text-lg font-bold rounded-xl shadow-sm hover:border-slate-300 hover:bg-slate-50 transition-all mb-16 flex items-center justify-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Retour
          </button>
          <button
            disabled={!canProceed}
            onClick={handleNext}
            className={cn(
              "w-2/3 py-5 text-white text-lg font-bold rounded-xl transition-all mb-16 flex items-center justify-center gap-2",
              canProceed
                ? "bg-[#1e293b] shadow-xl hover:bg-[#0f172a] hover:scale-[1.01] active:scale-[0.99]"
                : "bg-slate-300 text-slate-500 cursor-not-allowed"
            )}
          >
            Continuer
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </main>
    </div>
  );
};

export default OnboardingStep3;

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Landmark, ArrowLeft, CheckCircle2, Target, HandCoins, ArrowDownToLine, TrendingUp } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const OnboardingStep4 = () => {
  const navigate = useNavigate();
  const [mainObjective, setMainObjective] = useState('');
  const [targetDepartureAge, setTargetDepartureAge] = useState('');
  
  // Optional identity fields for the PDF report
  const [fullName, setFullName] = useState('');
  const [villeSignature, setVilleSignature] = useState('');

  const objectiveOptions = [
    { id: 'partir_tot', label: 'Partir le plus tôt possible quitte à perdre un peu d\'argent', icon: ArrowDownToLine },
    { id: 'retraite_max', label: 'Travailler jusqu\'à avoir la retraite maximale', icon: Target },
    { id: 'lever_pied', label: 'Lever le pied progressivement', icon: HandCoins },
    { id: 'augmenter_revenus', label: 'Augmenter mes revenus à la retraite', icon: TrendingUp },
  ];

  const canProceed = mainObjective && targetDepartureAge !== '';

  const handleSubmit = () => {
    const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
    localStorage.setItem('retroaide_onboarding', JSON.stringify({ 
      ...data, 
      mainObjective,
      targetDepartureAge: parseInt(targetDepartureAge, 10),
      fullName,
      villeSignature
    }));
    navigate('/dashboard');
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
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
        </div>

        {/* Title Section */}
        <div className="mb-12 text-center sm:text-left">
          <span className="text-sm font-bold text-slate-400 uppercase tracking-widest block mb-3">ÉTAPE 4 SUR 4</span>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-5 tracking-tight">Vos Objectifs</h1>
          <p className="text-slate-600 text-lg leading-relaxed max-w-2xl">
            L'IA a besoin de savoir ce que vous voulez pour cibler ses conseils.
          </p>
        </div>

        {/* Form Container */}
        <div className="bg-white rounded-2xl p-6 sm:p-10 shadow-sm border border-slate-100 mb-12 space-y-12">
          
          {/* Main Objective */}
          <div>
            <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
              Quel est votre objectif principal pour la retraite ?
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {objectiveOptions.map((option) => {
                const Icon = option.icon;
                const isSelected = mainObjective === option.id;
                
                return (
                  <button
                    key={option.id}
                    onClick={() => setMainObjective(option.id)}
                    className={cn(
                      "flex items-center gap-4 p-5 rounded-2xl border-2 transition-all duration-300 text-left",
                      isSelected 
                        ? "border-[#0f172a] bg-white ring-4 ring-slate-100/50" 
                        : "border-transparent bg-slate-50 shadow-sm hover:border-slate-200"
                    )}
                  >
                    <div className={cn(
                      "w-12 h-12 shrink-0 rounded-xl flex items-center justify-center transition-all duration-300",
                      isSelected ? "bg-[#0f2444] text-white" : "bg-[#daedfd] text-[#3b82f6]"
                    )}>
                      <Icon size={24} strokeWidth={2.5} />
                    </div>
                    <span className={cn(
                      "font-bold text-[14px] leading-tight",
                      isSelected ? "text-[#0f172a]" : "text-slate-700"
                    )}>
                      {option.label}
                    </span>
                    {isSelected && (
                      <CheckCircle2 size={20} className="text-[#0f2444] shrink-0 ml-auto" strokeWidth={3} />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Targeted Departure Age */}
          <div>
            <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
              Idéalement, à quel âge aimeriez-vous partir ?
            </h3>
            <input
              type="number"
              placeholder="Ex: 62"
              min="50" max="80"
              value={targetDepartureAge}
              onChange={(e) => setTargetDepartureAge(e.target.value)}
              className="w-full sm:w-1/2 p-5 bg-slate-50 rounded-xl border border-slate-200 text-xl font-medium focus:ring-2 focus:ring-[#0f172a] transition-all placeholder:text-slate-300"
            />
          </div>

          {/* Optional Identity */}
          <div className="pt-8 border-t border-slate-100">
            <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
              Identité pour votre rapport (Optionnel)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Prénom et Nom</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ex: Jean Dupont"
                  className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Lieu (pour la signature)</label>
                <input
                  type="text"
                  value={villeSignature}
                  onChange={(e) => setVilleSignature(e.target.value)}
                  placeholder="Ex: Paris"
                  className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
                />
              </div>
            </div>
          </div>

        </div>

        {/* Action Button */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            onClick={() => navigate('/onboarding/3')}
            className="w-full sm:w-auto flex items-center justify-center gap-2 py-5 px-8 bg-white border-2 border-slate-200 text-slate-600 text-lg font-bold rounded-xl shadow-sm hover:bg-slate-50 transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
            Retour
          </button>
          <button
            disabled={!canProceed}
            onClick={handleSubmit}
            className={cn(
              "w-full sm:w-auto flex items-center justify-center gap-2 py-5 px-12 text-white text-lg font-bold rounded-xl transition-all shadow-xl",
              canProceed
                ? "bg-[#0f2444] hover:bg-[#1e3a6a] hover:-translate-y-0.5"
                : "bg-slate-300 text-slate-500 cursor-not-allowed shadow-none hover:translate-y-0"
            )}
          >
            Analyser ma situation
            <CheckCircle2 className="w-5 h-5 text-[#93e1b4]" />
          </button>
        </div>
      </main>
    </div>
  );
};

export default OnboardingStep4;

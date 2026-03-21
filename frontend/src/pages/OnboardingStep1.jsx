import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Info, CheckCircle2 } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const OnboardingStep1 = () => {
  const navigate = useNavigate();
  const [birthMonth, setBirthMonth] = useState('');
  const [birthYear, setBirthYear] = useState('');
  const [maritalStatus, setMaritalStatus] = useState('');
  const [nbEnfants, setNbEnfants] = useState('');

  const maritalOptions = [
    { id: 'celibataire', label: 'Célibataire' },
    { id: 'marie', label: 'Marié(e)' },
    { id: 'pacse', label: 'Pacsé(e)' },
    { id: 'divorce', label: 'Divorcé(e)' },
    { id: 'veuf', label: 'Veuf/Veuve' }
  ];

  const canProceed = birthMonth && birthYear && maritalStatus && nbEnfants !== '';

  const handleNext = () => {
    localStorage.setItem('retroaide_onboarding', JSON.stringify({ 
      birthMonth: parseInt(birthMonth, 10), 
      birthYear: parseInt(birthYear, 10), 
      maritalStatus, 
      nbEnfants: parseInt(nbEnfants, 10) || 0 
    }));
    navigate('/onboarding/2');
  };

  return (
    <div className="min-h-screen bg-[#F8F9FB] flex flex-col items-center py-6 px-4 font-sans text-[#0F2544]">
      {/* Top Header */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-12">
        <h1 className="text-2xl font-bold tracking-tight cursor-pointer" onClick={() => navigate('/')}>RetroAide</h1>
      </div>

      {/* Progress Section */}
      <div className="w-full max-w-3xl mb-16 px-2">
        <div className="flex justify-between items-end mb-3">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">ÉTAPE 1 SUR 4</span>
          <span className="text-[15px] font-extrabold text-[#0F2544]">25%</span>
        </div>
        <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
          <div className="h-full bg-[#9AE6B4] rounded-full transition-all duration-500 ease-out" style={{ width: '25%' }} />
        </div>
      </div>

      {/* Title Section */}
      <div className="w-full max-w-3xl mb-10 text-center sm:text-left px-2">
        <h2 className="text-4xl sm:text-5xl font-extrabold mb-4 tracking-tight">Votre Profil</h2>
        <p className="text-slate-500 text-lg sm:text-xl max-w-xl leading-relaxed">
          Commençons par les bases pour établir votre simulateur personnalisé.
        </p>
      </div>

      {/* Form Cards Container */}
      <div className="w-full max-w-3xl space-y-6">
        
        {/* Date of Birth Card */}
        <div className="bg-white rounded-[2rem] p-8 sm:p-10 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-50">
          <h3 className="text-2xl font-bold mb-6">Quelle est votre date de naissance ?</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-bold text-slate-500 mb-2 ml-2">Mois (1-12)</label>
              <input
                type="number"
                placeholder="Ex: 5"
                min="1" max="12"
                value={birthMonth}
                onChange={(e) => setBirthMonth(e.target.value)}
                className="w-full p-5 bg-slate-100/80 rounded-2xl border-none text-xl focus:ring-2 focus:ring-[#0F2544] transition-all placeholder:text-slate-300"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-500 mb-2 ml-2">Année</label>
              <input
                type="number"
                placeholder="Ex: 1975"
                value={birthYear}
                onChange={(e) => setBirthYear(e.target.value)}
                className="w-full p-5 bg-slate-100/80 rounded-2xl border-none text-xl focus:ring-2 focus:ring-[#0F2544] transition-all placeholder:text-slate-300"
              />
            </div>
          </div>
          <div className="flex items-start gap-4 p-5 bg-[#E8F3F7] rounded-2xl">
            <div className="w-8 h-8 rounded-full bg-[#0F2544] flex items-center justify-center flex-shrink-0 mt-0.5">
              <Info className="w-4 h-4 text-white" />
            </div>
            <p className="text-[#0F2544] text-sm leading-relaxed font-medium">
              L'année de naissance seule ne suffit pas : avec les récentes réformes, le mois définit précisément l'âge légal et le nombre de trimestres requis.
            </p>
          </div>
        </div>

        {/* Marital Status Card */}
        <div className="bg-white rounded-[2rem] p-8 sm:p-10 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-50">
          <h3 className="text-2xl font-bold mb-8">Votre situation maritale</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {maritalOptions.map((option) => {
              const isSelected = maritalStatus === option.id;
              return (
                <button
                  key={option.id}
                  onClick={() => setMaritalStatus(option.id)}
                  className={cn(
                    "flex items-center justify-between p-4 rounded-xl border-2 transition-all duration-200",
                    isSelected 
                      ? "border-[#0F2544] bg-[#F8F9FB] text-[#0F2544]" 
                      : "border-transparent bg-slate-50 text-slate-600 hover:bg-slate-100"
                  )}
                >
                  <span className="font-bold text-base">{option.label}</span>
                  {isSelected && <CheckCircle2 size={18} className="text-[#0F2544]" strokeWidth={3} />}
                </button>
              );
            })}
          </div>
        </div>

        {/* Children Card */}
        <div className="bg-white rounded-[2rem] p-8 sm:p-10 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-50">
          <h3 className="text-2xl font-bold mb-6">Combien d'enfants avez-vous eu ?</h3>
          <input
            type="number"
            placeholder="Ex: 2"
            min="0"
            value={nbEnfants}
            onChange={(e) => setNbEnfants(e.target.value)}
            className="w-full sm:w-1/2 p-5 bg-slate-100/80 rounded-2xl border-none text-xl focus:ring-2 focus:ring-[#0F2544] transition-all placeholder:text-slate-300"
          />
        </div>

      </div>

      {/* Action Button */}
      <div className="w-full max-w-3xl flex flex-col items-center mt-12 mb-16">
        <button
          onClick={handleNext}
          disabled={!canProceed}
          className={cn(
            "px-12 py-5 rounded-2xl font-bold text-xl flex items-center gap-3 transition-all shadow-xl active:scale-95",
            canProceed
              ? "bg-[#0F2544] text-white hover:bg-[#1a3a6b]"
              : "bg-slate-300 text-slate-500 cursor-not-allowed shadow-none"
          )}
        >
          Continuer
          <ArrowRight className="w-6 h-6" />
        </button>
      </div>

      {/* Footer Disclaimer */}
      <div className="w-full max-w-4xl border-t border-slate-200 pt-10 px-4">
        <p className="text-slate-400 text-sm text-center leading-relaxed">
          RetroAide est un outil d'information pédagogique. Les résultats fournis sont des estimations basées sur les données saisies et la législation en vigueur. Ils ne remplacent pas le relevé de carrière officiel de vos caisses de retraite.
        </p>
      </div>
    </div>
  );
};

export default OnboardingStep1;

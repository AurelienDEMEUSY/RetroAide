import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Building2, HardHat, Scale, Tractor, ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const OnboardingStep2 = () => {
  const navigate = useNavigate();
  const [professionalStatuses, setProfessionalStatuses] = useState([]);
  const [careerStartAge, setCareerStartAge] = useState('');
  const [careerBreaks, setCareerBreaks] = useState([]);

  const statusOptions = [
    { id: 'salarie_prive', label: 'Salarié privé', icon: Briefcase },
    { id: 'fonctionnaire', label: 'Fonctionnaire', icon: Building2 },
    { id: 'independant', label: 'Indépendant / Artisan', icon: HardHat },
    { id: 'liberale', label: 'Profession libérale', icon: Scale },
    { id: 'agriculteur', label: 'Agriculteur', icon: Tractor },
  ];

  const breakOptions = [
    { id: 'chomage', label: 'Chômage prolongé' },
    { id: 'maladie', label: 'Maladie longue durée' },
    { id: 'invalidite', label: 'Invalidité' },
    { id: 'etranger', label: 'Travail à l\'étranger' },
    { id: 'parental', label: 'Congé parental' },
  ];

  const toggleStatus = (id) => {
    setProfessionalStatuses(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleBreak = (id) => {
    setCareerBreaks(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const canProceed = professionalStatuses.length > 0 && careerStartAge;

  const handleNext = () => {
    const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
    localStorage.setItem('retroaide_onboarding', JSON.stringify({ 
      ...data, 
      professionalStatuses, 
      careerStartAge, 
      careerBreaks 
    }));
    navigate('/onboarding/3');
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] font-sans text-slate-900 flex flex-col">
      {/* Header */}
      <header className="px-6 py-5 flex justify-between items-center bg-white border-b border-slate-100">
        <h1 className="text-[22px] font-extrabold text-[#0f172a] tracking-tight cursor-pointer" onClick={() => navigate('/')}>RetroAide</h1>
      </header>

      <main className="flex-grow flex flex-col items-center px-4 pt-10 pb-20">
        <div className="w-full max-w-3xl">
          {/* Progress Bar */}
          <div className="mb-10 px-2">
            <div className="flex justify-between items-end mb-3">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">ÉTAPE 2 SUR 4</span>
              <span className="text-[15px] font-extrabold text-[#0f172a]">50%</span>
            </div>
            <div className="w-full h-[6px] bg-slate-200 rounded-full overflow-hidden">
              <div className="w-1/2 h-full bg-[#93e1b4] rounded-full" />
            </div>
          </div>

          <div className="mb-10 text-center sm:text-left px-2">
            <h2 className="text-[34px] font-extrabold text-[#0f172a] leading-[1.1] tracking-tight mb-4">
              Votre Parcours Professionnel
            </h2>
            <p className="text-slate-500 text-lg sm:text-lg max-w-xl leading-relaxed">
              La retraite en France fonctionne par caisses. Dites-nous à quels régimes vous avez pu cotiser.
            </p>
          </div>

          {/* Main Card */}
          <div className="bg-[#f1f5f9]/50 rounded-[2rem] p-6 sm:p-10 shadow-sm border border-slate-100/50 mb-8 backdrop-blur-sm space-y-12">
            
            {/* Status Options */}
            <div>
              <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
                Vos statuts professionnels au cours de votre vie (Plusieurs choix possibles)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {statusOptions.map((option) => {
                  const Icon = option.icon;
                  const isSelected = professionalStatuses.includes(option.id);
                  
                  return (
                    <button
                      key={option.id}
                      onClick={() => toggleStatus(option.id)}
                      className={cn(
                        "flex items-center justify-between p-4 rounded-2xl border-2 transition-all duration-300 text-left",
                        isSelected 
                          ? "border-[#0f172a] bg-white ring-4 ring-slate-100/50" 
                          : "border-transparent bg-white shadow-sm hover:border-slate-200"
                      )}
                    >
                      <div className="flex items-center gap-4">
                        <div className={cn(
                          "w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300",
                          isSelected ? "bg-[#0f2444] text-white" : "bg-[#daedfd] text-[#3b82f6]"
                        )}>
                          <Icon size={20} strokeWidth={2.5} />
                        </div>
                        <span className={cn(
                          "font-bold text-[15px] transition-colors leading-tight",
                          isSelected ? "text-[#0f172a]" : "text-slate-700"
                        )}>
                          {option.label}
                        </span>
                      </div>
                      {isSelected && (
                        <CheckCircle2 size={20} className="text-[#0f2444] shrink-0 ml-2" strokeWidth={3} />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Career Start Age */}
            <div>
              <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
                Âge de début de votre vie active
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  { id: 'avant_16', label: 'Avant 16 ans' },
                  { id: 'avant_18', label: 'Avant 18 ans' },
                  { id: 'avant_20', label: 'Avant 20 ans' },
                  { id: 'avant_21', label: 'Avant 21 ans' },
                  { id: 'apres_21', label: '21 ans ou plus' },
                ].map(opt => (
                  <button
                    key={opt.id}
                    onClick={() => setCareerStartAge(opt.id)}
                    className={cn(
                      "p-4 rounded-xl border-2 font-bold text-center transition-all",
                      careerStartAge === opt.id
                        ? "border-[#0f172a] bg-white text-[#0f172a]"
                        : "border-transparent bg-white text-slate-600 shadow-sm hover:border-slate-200"
                    )}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Career Breaks */}
            <div>
              <h3 className="text-xl font-bold text-[#0f172a] mb-5 tracking-tight">
                Accidents ou pauses de carrière (Optionnel)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {breakOptions.map((option) => {
                  const isSelected = careerBreaks.includes(option.id);
                  return (
                    <button
                      key={option.id}
                      onClick={() => toggleBreak(option.id)}
                      className={cn(
                        "flex items-center gap-3 p-4 rounded-xl border-2 transition-all duration-200 text-left",
                        isSelected 
                          ? "border-[#0f172a] bg-white text-[#0f172a]" 
                          : "border-transparent bg-white text-slate-600 shadow-sm hover:border-slate-200"
                      )}
                    >
                      <div className={cn(
                        "w-5 h-5 rounded border-2 flex items-center justify-center shrink-0",
                        isSelected ? "bg-[#0f172a] border-[#0f172a]" : "border-slate-300"
                      )}>
                        {isSelected && <CheckCircle2 size={14} className="text-white" />}
                      </div>
                      <span className="font-bold text-[15px]">{option.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Navigation Buttons */}
            <div className="pt-6 border-t border-slate-200/60 flex flex-col md:flex-row items-center justify-between gap-6">
              <button 
                onClick={() => navigate('/onboarding/1')}
                className="flex items-center gap-2 text-slate-500 font-bold text-[16px] hover:text-slate-900 transition-colors"
              >
                <ArrowLeft size={18} strokeWidth={3} />
                Retour
              </button>
              <button 
                disabled={!canProceed}
                onClick={handleNext}
                className={cn(
                  "w-full md:w-auto flex items-center justify-center gap-3 px-12 py-5 rounded-2xl font-bold text-[18px] transition-all duration-300 shadow-[0_10px_30px_rgba(15,37,68,0.15)]",
                  canProceed 
                    ? "bg-[#0f2444] text-white hover:bg-[#1e3a6a] hover:scale-[1.02] active:scale-[0.98]" 
                    : "bg-slate-300 text-slate-500 cursor-not-allowed shadow-none"
                )}
              >
                Continuer
                <ArrowRight size={20} strokeWidth={2.5} />
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-16 px-6 flex flex-col items-center border-t border-slate-100">
        <h2 className="text-[24px] font-black text-[#0f172a] mb-8 tracking-tighter">RetroAide</h2>
        <div className="max-w-xl text-center mb-10">
          <p className="text-slate-400 text-[13px] font-medium leading-relaxed">
            Vos données sont sécurisées et cryptées selon les standards bancaires. Elles ne sont utilisées que pour personnaliser votre estimation.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default OnboardingStep2;

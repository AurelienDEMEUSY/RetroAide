import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Briefcase, 
  Building2, 
  MoreHorizontal, 
  CheckCircle2, 
  ChevronRight, 
  ArrowLeft, 
  ArrowRight,
  ThumbsUp,
  Ban,
  Headphones
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const OnboardingStep2 = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState('fonctionnaire');
  const [isActive, setIsActive] = useState(null);

  const statusOptions = [
    { id: 'salarie', label: 'Salarié privé', icon: Briefcase },
    { id: 'fonctionnaire', label: 'Fonctionnaire', icon: Building2 },
    { id: 'autre', label: 'Autre', icon: MoreHorizontal },
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc] font-sans text-slate-900 flex flex-col">
      {/* Header */}
      <header className="px-6 py-5 flex justify-between items-center bg-white border-b border-slate-100">
        <h1 className="text-[22px] font-extrabold text-[#0f172a] tracking-tight cursor-pointer" onClick={() => navigate('/')}>RetroAide</h1>
      </header>

      <main className="flex-grow flex flex-col items-center px-4 pt-10 pb-20">
        <div className="w-full max-w-[640px]">
          {/* Progress Bar */}
          <div className="mb-10 px-2">
            <div className="flex justify-between items-end mb-3">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                ÉTAPE 2 SUR 3
              </span>
              <span className="text-[15px] font-extrabold text-[#0f172a]">66%</span>
            </div>
            <div className="w-full h-[6px] bg-slate-200 rounded-full overflow-hidden">
              <div className="w-2/3 h-full bg-[#93e1b4] rounded-full" />
            </div>
          </div>

          {/* Main Card */}
          <div className="bg-[#f1f5f9]/50 rounded-[40px] p-8 md:p-14 shadow-sm border border-slate-100/50 mb-8 backdrop-blur-sm">
            <h2 className="text-[34px] font-extrabold text-[#0f172a] mb-10 leading-[1.1] tracking-tight">
              Quel est votre statut professionnel ?
            </h2>

            {/* Status Options */}
            <div className="space-y-4 mb-12">
              {statusOptions.map((option) => {
                const Icon = option.icon;
                const isSelected = status === option.id;
                
                return (
                  <button
                    key={option.id}
                    onClick={() => setStatus(option.id)}
                    className={cn(
                      "w-full flex items-center justify-between p-5 rounded-2xl border-2 transition-all duration-300 group",
                      isSelected 
                        ? "border-[#0f172a] bg-white ring-4 ring-slate-100/50" 
                        : "border-transparent bg-white shadow-sm hover:border-slate-200"
                    )}
                  >
                    <div className="flex items-center gap-5">
                      <div className={cn(
                        "w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300",
                        isSelected ? "bg-[#0f2444] text-white" : "bg-[#daedfd] text-[#3b82f6]"
                      )}>
                        <Icon size={22} strokeWidth={2.5} />
                      </div>
                      <span className={cn(
                        "font-bold text-[18px] transition-colors",
                        isSelected ? "text-[#0f172a]" : "text-slate-700"
                      )}>
                        {option.label}
                      </span>
                    </div>
                    {isSelected ? (
                      <div className="w-6 h-6 rounded-full bg-[#0f2444] flex items-center justify-center">
                        <CheckCircle2 size={14} className="text-white" strokeWidth={3} />
                      </div>
                    ) : (
                      <ChevronRight className="text-slate-300 group-hover:text-slate-400" size={24} strokeWidth={2} />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Sub Question */}
            <div className="mb-6">
              <h3 className="text-[20px] font-bold text-[#0f172a] mb-6 tracking-tight">
                Êtes-vous actuellement en activité ?
              </h3>
              <div className="grid grid-cols-2 gap-5">
                <button
                  onClick={() => setIsActive(true)}
                  className={cn(
                    "flex items-center justify-center gap-3 py-4 rounded-2xl border-2 transition-all duration-300 font-bold text-[16px]",
                    isActive === true
                      ? "border-[#0f172a] bg-white text-[#0f172a] ring-4 ring-slate-100/50"
                      : "border-transparent bg-white text-slate-600 shadow-sm hover:border-slate-200"
                  )}
                >
                  <ThumbsUp size={20} strokeWidth={2.5} />
                  Oui
                </button>
                <button
                  onClick={() => setIsActive(false)}
                  className={cn(
                    "flex items-center justify-center gap-3 py-4 rounded-2xl border-2 transition-all duration-300 font-bold text-[16px]",
                    isActive === false
                      ? "border-[#0f172a] bg-white text-[#0f172a] ring-4 ring-slate-100/50"
                      : "border-transparent bg-white text-slate-600 shadow-sm hover:border-slate-200"
                  )}
                >
                  <Ban size={20} strokeWidth={2.5} />
                  Non
                </button>
              </div>
            </div>

            {/* Navigation Buttons */}
            <div className="mt-14 flex flex-col md:flex-row items-center justify-between gap-6">
              <button 
                onClick={() => navigate('/onboarding/1')}
                className="flex items-center gap-2 text-slate-500 font-bold text-[16px] hover:text-slate-900 transition-colors"
              >
                <ArrowLeft size={18} strokeWidth={3} />
                Retour
              </button>
              <button 
                disabled={isActive === null}
                onClick={() => {
                  const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
                  localStorage.setItem('retroaide_onboarding', JSON.stringify({ ...data, status, isActive }));
                  navigate('/onboarding/3');
                }}
                className={cn(
                  "w-full md:w-auto flex items-center justify-center gap-3 px-12 py-5 rounded-2xl font-bold text-[18px] transition-all duration-300 shadow-xl",
                  isActive !== null 
                    ? "bg-[#0f2444] text-white hover:bg-[#1e3a6a] hover:scale-[1.02]" 
                    : "bg-slate-300 text-slate-500 cursor-not-allowed"
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
            © 2026 RetroAide Financial Services. All rights reserved. Member SIPC. Vos
            données sont sécurisées et cryptées selon les standards bancaires les plus
            élevés.
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-x-10 gap-y-3">
          {['Politique de confidentialité', 'Conditions d\'utilisation', 'Sécurité'].map((link) => (
            <button key={link} className="text-slate-400 text-[13px] font-bold hover:text-slate-900 transition-colors">
              {link}
            </button>
          ))}
        </div>
      </footer>
    </div>
  );
};

export default OnboardingStep2;

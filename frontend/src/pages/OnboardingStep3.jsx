import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Landmark, HelpCircle, Check, User } from 'lucide-react';

const OnboardingStep3 = () => {
  const navigate = useNavigate();
  const [selectedSituations, setSelectedSituations] = useState([]);

  const toggleSituation = (id) => {
    setSelectedSituations((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const situations = [
    { id: 'children', label: "J'ai eu des enfants", tooltip: "Chaque enfant peut vous donner droit à des trimestres supplémentaires pour son éducation." },
    { id: 'unemployment', label: "J'ai eu des périodes de chômage", tooltip: "Les périodes de chômage indemnisé permettent de valider des trimestres." },
    { id: 'sick_leave', label: "J'ai eu des arrêts maladie longs (+ de 60 jours)", tooltip: "Un arrêt de travail de plus de 60 jours consécutifs valide 1 trimestre." },
    { id: 'military', label: "J'ai effectué mon service militaire", tooltip: "La période de service civique ou militaire compte dans votre durée d'assurance." },
  ];

  return (
    <div className="min-h-screen bg-slate-50/30 font-sans text-slate-900 flex flex-col">
      {/* Header */}
      <header className="px-6 py-4 flex justify-between items-center bg-white border-b border-transparent">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
          <Landmark className="w-5 h-5 text-slate-800" />
          <span className="font-bold text-xl tracking-tight">RetroAide</span>
        </div>
        <div className="flex items-center gap-6">
          <span className="font-semibold text-slate-900 text-sm sm:text-base">Étape 3 sur 3</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-12">
        {/* Progress Bar */}
        <div className="flex gap-2 mb-14 px-4 sm:px-0">
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
        </div>

        {/* Title Section */}
        <div className="mb-12 text-center sm:text-left">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-5">Situations Particulières</h1>
          <p className="text-slate-600 text-lg leading-relaxed max-w-2xl">
            Certaines étapes de votre vie influencent le calcul de votre retraite. 
            Sélectionnez celles qui vous concernent.
          </p>
        </div>

        {/* Situations List */}
        <div className="space-y-4 mb-12">
          {situations.map((item) => (
            <div
              key={item.id}
              onClick={() => toggleSituation(item.id)}
              className="group flex items-center justify-between p-6 bg-[#f8fafc] hover:bg-slate-100/80 rounded-xl cursor-pointer transition-all border border-transparent hover:border-slate-200"
            >
              <div className="flex items-center gap-5">
                <div 
                  className={`w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all ${
                    selectedSituations.includes(item.id) 
                      ? 'bg-slate-900 border-slate-900' 
                      : 'border-slate-300'
                  }`}
                >
                  <Check className={`w-4 h-4 transition-opacity ${selectedSituations.includes(item.id) ? 'text-white opacity-100' : 'text-slate-300 opacity-40'}`} />
                </div>
                <span className="font-medium text-[17px] text-slate-800">{item.label}</span>
              </div>
              <div className="relative flex items-center group/tooltip p-2 -m-2">
                <HelpCircle className="w-5 h-5 text-slate-400 cursor-help group-hover/tooltip:text-slate-600 transition-colors" />
                <div className="absolute right-0 bottom-full mb-2 hidden group-hover/tooltip:block w-48 sm:w-64 bg-[#0f172a] text-white text-[13px] rounded-xl p-3 shadow-xl z-20 font-normal leading-relaxed cursor-default pointer-events-none origin-bottom animate-in fade-in zoom-in-95 duration-200">
                  {item.tooltip}
                  {/* Arrow pointing down */}
                  <div className="absolute -bottom-1.5 right-3 w-3 h-3 bg-[#0f172a] rotate-45 rounded-sm"></div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Action Button */}
        <div className="px-2 sm:px-0 flex gap-4">
          <button
            onClick={() => navigate('/onboarding/2')}
            className="w-1/3 py-5 bg-white border-2 border-[#1e293b] text-[#1e293b] text-lg font-bold rounded-xl shadow-sm hover:bg-slate-50 transition-all mb-16"
          >
            Retour
          </button>
          <button
            onClick={() => {
              const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
              localStorage.setItem('retroaide_onboarding', JSON.stringify({ ...data, situations: selectedSituations }));
              navigate('/dashboard');
            }}
            className="w-2/3 py-5 bg-[#1e293b] text-white text-lg font-bold rounded-xl shadow-xl hover:bg-[#0f172a] hover:scale-[1.01] active:scale-[0.99] transition-all mb-16"
          >
            Analyser ma situation
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-16 px-6 bg-slate-50 mt-auto border-t border-slate-100">
        <div className="max-w-6xl mx-auto flex flex-col items-center">
          <div className="flex items-center gap-2 mb-8 cursor-pointer" onClick={() => navigate('/')}>
            <Landmark className="w-6 h-6 text-slate-800" />
            <span className="font-bold text-2xl tracking-tight text-blue-900">RetroAide</span>
          </div>
          <div className="flex flex-wrap justify-center gap-x-10 gap-y-4 mb-8 text-[15px] font-medium text-slate-600/80">
            <a href="#" className="hover:text-blue-900 transition-colors">Politique de confidentialité</a>
            <a href="#" className="hover:text-blue-900 transition-colors">Conditions d'utilisation</a>
            <a href="#" className="hover:text-blue-900 transition-colors">Sécurité</a>
          </div>
          <div className="text-sm text-slate-400 font-medium text-center">
            © 2026 RetroAide Financial Services. All rights reserved. Member SIPC.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default OnboardingStep3;

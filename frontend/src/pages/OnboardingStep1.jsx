import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { HelpCircle, ArrowRight, Info } from 'lucide-react';

const OnboardingStep1 = () => {
  const navigate = useNavigate();
  const [birthYear, setBirthYear] = useState('');
  const [careerStartYear, setCareerStartYear] = useState('');

  const handleNext = () => {
    localStorage.setItem('retroaide_onboarding', JSON.stringify({ birthYear, careerStartYear }));
    navigate('/onboarding/2');
  };

  return (
    <div className="min-h-screen bg-[#F8F9FB] flex flex-col items-center py-6 px-4 font-sans text-[#0F2544]">
      {/* Top Header */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-12">
        <h1 className="text-2xl font-bold tracking-tight cursor-pointer" onClick={() => navigate('/')}>RetroAide</h1>
      </div>

      {/* Progress Section */}
      <div className="w-full max-w-3xl mb-16">
        <div className="flex justify-between items-center mb-4">
          <span className="text-slate-500 text-lg font-medium">Étape 1 sur 4</span>
          <span className="text-slate-900 text-lg font-bold">25% complété</span>
        </div>
        <div className="h-2.5 w-full bg-slate-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-[#9AE6B4] rounded-full transition-all duration-500 ease-out" 
            style={{ width: '25%' }} 
          />
        </div>
      </div>

      {/* Title Section */}
      <div className="w-full max-w-3xl mb-10 text-center sm:text-left">
        <h2 className="text-5xl font-extrabold mb-4">Votre Profil</h2>
        <p className="text-slate-500 text-xl max-w-xl leading-relaxed">
          Commençons par les bases pour établir votre simulateur personnalisé.
        </p>
      </div>

      {/* Form Cards Container */}
      <div className="w-full max-w-3xl space-y-6">
        {/* Birth Year Card */}
        <div className="bg-white rounded-[2rem] p-10 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-50">
          <h3 className="text-2xl font-bold mb-8">Quelle est votre année de naissance ?</h3>
          
          <input
            type="text"
            placeholder="Ex: 1975"
            value={birthYear}
            onChange={(e) => setBirthYear(e.target.value)}
            className="w-full p-6 bg-slate-100 rounded-2xl border-none text-xl focus:ring-2 focus:ring-[#0F2544] transition-all placeholder:text-slate-300"
          />
        </div>

        {/* Career Start Card */}
        <div className="bg-white rounded-[2rem] p-10 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-50">
          <h3 className="text-2xl font-bold mb-8">En quelle année avez-vous débuté votre carrière ?</h3>
          
          <input
            type="text"
            placeholder="Ex: 1994"
            value={careerStartYear}
            onChange={(e) => setCareerStartYear(e.target.value)}
            className="w-full p-6 bg-slate-100 rounded-2xl border-none text-xl mb-8 focus:ring-2 focus:ring-[#0F2544] transition-all placeholder:text-slate-300"
          />

          <div className="flex items-start gap-4 p-6 bg-[#E8F3F7] rounded-2xl">
            <div className="w-8 h-8 rounded-full bg-[#0F2544] flex items-center justify-center flex-shrink-0 mt-1">
              <Info className="w-5 h-5 text-white" />
            </div>
            <p className="text-[#0F2544] text-base leading-relaxed font-medium">
              Ces informations nous permettent de calculer votre âge légal de départ et d'estimer vos droits.
            </p>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="w-full max-w-3xl flex flex-col items-center mt-12 mb-16">
        <button
          onClick={handleNext}
          className="bg-[#0F2544] text-white px-12 py-5 rounded-2xl font-bold text-xl flex items-center gap-3 hover:bg-[#1a3a6b] transition-all shadow-[0_10px_30px_rgba(15,37,68,0.2)] active:scale-95"
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

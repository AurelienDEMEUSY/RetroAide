import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Landmark, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const OnboardingStep4 = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    villeSignature: '',
    montantEstime: '',
    nbTrimestresAvant20: '',
    paysEtranger: '',
    nbEnfants: '',
    nbMoisArmee: ''
  });
  
  const [needsChildren, setNeedsChildren] = useState(false);
  const [needsMilitary, setNeedsMilitary] = useState(false);

  useEffect(() => {
    const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
    if (data.situations) {
      setNeedsChildren(data.situations.includes('children'));
      setNeedsMilitary(data.situations.includes('military'));
    }
    // prefill if any
    if (data.fullName) {
      setFormData(prev => ({
        ...prev,
        fullName: data.fullName || '',
        villeSignature: data.villeSignature || '',
        montantEstime: data.montantEstime || '',
        nbTrimestresAvant20: data.nbTrimestresAvant20 || '',
        paysEtranger: data.paysEtranger || '',
        nbEnfants: data.nbEnfants || '',
        nbMoisArmee: data.nbMoisArmee || ''
      }));
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
    const situations = data.situations || [];
    
    if (formData.nbEnfants && parseInt(formData.nbEnfants, 10) > 0 && !situations.includes('children')) {
      situations.push('children');
    }
    if (formData.nbMoisArmee && parseInt(formData.nbMoisArmee, 10) > 0 && !situations.includes('military')) {
      situations.push('military');
    }

    localStorage.setItem('retroaide_onboarding', JSON.stringify({ 
      ...data, 
      ...formData,
      situations 
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
        <div className="flex items-center gap-6">
          <span className="font-semibold text-slate-900 text-sm sm:text-base">Étape 4 sur 4</span>
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
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-5">Dernières précisions</h1>
          <p className="text-slate-600 text-lg leading-relaxed max-w-2xl">
            Ces informations nous permettent de générer un rapport complet et personnalisé pour vous, et d'affiner nos calculs.
          </p>
        </div>

        {/* Form Container */}
        <div className="bg-white rounded-2xl p-6 sm:p-10 shadow-sm border border-slate-100 mb-12 space-y-8">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Nom complet</label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="Ex: Jean Dupont"
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Lieu (pour la signature)</label>
              <input
                type="text"
                name="villeSignature"
                value={formData.villeSignature}
                onChange={handleChange}
                placeholder="Ex: Paris"
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Montant estimé (en €) (Optionnel)</label>
              <input
                type="number"
                name="montantEstime"
                value={formData.montantEstime}
                onChange={handleChange}
                placeholder="Ex: 1500"
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Trimestres validés avant 20 ans</label>
              <input
                type="number"
                name="nbTrimestresAvant20"
                value={formData.nbTrimestresAvant20}
                onChange={handleChange}
                placeholder="Ex: 4"
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2">Périodes travaillées à l'étranger (Pays)</label>
            <input
              type="text"
              name="paysEtranger"
              value={formData.paysEtranger}
              onChange={handleChange}
              placeholder="Ex: Allemagne, Espagne..."
              className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
            />
          </div>

          <div className="pt-6 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">Nombre d'enfants (Optionnel)</label>
              <input
                type="number"
                name="nbEnfants"
                value={formData.nbEnfants}
                onChange={handleChange}
                placeholder="Ex: 2"
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
              />
            </div>
            {needsMilitary && (
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Mois de service militaire (Optionnel)</label>
                <input
                  type="number"
                  name="nbMoisArmee"
                  value={formData.nbMoisArmee}
                  onChange={handleChange}
                  placeholder="Ex: 12"
                  className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
                />
              </div>
            )}
          </div>
        </div>

        {/* Action Button */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            onClick={() => navigate('/onboarding/3')}
            className="w-full sm:w-auto flex items-center justify-center gap-2 py-4 px-8 bg-white border-2 border-slate-200 text-slate-600 text-lg font-bold rounded-xl shadow-sm hover:border-slate-300 transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
            Retour
          </button>
          <button
            onClick={handleSubmit}
            className="w-full sm:w-auto flex items-center justify-center gap-2 py-4 px-12 bg-[#0f172a] text-white text-lg font-bold rounded-xl shadow-xl hover:bg-[#1e293b] hover:-translate-y-0.5 transition-all"
          >
            Analyser ma situation
            <CheckCircle2 className="w-5 h-5 text-[#93e1b4]" />
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

export default OnboardingStep4;

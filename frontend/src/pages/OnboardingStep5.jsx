import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Landmark, ArrowLeft, CheckCircle2, PiggyBank, Settings, Building2, Receipt, BadgePercent } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const OnboardingStep5 = () => {
  const navigate = useNavigate();
  
  // State variables for PER fields
  const [perOrganisme, setPerOrganisme] = useState('');
  const [perVersementMensuel, setPerVersementMensuel] = useState('');
  const [perVersementPonctuel, setPerVersementPonctuel] = useState('');
  const [perGestionType, setPerGestionType] = useState('a_definir');
  const [perFormeSortie, setPerFormeSortie] = useState('a_definir');
  const [perOptionFiscale, setPerOptionFiscale] = useState('a_decider');
  const [perPlanEntreprise, setPerPlanEntreprise] = useState('je_ne_sais_pas');
  const [perAnciensContrats, setPerAnciensContrats] = useState('je_ne_sais_pas');

  useEffect(() => {
    // Load existing data if arriving via "Retour"
    const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
    if (data.perOrganisme) setPerOrganisme(data.perOrganisme);
    if (data.perVersementMensuel !== undefined) setPerVersementMensuel(data.perVersementMensuel);
    if (data.perVersementPonctuel !== undefined) setPerVersementPonctuel(data.perVersementPonctuel);
    if (data.perGestionType) setPerGestionType(data.perGestionType);
    if (data.perFormeSortie) setPerFormeSortie(data.perFormeSortie);
    if (data.perOptionFiscale) setPerOptionFiscale(data.perOptionFiscale);
    if (data.perPlanEntreprise) setPerPlanEntreprise(data.perPlanEntreprise);
    if (data.perAnciensContrats) setPerAnciensContrats(data.perAnciensContrats);
  }, []);

  const handleSubmit = () => {
    const data = JSON.parse(localStorage.getItem('retroaide_onboarding') || '{}');
    localStorage.setItem('retroaide_onboarding', JSON.stringify({ 
      ...data, 
      perOrganisme,
      perVersementMensuel: perVersementMensuel ? parseInt(perVersementMensuel, 10) : null,
      perVersementPonctuel: perVersementPonctuel ? parseInt(perVersementPonctuel, 10) : null,
      perGestionType,
      perFormeSortie,
      perOptionFiscale,
      perPlanEntreprise,
      perAnciensContrats
    }));
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50/30 font-sans text-slate-900 flex flex-col">
      <header className="px-6 py-4 flex justify-between items-center bg-white border-b border-transparent">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
          <Landmark className="w-5 h-5 text-slate-800" />
          <span className="font-bold text-xl tracking-tight">RetroAide</span>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-6 py-12">
        <div className="flex gap-2 mb-14 px-4 sm:px-0">
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#c2f3d6] rounded-full"></div>
          <div className="h-1.5 flex-1 bg-[#0f2444] rounded-full shadow-[0_0_10px_rgba(15,36,68,0.3)]"></div>
        </div>

        <div className="mb-12 text-center sm:text-left">
          <span className="text-sm font-bold text-slate-400 uppercase tracking-widest block mb-3">ÉTAPE 5 SUR 5</span>
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-5 tracking-tight">Projet Plan d'Épargne Retraite (PER)</h1>
          <p className="text-slate-600 text-lg leading-relaxed max-w-2xl">
            Aidez-nous à personnaliser votre projet (ou contrat pré-rempli). Si vous ne savez pas, laissez l'option sur "À définir".
          </p>
        </div>

        <div className="bg-white rounded-2xl p-6 sm:p-10 shadow-sm border border-slate-100 mb-12 space-y-12">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="flex items-center gap-2 text-sm font-bold text-slate-700 mb-2">
                <Building2 size={16} /> Organisme / Banque (Optionnel)
              </label>
              <input
                type="text"
                value={perOrganisme}
                onChange={(e) => setPerOrganisme(e.target.value)}
                placeholder="Ex: La Banque Postale, Lucya..."
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
              />
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm font-bold text-slate-700 mb-2">
                <PiggyBank size={16} /> Versement Mensuel (€)
              </label>
              <input
                type="number"
                value={perVersementMensuel}
                onChange={(e) => {
                  const v = parseInt(e.target.value, 10);
                  if (e.target.value === '' || (v >= 0 && v <= 50000)) setPerVersementMensuel(e.target.value);
                }}
                placeholder="Ex: 150"
                min="0" max="50000"
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-[#0f172a] outline-none transition-all placeholder:text-slate-400"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
            <div>
              <label className="flex items-center gap-2 text-sm font-bold text-slate-700 mb-2">
                <Settings size={16} /> Style de Gestion
              </label>
              <select
                value={perGestionType}
                onChange={(e) => setPerGestionType(e.target.value)}
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium focus:ring-2 focus:ring-[#0f172a] outline-none appearance-none"
              >
                <option value="a_definir">À définir</option>
                <option value="pilotee">Gestion Pilotée (défaut)</option>
                <option value="libre">Gestion Libre (expert)</option>
              </select>
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm font-bold text-slate-700 mb-2">
                <Receipt size={16} /> Forme de sortie envisagée
              </label>
              <select
                value={perFormeSortie}
                onChange={(e) => setPerFormeSortie(e.target.value)}
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium focus:ring-2 focus:ring-[#0f172a] outline-none appearance-none"
              >
                <option value="a_definir">À définir</option>
                <option value="capital">Le tout en Capital (cash)</option>
                <option value="rente">Rente mensuelle garantie</option>
                <option value="mixte">Mixte (Capital + Rente)</option>
              </select>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100">
            <label className="flex items-center gap-2 text-sm font-bold text-slate-700 mb-2">
              <BadgePercent size={16} /> Avantage Fiscal (Déductibilité)
            </label>
            <select
              value={perOptionFiscale}
              onChange={(e) => setPerOptionFiscale(e.target.value)}
              className="w-full sm:w-1/2 p-4 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium focus:ring-2 focus:ring-[#0f172a] outline-none appearance-none"
            >
              <option value="a_decider">Je dois en discuter avec un conseiller</option>
              <option value="deductible">Déductible de l'impôt actuel (TMI forte)</option>
              <option value="non_deductible">Non-déductible (Avantage pour la sortie)</option>
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">
                Existence d'un plan épargne via votre entreprise (PERECO / PERO) ?
              </label>
              <select
                value={perPlanEntreprise}
                onChange={(e) => setPerPlanEntreprise(e.target.value)}
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium focus:ring-2 focus:ring-[#0f172a] outline-none appearance-none"
              >
                <option value="je_ne_sais_pas">Je ne sais pas</option>
                <option value="oui">Oui, j'en ai un</option>
                <option value="non">Non, aucun support entreprise</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">
                Avez-vous d'anciens contrats à y transférer ? (Madelin, PERP, PERCO)
              </label>
              <select
                value={perAnciensContrats}
                onChange={(e) => setPerAnciensContrats(e.target.value)}
                className="w-full p-4 bg-slate-50 rounded-xl border border-slate-200 text-slate-800 font-medium focus:ring-2 focus:ring-[#0f172a] outline-none appearance-none"
              >
                <option value="je_ne_sais_pas">Je ne sais pas</option>
                <option value="oui">Oui</option>
                <option value="non">Non</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <button
            onClick={() => navigate('/onboarding/4')}
            className="w-full sm:w-auto flex items-center justify-center gap-2 py-5 px-8 bg-white border-2 border-slate-200 text-slate-600 text-lg font-bold rounded-xl shadow-sm hover:bg-slate-50 transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
            Retour
          </button>
          <button
            onClick={handleSubmit}
            className="w-full sm:w-auto flex items-center justify-center gap-2 py-5 px-12 text-white text-lg font-bold rounded-xl transition-all shadow-xl bg-[#0f2444] hover:bg-[#1e3a6a] hover:-translate-y-0.5"
          >
            Compiler mon contrat
            <CheckCircle2 className="w-5 h-5 text-[#93e1b4]" />
          </button>
        </div>
      </main>
    </div>
  );
};

export default OnboardingStep5;

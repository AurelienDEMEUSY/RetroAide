import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Landmark, 
  CheckCircle2, 
  Clock, 
  ExternalLink, 
  ArrowRight, 
  ShieldCheck, 
  HelpCircle,
  Database,
  Loader2
} from 'lucide-react';

const Dashboard = () => {
  const [simulationData, setSimulationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  const handleDownloadPdf = async () => {
    try {
      setIsGeneratingPdf(true);
      setError(null);
      
      const onboardingStr = localStorage.getItem('retroaide_onboarding');
      if (!onboardingStr) throw new Error("No onboarding data found");
      
      const onboarding = JSON.parse(onboardingStr);
      let statusPayload = 'autre';
      if (onboarding.status === 'salarie' || onboarding.status === 'salarie_prive') {
        statusPayload = 'salarie_prive';
      } else if (onboarding.status === 'fonctionnaire') {
        statusPayload = 'fonctionnaire';
      }
      
      const payload = {
        birth_year: parseInt(onboarding.birthYear || 1970, 10),
        career_start_year: parseInt(onboarding.careerStartYear || 1990, 10),
        status: statusPayload,
        currently_employed: onboarding.isActive === true,
        had_children: onboarding.situations?.includes('children') || false,
        had_unemployment: onboarding.situations?.includes('unemployment') || false,
        had_long_sick_leave: onboarding.situations?.includes('sick_leave') || false,
        had_military_service: onboarding.situations?.includes('military') || false,
        long_part_time_years: false
      };
      
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const reportRes = await fetch(`${apiUrl}/api/v1/analyze/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!reportRes.ok) throw new Error("Erreur génération rapport");
      const reportData = await reportRes.json();
      
      const pdfRes = await fetch(`${apiUrl}/api/v1/report/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportData)
      });
      if (!pdfRes.ok) throw new Error("Erreur génération PDF");
      
      const blob = await pdfRes.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "retroaide-rapport.pdf";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch(err) {
      console.error(err);
      setError("Erreur lors de la génération du PDF. " + err.message);
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const onboardingStr = localStorage.getItem('retroaide_onboarding');
        if (!onboardingStr) {
          throw new Error("No onboarding data found");
        }
        
        const onboarding = JSON.parse(onboardingStr);
        let statusPayload = 'autre';
        if (onboarding.status === 'salarie' || onboarding.status === 'salarie_prive') {
          statusPayload = 'salarie_prive';
        } else if (onboarding.status === 'fonctionnaire') {
          statusPayload = 'fonctionnaire';
        }
        
        const payload = {
          birth_year: parseInt(onboarding.birthYear || 1970, 10),
          career_start_year: parseInt(onboarding.careerStartYear || 1990, 10),
          status: statusPayload,
          currently_employed: onboarding.isActive === true,
          had_children: onboarding.situations?.includes('children') || false,
          had_unemployment: onboarding.situations?.includes('unemployment') || false,
          had_long_sick_leave: onboarding.situations?.includes('sick_leave') || false,
          had_military_service: onboarding.situations?.includes('military') || false,
          long_part_time_years: false
        };
        
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }
        
        const responseData = await response.json();
        
        setSimulationData({
          ageLegal: responseData.departure_age,
          trimestresValides: responseData.quarters_worked,
          trimestresRestants: responseData.quarters_remaining,
          trimestresRequis: responseData.quarters_worked + responseData.quarters_remaining,
          droitsOublies: (responseData.missing_quarters || []).map(mq => ({
            type: mq.period,
            description: mq.reason,
            action: mq.action,
            icon: 'HelpCircle',
            color: 'blue'
          })),
          isMocked: false
        });
        
      } catch (err) {
        console.error("Dashboard analysis error:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalysis();
  }, []);

  // Fallback defaults without API
  const data = simulationData || {
    ageLegal: 64,
    trimestresValides: 128,
    trimestresRequis: 172,
    trimestresRestants: 44,
    droitsOublies: [],
    isMocked: true
  };

  const trimestresPercent = Math.round((data.trimestresValides / data.trimestresRequis) * 100) || 0;

  if (loading && !simulationData) {
    return (
      <div className="min-h-screen bg-[#f3f4f6] font-sans text-slate-900 flex flex-col items-center justify-center">
        <Loader2 className="w-16 h-16 text-[#818cf8] animate-spin mb-6" />
        <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Analyse de votre carrière en cours...</h2>
        <p className="text-slate-500 mt-3 max-w-md text-center">Nos algorithmes croisent vos données <br/> avec la législation actuelle.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f3f4f6] font-sans text-slate-900">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white border-b border-gray-100">
        <Link to="/" className="flex items-center gap-2 text-lg md:text-xl font-bold text-[#0f172a] tracking-tight">
          <Landmark className="w-5 h-5 md:w-6 md:h-6 text-[#0f172a]" />
          <span>RetroAide</span>
        </Link>
        <div className="hidden md:flex items-center gap-12 text-sm font-medium text-slate-600">
          <Link to="/dashboard" className="relative py-2 text-slate-900 after:absolute after:bottom-0 after:left-0 after:w-full after:h-0.5 after:bg-slate-900">Plan</Link>
          <Link to="/glossary" className="hover:text-slate-900">Glossaire</Link>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
            Synthèse de votre <span className="text-[#818cf8]">Analyse</span>
          </h1>
          <p className="text-gray-600 text-lg max-w-2xl leading-relaxed">
            Voici le bilan actuel de votre carrière. Nos algorithmes ont identifié des opportunités pour optimiser votre date de départ.
          </p>
          {error && (
            <div className="mt-4 p-4 bg-orange-50 border border-orange-200 text-orange-700 rounded-xl text-sm max-w-2xl">
              <strong>Note:</strong> Impossible de contacter nos serveurs pour une analyse précise ({error}). Les données affichées ci-dessous sont un exemple standard.
            </div>
          )}
        </div>

        {/* Top Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Card 1: Age Legal */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between h-56">
            <div>
              <p className="text-[10px] font-bold tracking-[0.15em] text-slate-500 mb-6 antialiased">ÂGE LÉGAL DE DÉPART</p>
              <h2 className="text-5xl font-bold text-slate-900">{data.ageLegal} ans</h2>
            </div>
            <div className="flex items-center gap-2 text-green-600 font-medium text-sm">
              <CheckCircle2 className="w-5 h-5" />
              <span>{data.isMocked ? "Estimation (API Standard)" : "Calcul officiel certifié"}</span>
            </div>
          </div>

          {/* Card 2: Trimesters Validated */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between h-56">
            <div>
              <p className="text-[10px] font-bold tracking-[0.15em] text-slate-500 mb-6 antialiased uppercase">TRIMESTRES VALIDÉS</p>
              <h2 className="text-5xl font-bold text-slate-900">{data.trimestresValides} <span className="text-2xl text-gray-400 font-normal">/ {data.trimestresRequis}</span></h2>
            </div>
            <div className="w-full bg-gray-100 h-2.5 rounded-full mt-4 overflow-hidden">
               <div className="bg-[#a4dcb4] h-full rounded-full transition-all duration-1000" style={{ width: `${trimestresPercent}%` }}></div>
            </div>
          </div>

          {/* Card 3: Trimesters Remaining */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between h-56">
            <div>
              <p className="text-[10px] font-bold tracking-[0.15em] text-slate-500 mb-6 antialiased uppercase">TRIMESTRES RESTANTS</p>
              <h2 className="text-5xl font-bold text-slate-900">{data.trimestresRestants}</h2>
            </div>
            <div className="flex items-center gap-2 text-gray-500 font-medium text-sm">
              <Clock className="w-5 h-5" />
              <span>Parcours classique</span>
            </div>
          </div>
        </div>

        {/* Section Potential Rights */}
        <div className="bg-[#eaedef] rounded-3xl p-6 mb-12">
           <div className="flex flex-col md:flex-row items-start md:items-center gap-4 mb-8 pl-4 pt-2">
              <div className="p-3 bg-slate-900 rounded-xl">
                 <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900">Droits potentiellement oubliés</h3>
                <p className="text-sm text-gray-600">Analyse IA basée sur votre historique déclaratif</p>
              </div>
           </div>

           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.droitsOublies.length > 0 ? data.droitsOublies.map((droit, index) => {
                const colorClasses = droit.color === 'green' ? 'bg-green-50 text-green-500' 
                                   : droit.color === 'blue' ? 'bg-blue-50 text-blue-400' 
                                   : 'bg-gray-50 text-gray-400';
                return (
                  <div key={index} className="bg-white p-8 rounded-2xl shadow-sm flex flex-col">
                    <div className="mb-4 flex-1">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${colorClasses}`}>
                          {droit.icon === 'Clock' ? <Clock className="w-6 h-6" /> : <HelpCircle className="w-6 h-6" />}
                        </div>
                        <h4 className="text-lg font-bold text-slate-900 mb-2">{droit.type}</h4>
                        <p className="text-sm text-gray-500 leading-relaxed mb-6">
                          {droit.description}
                        </p>
                    </div>
                    <button className="flex items-center gap-2 text-sm font-bold text-slate-900 hover:opacity-70 mt-auto justify-start">
                        {droit.action} <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                );
              }) : (
                <div className="col-span-1 md:col-span-2 text-center py-8 text-gray-500">
                  Aucun droit oublié détecté basé sur vos réponses actuelles.
                </div>
              )}
           </div>
        </div>

        {/* Final CTA Area */}
        <div className="flex flex-col items-center justify-center mb-24 text-center">
          <button 
            onClick={handleDownloadPdf}
            disabled={isGeneratingPdf}
            className="w-full md:w-auto justify-center bg-[#1e3a5f] text-white px-8 py-4 rounded-xl font-bold flex items-center gap-3 text-lg hover:bg-slate-800 transition-colors mb-4 disabled:bg-slate-400"
          >
            {isGeneratingPdf ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Génération en cours...</>
            ) : (
              <>Télécharger mon plan d'action PDF <ArrowRight className="w-5 h-5" /></>
            )}
          </button>
          
          <div className="bg-white border border-gray-100 rounded-xl px-4 md:px-6 py-3 flex items-center justify-center gap-2 md:gap-3 shadow-sm mx-auto">
            <ShieldCheck className="w-4 h-4 md:w-5 md:h-5 text-green-500 flex-shrink-0" />
            <span className="text-xs md:text-sm font-medium text-gray-600">Données protégées par cryptage bancaire (AES-256)</span>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-50 border-t border-gray-200 py-12 md:py-16 px-4 md:px-8 flex flex-col items-center">
        <h2 className="text-lg md:text-xl font-bold text-slate-900 mb-4 md:mb-2 text-center">RetroAide Financial Services</h2>
        <div className="flex flex-wrap justify-center gap-4 md:gap-6 text-sm text-gray-500 mb-6 md:mb-8 text-center px-4">
          <a href="#" className="hover:text-slate-900">Privacy Policy</a>
          <a href="#" className="hover:text-slate-900">Terms of Service</a>
          <a href="#" className="hover:text-slate-900">Accessibility Statement</a>
          <a href="#" className="hover:text-slate-900">Legal Disclosures</a>
        </div>
        <p className="text-xs md:text-sm text-gray-400 text-center px-4">
          © 2026 RetroAide Financial Services. All rights reserved. Member SIPC.
        </p>
      </footer>
    </div>
  );
};

export default Dashboard;

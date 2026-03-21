import React, { useState } from 'react';
import { Search, User, Calendar, CheckCircle, TrendingDown, Building2, FileText, Plus, Headphones, Landmark, Loader2 } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';

const Glossary = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;
    
    try {
      setIsSearching(true);
      setError(null);
      setSearchResult(null);
      
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/glossary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ term: searchTerm })
      });
      
      if (!response.ok) {
        throw new Error(`Erreur serveur: ${response.status}`);
      }
      
      const data = await response.json();
      setSearchResult(data);
    } catch (err) {
      console.error(err);
      setError("Impossible de charger la définition pour ce terme.");
    } finally {
      setIsSearching(false);
    }
  };

  const terms = [
    {
      title: "Trimestre",
      description: "L'unité de base pour calculer votre retraite. Il correspond à une durée d'assurance validée au cours de votre vie professionnelle.",
      icon: <Calendar className="w-6 h-6 text-blue-600" />,
      bgColor: "bg-blue-50"
    },
    {
      title: "Taux plein",
      description: "Le montant maximum de votre pension sans réduction. Il est atteint quand vous avez validé le nombre requis de trimestres ou atteint l'âge limite.",
      icon: <CheckCircle className="w-6 h-6 text-green-600" />,
      bgColor: "bg-green-50"
    },
    {
      title: "Décote",
      description: "Une réduction appliquée si vous partez avant d'avoir tous vos trimestres. Cela réduit de façon permanente le montant de votre pension annuelle.",
      icon: <TrendingDown className="w-6 h-6 text-rose-600" />,
      bgColor: "bg-rose-50"
    },
    {
      title: "Agirc-Arrco",
      description: "L'organisme qui gère votre retraite complémentaire de salarié. Vos cotisations y sont transformées en points cumulés tout au long de votre carrière.",
      icon: <Building2 className="w-6 h-6 text-indigo-600" />,
      bgColor: "bg-indigo-50"
    },
    {
      title: "Relevé de carrière (RIS)",
      description: "Le document qui récapitule toute votre activité. Il permet de vérifier que tous vos jobs et périodes d'arrêt ont bien été comptabilisés.",
      icon: <FileText className="w-6 h-6 text-cyan-600" />,
      bgColor: "bg-cyan-50"
    }
  ];

  return (
    <div className="min-h-screen bg-white font-sans text-slate-900 pb-10">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-4 bg-white border-b border-gray-100 max-w-7xl mx-auto w-full">
        <Link to="/" className="flex items-center gap-2 text-lg md:text-xl font-bold text-[#0f172a] tracking-tight">
          <Landmark className="w-5 h-5 md:w-6 md:h-6 text-[#0f172a]" />
          <span>RetroAide</span>
        </Link>
        <div className="hidden md:flex items-center gap-12 text-sm font-medium text-slate-600">
          <Link to="/dashboard" className="hover:text-slate-900">Plan</Link>
          <Link to="/glossary" className="relative py-2 text-slate-900 after:absolute after:bottom-0 after:left-0 after:w-full after:h-0.5 after:bg-slate-900">Glossaire</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-12 md:py-20 flex flex-col md:flex-row items-center gap-12 w-full">
        <div className="flex-1 space-y-6 md:pr-12 text-center md:text-left">
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-indigo-950 leading-[1.1]">Glossaire Administratif</h2>
          <p className="text-lg text-gray-500 max-w-lg leading-relaxed mx-auto md:mx-0">
            Retrouvez ici les définitions simples des termes de la retraite. Nous décryptons pour vous le jargon administratif pour une transition sereine.
          </p>
          <form onSubmit={handleSearch} className="mt-8 flex items-center max-w-lg mx-auto md:mx-0 relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-11 pr-32 py-4 bg-white border border-gray-200 rounded-2xl text-base placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm"
              placeholder="Ex: Carrière longue, Minimum contributif..."
            />
            <button
              type="submit"
              disabled={isSearching || !searchTerm.trim()}
              className="absolute inset-y-2 right-2 flex items-center justify-center px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-medium rounded-xl transition-colors"
            >
              {isSearching ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Chercher'}
            </button>
          </form>
          {error && <p className="text-rose-500 text-sm mt-2">{error}</p>}
        </div>
        <div className="flex-1 w-full max-w-lg">
          <div className="relative rounded-[2rem] md:rounded-[2.5rem] overflow-hidden shadow-2xl md:rotate-2 hover:rotate-0 transition-transform duration-500">
            <img 
              src="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&q=80&w=1000" 
              alt="Person writing notes" 
              className="w-full h-[300px] md:h-[450px] object-cover"
            />
          </div>
        </div>
      </section>

      {/* Search Result */}
      {searchResult && (
        <section className="max-w-7xl mx-auto px-6 pb-6 w-full">
          <div className="bg-indigo-50 border border-indigo-100 rounded-[2rem] p-8 shadow-sm">
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-indigo-600 w-12 h-12 rounded-2xl flex items-center justify-center shadow-md">
                <Search className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 capitalize">{searchTerm}</h3>
            </div>
            <p className="text-gray-700 leading-relaxed text-lg whitespace-pre-wrap">
              {searchResult.explanation}
            </p>
          </div>
        </section>
      )}

      {/* Glossary Grid */}
      <section className="max-w-7xl mx-auto px-6 py-12 md:py-16 w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {terms.map((term, index) => (
            <div key={index} className="bg-white p-8 md:p-10 rounded-[2rem] md:rounded-[2.5rem] border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_40px_rgb(0,0,0,0.08)] transition-all flex flex-col gap-5 md:gap-6">
              <div className={`${term.bgColor} w-12 h-12 md:w-14 md:h-14 rounded-2xl flex items-center justify-center`}>
                {term.icon}
              </div>
              <div className="space-y-3 md:space-y-4">
                <h3 className="text-xl md:text-2xl font-bold text-slate-900">{term.title}</h3>
                <p className="text-gray-500 leading-relaxed text-sm md:text-[0.95rem]">
                  {term.description}
                </p>
              </div>
            </div>
          ))}
          
          {/* Placeholder Card */}
          <div className="bg-gray-50/50 p-8 md:p-10 rounded-[2rem] md:rounded-[2.5rem] border-2 border-dashed border-gray-200 flex flex-col items-center justify-center gap-4 text-center">
            <div className="bg-gray-300 w-10 h-10 rounded-full flex items-center justify-center">
              <Plus className="w-6 h-6 text-white" />
            </div>
            <p className="text-gray-400 max-w-[200px] text-xs md:text-sm font-semibold">
              D'autres termes arrivent bientôt pour vous aider.
            </p>
          </div>
        </div>
      </section>

      {/* Footer Info / Disclaimer */}
      <footer className="max-w-7xl mx-auto px-6 w-full">
        <div className="bg-gray-50 rounded-2xl md:rounded-3xl p-6 md:p-10 border border-gray-100">
          <p className="text-center text-xs md:text-sm text-gray-500 max-w-4xl mx-auto leading-relaxed">
            <span className="font-bold text-gray-700">Note importante :</span> RetroAide est un outil d'information pédagogique. Bien que nous nous efforcions de fournir les informations les plus précises possibles, les règles de retraite sont complexes et sujettes à changement. Consultez toujours vos caisses de retraite officielles pour vos démarches définitives.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Glossary;

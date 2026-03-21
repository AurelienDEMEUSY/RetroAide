import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, Clock, Shield, Headphones, Landmark, Scale, CheckCircle2 } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate('/onboarding/1');
  };

  return (
    <div className="min-h-screen bg-[#f8f9fa] font-sans text-slate-900 pb-20">
      {/* Header */}
      <header className="flex justify-between items-center px-4 md:px-8 py-4 md:py-6 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
          <Landmark className="w-5 h-5 md:w-6 md:h-6 text-[#0f172a]" />
          <span className="text-lg md:text-xl font-bold text-[#0f172a] tracking-tight">RetroAide</span>
        </div>
        <div className="flex gap-6 items-center">
          <button onClick={() => navigate('/glossary')} className="text-xs md:text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
            Glossaire
          </button>
          <button className="text-xs md:text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
            Get Help
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 md:px-8 pt-8 md:pt-12">
        {/* Hero Section */}
        <section className="flex flex-col lg:flex-row gap-10 lg:gap-16 items-start mb-16 lg:mb-24">
          <div className="relative w-full lg:w-1/2">
            <div className="rounded-2xl md:rounded-3xl overflow-hidden shadow-2xl">
              <img 
                src="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&q=80&w=800" 
                alt="Retirement planning" 
                className="w-full h-[280px] md:h-[450px] object-cover"
              />
            </div>
            {/* Overlay Badge */}
            <div className="absolute -bottom-4 md:-bottom-6 -right-2 md:-right-6 bg-white p-3 md:p-4 rounded-xl md:rounded-2xl shadow-xl flex items-center gap-2 md:gap-3 border border-slate-100 max-w-[180px] md:max-w-[200px]">
              <div className="bg-green-100 p-1.5 md:p-2 rounded-lg text-green-600">
                <CheckCircle2 className="w-4 h-4 md:w-5 md:h-5" />
              </div>
              <div>
                <p className="text-[10px] md:text-xs font-bold text-slate-800">Sérénité Garantie</p>
                <p className="text-[8px] md:text-[10px] text-slate-500">Accompagnement expert</p>
              </div>
            </div>
          </div>

          <div className="w-full lg:w-1/2 pt-2 md:pt-4">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-[#0f172a] mb-4 md:mb-8 leading-[1.1] md:leading-[1.1]">
              Préparez demain avec clarté.
            </h1>
            <p className="text-lg md:text-xl text-slate-600 mb-4 md:mb-6 leading-relaxed">
              Comme Martine, 62 ans, qui souhaitait faire le point sur ses trimestres avant de prendre sa décision, RetroAide vous guide pas à pas.
            </p>
            <p className="text-base md:text-lg text-slate-500 italic mb-8 md:mb-10 leading-relaxed font-light border-l-4 border-slate-200 pl-4 md:border-none md:pl-0">
              "J'avais besoin d'une vision simple pour mes projets futurs. RetroAide m'a redonné confiance."
            </p>
            <button 
              onClick={handleStart}
              className="w-full md:w-auto bg-[#0f172a] text-white px-8 md:px-10 py-3.5 md:py-4 rounded-xl font-bold text-base md:text-lg hover:bg-slate-800 transition-all shadow-lg hover:shadow-xl active:scale-[0.98]"
            >
              Commencer mon bilan
            </button>
          </div>
        </section>

        {/* Feature Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6 mb-16 lg:mb-24">
          <div className="bg-white/50 backdrop-blur-sm p-6 md:p-8 rounded-[1.5rem] md:rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="bg-indigo-50 w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center mb-4 md:mb-6">
              <Eye className="w-5 h-5 md:w-6 md:h-6 text-indigo-600" />
            </div>
            <h3 className="text-lg md:text-xl font-bold text-slate-900 mb-2 md:mb-4">Transparence</h3>
            <p className="text-sm md:text-base text-slate-600 leading-relaxed">
              Comprenez chaque détail de votre future pension sans jargon technique.
            </p>
          </div>

          <div className="bg-white/50 backdrop-blur-sm p-6 md:p-8 rounded-[1.5rem] md:rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="bg-blue-50 w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center mb-4 md:mb-6">
              <Clock className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
            </div>
            <h3 className="text-lg md:text-xl font-bold text-slate-900 mb-2 md:mb-4">Rapidité</h3>
            <p className="text-sm md:text-base text-slate-600 leading-relaxed">
              Obtenez votre simulation complète en moins de 10 minutes chrono.
            </p>
          </div>

          <div className="bg-white/50 backdrop-blur-sm p-6 md:p-8 rounded-[1.5rem] md:rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="bg-cyan-50 w-10 h-10 md:w-12 md:h-12 rounded-xl flex items-center justify-center mb-4 md:mb-6">
              <Shield className="w-5 h-5 md:w-6 md:h-6 text-cyan-600" />
            </div>
            <h3 className="text-lg md:text-xl font-bold text-slate-900 mb-2 md:mb-4">Sécurité</h3>
            <p className="text-sm md:text-base text-slate-600 leading-relaxed">
              Vos données sont chiffrées et protégées selon les normes bancaires.
            </p>
          </div>
        </section>

        {/* Legal Mention Section */}
        <section className="bg-slate-100/80 rounded-[1.5rem] md:rounded-[2.5rem] p-6 md:p-12 mb-16 lg:mb-24">
          <div className="flex items-center gap-3 md:gap-4 mb-6 md:mb-8">
            <div className="bg-slate-200 p-2 md:p-3 rounded-lg md:rounded-xl">
              <Scale className="w-5 h-5 md:w-6 md:h-6 text-slate-600" />
            </div>
            <h2 className="text-xl md:text-2xl font-bold text-slate-900">Mention Légale</h2>
          </div>
          <div className="bg-white p-6 md:p-10 rounded-2xl md:rounded-3xl shadow-sm">
            <p className="text-slate-700 leading-relaxed text-sm md:text-lg text-left md:text-left">
              RetroAide est un outil d'information pédagogique. Les résultats sont des estimations basées sur votre profil et ne constituent pas un avis juridique. Pour toute décision officielle, consultez votre caisse de retraite ou un conseiller agréé.
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 pt-10 md:pt-16 pb-12 w-full bg-white">
        <div className="max-w-7xl mx-auto px-6 md:px-8 flex flex-col items-center">
          <h2 className="text-lg md:text-xl font-bold text-blue-900 mb-6 md:mb-8">RetroAide</h2>
          <div className="flex flex-wrap justify-center gap-x-6 gap-y-3 md:gap-x-12 md:gap-y-4 mb-8 md:mb-10">
            <a href="#" className="text-xs md:text-sm text-slate-500 hover:text-slate-900">Privacy Policy</a>
            <a href="#" className="text-xs md:text-sm text-slate-500 hover:text-slate-900">Terms of Service</a>
            <a href="#" className="text-xs md:text-sm text-slate-500 hover:text-slate-900">Accessibility Statement</a>
            <a href="#" className="text-xs md:text-sm text-slate-500 hover:text-slate-900">Legal Disclosures</a>
          </div>
          <p className="text-[10px] md:text-xs text-slate-400 text-center px-4">
            © 2024 RetroAide Financial Services. All rights reserved. Member SIPC.
          </p>
        </div>
      </footer>

      {/* Floating CTA */}
      <div className="fixed bottom-4 right-4 md:bottom-8 md:right-8 z-50">
        <button className="bg-white shadow-xl md:shadow-2xl rounded-full px-4 py-2.5 md:px-6 md:py-3 flex items-center gap-2 border border-slate-100 hover:scale-105 transition-transform">
          <Headphones className="w-4 h-4 md:w-5 md:h-5 text-[#0f172a]" />
          <span className="font-semibold text-xs md:text-sm text-[#0f172a]">Parler à un humain</span>
        </button>
      </div>
    </div>
  );
};

export default Home;

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import OnboardingStep1 from './pages/OnboardingStep1';
import OnboardingStep2 from './pages/OnboardingStep2';
import OnboardingStep3 from './pages/OnboardingStep3';
import Dashboard from './pages/Dashboard';
import Glossary from './pages/Glossary';
import OnboardingStep4 from './pages/OnboardingStep4';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen antialiased bg-white text-slate-900">
        <main className="w-full min-h-screen flex flex-col relative">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/onboarding/1" element={<OnboardingStep1 />} />
            <Route path="/onboarding/2" element={<OnboardingStep2 />} />
            <Route path="/onboarding/3" element={<OnboardingStep3 />} />
            <Route path="/onboarding/4" element={<OnboardingStep4 />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/glossary" element={<Glossary />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

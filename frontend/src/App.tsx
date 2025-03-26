import React, { useState, useEffect } from 'react';
import { Factory, Recycle, Search, TrendingUp, Users, Workflow } from 'lucide-react';
import { supabase } from './lib/supabase';
import { AuthModal } from './components/AuthModal';
import { MaterialForm } from './components/MaterialForm';
import { AdminHub } from './components/AdminHub';
import { isUserAdmin } from './lib/supabase';

function App() {
  const [session, setSession] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showMaterialForm, setShowMaterialForm] = useState<'waste' | 'requirement' | null>(null);
  const [showAdminHub, setShowAdminHub] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        checkAdminStatus(session.user.id);
      }
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session?.user) {
        checkAdminStatus(session.user.id);
      } else {
        setIsAdmin(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const checkAdminStatus = async (userId: string) => {
    const adminStatus = await isUserAdmin(userId);
    setIsAdmin(adminStatus);
  };

  const handleAction = () => {
    if (!session) {
      setShowAuthModal(true);
    } else if (isAdmin) {
      setShowAdminHub(true);
    }
  };

  const handleListMaterials = () => {
    if (session) {
      setShowMaterialForm('waste');
    } else {
      setShowAuthModal(true);
    }
  };

  const handleFindResources = () => {
    if (session) {
      setShowMaterialForm('requirement');
    } else {
      setShowAuthModal(true);
    }
  };

  if (showAdminHub && isAdmin) {
    return (
      <div>
        <nav className="bg-slate-900 p-4">
          <div className="container mx-auto flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Workflow className="h-8 w-8 text-emerald-400" />
              <span className="text-2xl font-bold text-white">EcoSync</span>
            </div>
            <button
              onClick={() => setShowAdminHub(false)}
              className="text-white hover:text-emerald-400 transition"
            >
              Back to Main Site
            </button>
          </div>
        </nav>
        <AdminHub />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Hero Section */}
      <header className="relative">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1590502160462-58b41354f588?auto=format&fit=crop&q=80"
            alt="Industrial background"
            className="w-full h-[600px] object-cover opacity-20"
          />
        </div>
        
        <nav className="relative z-10 container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Workflow className="h-8 w-8 text-emerald-400" />
              <span className="text-2xl font-bold text-white">EcoSync</span>
            </div>
            <div className="hidden md:flex space-x-8">
              <a href="#how-it-works" className="text-gray-300 hover:text-white transition">How It Works</a>
              <a href="#benefits" className="text-gray-300 hover:text-white transition">Benefits</a>
              <a href="#contact" className="text-gray-300 hover:text-white transition">Contact</a>
            </div>
            <button 
              onClick={handleAction}
              className="bg-emerald-500 text-white px-6 py-2 rounded-lg hover:bg-emerald-600 transition"
            >
              {session ? (isAdmin ? 'Admin Dashboard' : 'Dashboard') : 'Get Started'}
            </button>
          </div>
        </nav>

        <div className="relative z-10 container mx-auto px-6 py-24 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Industrial Symbiosis Marketplace
          </h1>
          <p className="text-xl text-gray-300 mb-12 max-w-3xl mx-auto">
            Connect with businesses to exchange resources, reduce waste, and maximize efficiency through AI-powered matching.
          </p>
          <div className="flex flex-col md:flex-row gap-4 justify-center">
            <button 
              onClick={handleFindResources}
              className="bg-emerald-500 text-white px-8 py-4 rounded-lg hover:bg-emerald-600 transition flex items-center justify-center space-x-2"
            >
              <Search className="h-5 w-5" />
              <span>Find Resources</span>
            </button>
            <button 
              onClick={handleListMaterials}
              className="bg-slate-700 text-white px-8 py-4 rounded-lg hover:bg-slate-600 transition flex items-center justify-center space-x-2"
            >
              <Factory className="h-5 w-5" />
              <span>List Your Materials</span>
            </button>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className="py-24 bg-slate-800">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-white text-center mb-16">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-12">
            <div className="bg-slate-700 p-8 rounded-xl">
              <div className="bg-emerald-500/10 p-3 rounded-lg w-fit mb-6">
                <Factory className="h-6 w-6 text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">List Resources</h3>
              <p className="text-gray-300">
                Register your business and list your available resources or requirements.
              </p>
            </div>
            <div className="bg-slate-700 p-8 rounded-xl">
              <div className="bg-emerald-500/10 p-3 rounded-lg w-fit mb-6">
                <Recycle className="h-6 w-6 text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">AI Matching</h3>
              <p className="text-gray-300">
                Our AI system matches your resources with potential partners based on compatibility.
              </p>
            </div>
            <div className="bg-slate-700 p-8 rounded-xl">
              <div className="bg-emerald-500/10 p-3 rounded-lg w-fit mb-6">
                <TrendingUp className="h-6 w-6 text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Create Value</h3>
              <p className="text-gray-300">
                Connect with matches and create sustainable business relationships.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-24 bg-slate-900">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-12 text-center">
            <div>
              <div className="text-4xl font-bold text-emerald-400 mb-2">500+</div>
              <div className="text-gray-300">Active Businesses</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-emerald-400 mb-2">1,200+</div>
              <div className="text-gray-300">Successful Matches</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-emerald-400 mb-2">50,000t</div>
              <div className="text-gray-300">Waste Reduced</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-slate-800">
        <div className="container mx-auto px-6 text-center">
          <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-2xl p-12">
            <h2 className="text-3xl font-bold text-white mb-6">
              Ready to Join the Circular Economy?
            </h2>
            <p className="text-white/90 mb-8 max-w-2xl mx-auto">
              Start your journey towards sustainable business practices and resource efficiency today.
            </p>
            <button 
              onClick={handleAction}
              className="bg-white text-emerald-600 px-8 py-4 rounded-lg hover:bg-gray-100 transition flex items-center space-x-2 mx-auto"
            >
              <Users className="h-5 w-5" />
              <span>Join the Network</span>
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 py-12">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Workflow className="h-6 w-6 text-emerald-400" />
              <span className="text-xl font-bold text-white">EcoSync</span>
            </div>
            <div className="text-gray-400 text-sm">
              © 2025 EcoSync. All rights reserved.
            </div>
          </div>
        </div>
      </footer>

      {/* Modals */}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
      {showMaterialForm && (
        <MaterialForm 
          type={showMaterialForm} 
          onClose={() => setShowMaterialForm(null)} 
        />
      )}
    </div>
  );
}

export default App;
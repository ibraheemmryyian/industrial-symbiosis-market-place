import { supabase } from './lib/supabase';
import { useState } from 'react';
import { ConfirmDialog } from './ConfirmDialog';
import { OnboardingForm } from './components/OnboardingForm';

function App() {
    const [showConfirmLogout, setShowConfirmLogout] = useState(false);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [showAdminHub, setShowAdminHub] = useState(false);
    const [showOnboarding, setShowOnboarding] = useState(false);
    const [showMatches, setShowMatches] = useState(false);

    const handleLogout = async () => {
        await supabase.auth.signOut();
        setSession(null); // Clear session state
    };

    const handleAction = () => {
        if (!session) {
            setShowAuthModal(true);
        } else if (isAdmin) {
            setShowAdminHub(true);
        } else {
            // Check if the user has completed their profile
            const userProfileCompleted = checkUserProfileCompletion(); // Implement this function
            if (!userProfileCompleted) {
                setShowOnboarding(true); // Show onboarding if profile is incomplete
            } else {
                setShowMatches(true);
            }
        }
    };

    return (
        <div>
            {/* Navigation Bar */}
            <nav className="bg-slate-900 p-4">
                <div className="container mx-auto flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                        <Workflow className="h-8 w-8 text-emerald-400" />
                        <span className="text-2xl font-bold text-white">LoopLink</span>
                    </div>
                    <div className="flex items-center space-x-4">
                        {session && (
                            <button onClick={() => setShowConfirmLogout(true)} className="text-white hover:text-emerald-400 transition">
                                Logout
                            </button>
                        )}
                    </div>
                </div>
            </nav>

            {showConfirmLogout && (
                <ConfirmDialog
                    message="Are you sure you want to log out?"
                    onConfirm={handleLogout}
                    onCancel={() => setShowConfirmLogout(false)}
                />
            )}
            {/* ... existing code ... */}
        </div>
    );
}

export default App; 
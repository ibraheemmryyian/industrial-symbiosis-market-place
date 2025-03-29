import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { Activity, Link, MapPin, Check, X, Spinner } from 'lucide-react';

interface Match {
  id: string;
  waste_id: string;
  consumer_id: string;
  score: number;
  details: {
    category_match: number;
    keyword_overlap: number;
    distance_km?: number;
    quantity_score: number;
  };
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  wastes: {
    material_name: string;
    quantity: number;
    unit: string;
    companies: {
      name: string;
    };
  };
  companies: {
    name: string;
  };
}

export function MatchList() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadMatches();
  }, []);

  async function loadMatches() {
    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      const { data: profile } = await supabase
        .from('company_profiles')
        .select('company_id')
        .eq('user_id', user.id)
        .single();

      if (!profile?.company_id) {
        setError('Please complete your company profile first');
        setMatches([]);
        return;
      }

      const { data, error } = await supabase
        .from('matches')
        .select(`
          *,
          wastes!waste_id (material_name, quantity, unit, companies!company_id (name)),
          companies!consumer_id (name)
        `)
        .or(`waste_id.in.(select id from wastes where company_id.eq.${profile.company_id}),consumer_id.eq.${profile.company_id}`)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setMatches(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load matches');
      console.error('Error loading matches:', err);
    } finally {
      setLoading(false);
    }
  }

  async function updateMatchStatus(matchId: string, status: 'accepted' | 'rejected') {
    try {
      const { error } = await supabase
        .from('matches')
        .update({ status })
        .eq('id', matchId);

      if (error) throw error;
      await loadMatches();
    } catch (err: any) {
      setError(err.message || 'Failed to update match status');
      console.error('Error updating match:', err);
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Potential Matches</h2>

      <div className="flex justify-between mb-4">
        <select onChange={(e) => setFilter(e.target.value)} className="border rounded p-2">
          <option value="all">All Matches</option>
          <option value="accepted">Accepted</option>
          <option value="pending">Pending</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">Loading...</div>
      ) : error ? (
        <div className="text-red-500 bg-red-50 p-4 rounded-lg">{error}</div>
      ) : matches.length === 0 ? (
        <div className="text-gray-500 text-center py-8">
          No matches found yet. Check back later!
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <div key={match.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium text-lg">
                    {match.wastes.material_name} ({match.wastes.quantity} {match.wastes.unit})
                  </h3>
                  <p className="text-gray-600">
                    {match.wastes.companies.name} → {match.companies.name}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    match.status === 'accepted' ? 'bg-green-100 text-green-800' :
                    match.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {match.status === 'accepted' ? 'Accepted' : 
                     match.status === 'rejected' ? 'Rejected' : 'Pending'}
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                    {Math.round(match.score * 100)}% match
                  </span>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center">
                  <Link className="h-4 w-4 text-gray-500 mr-2" />
                  <span>Category match: {Math.round(match.details.category_match * 100)}%</span>
                </div>
                <div className="flex items-center">
                  <MapPin className="h-4 w-4 text-gray-500 mr-2" />
                  <span>
                    {match.details.distance_km ? 
                      `${match.details.distance_km.toFixed(1)} km away` : 
                      'Distance unknown'}
                  </span>
                </div>
              </div>

              {match.status === 'pending' && (
                <div className="mt-4 flex space-x-2">
                  <button
                    onClick={() => updateMatchStatus(match.id, 'accepted')}
                    className="flex items-center px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
                  >
                    <Check className="h-4 w-4 mr-1" />
                    Accept
                  </button>
                  <button
                    onClick={() => updateMatchStatus(match.id, 'rejected')}
                    className="flex items-center px-3 py-1 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
                  >
                    <X className="h-4 w-4 mr-1" />
                    Reject
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

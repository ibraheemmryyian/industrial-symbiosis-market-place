import React, { useState } from 'react';
import { supabase } from '../lib/supabase';
import { X } from 'lucide-react';

interface MaterialFormProps {
  onClose: () => void;
  type: 'waste' | 'requirement';
}

export function MaterialForm({ onClose, type }: MaterialFormProps) {
  const [formData, setFormData] = useState({
    material_name: '',
    quantity: '',
    unit: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      // First check if user already has a company profile
      const { data: profile, error: profileError } = await supabase
        .from('company_profiles')
        .select('company_id')
        .eq('user_id', user.id)
        .single();

      if (profileError && profileError.code !== 'PGRST116') throw profileError;
      
      let companyId = profile?.company_id;
      
      // If no company exists, create one
      if (!companyId) {
        const { data: newCompanyId, error: rpcError } = await supabase.rpc('create_company_and_profile', {
          user_id: user.id,
          profile_data: {
            industry: 'Other',
            location: '',
            description: ''
          },
          company_data: {
            name: 'My Company'
          }
        });

        if (rpcError) throw rpcError;
        companyId = newCompanyId;
      }

      if (rpcError) throw rpcError;
      if (!companyId) throw new Error('Failed to create/get company');

      const { error: err } = await supabase.from('materials').insert([
        {
          name: formData.material_name,
          quantity: parseFloat(formData.quantity),
          unit: formData.unit,
          description: formData.description,
          company_id: companyId
        },
      ]).select();

      if (err) throw err;
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to submit material. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md relative">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-500 hover:text-gray-700"
        >
          <X className="h-5 w-5" />
        </button>
        
        <h2 className="text-2xl font-bold mb-6">
          {type === 'waste' ? 'List Waste Material' : 'List Required Material'}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Material Name
              </label>
              <input
                type="text"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                value={formData.material_name}
                onChange={(e) => setFormData({ ...formData, material_name: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unit
                </label>
                <input
                  type="text"
                  required
                  placeholder="kg, tons, etc."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                required
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            {error && (
              <div className="text-red-500 text-sm bg-red-50 p-2 rounded">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-500 text-white py-2 px-4 rounded-lg hover:bg-emerald-600 transition disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Submit Material'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

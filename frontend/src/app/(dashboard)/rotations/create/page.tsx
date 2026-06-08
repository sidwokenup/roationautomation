"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Trash2, Plus } from 'lucide-react';

export default function CreateRotationPage() {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    campaign_id: '',
    interval_minutes: 15,
    links: [{ url: '', position: 0, is_active: true }]
  });
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const { data } = await api.get('/campaigns/');
        setCampaigns(data);
        if (data.length > 0) {
          setFormData(prev => ({ ...prev, campaign_id: data[0].id }));
        }
      } catch (err) {
        console.error("Failed to load campaigns");
      }
    };
    fetchCampaigns();
  }, []);

  const addLink = () => {
    setFormData(prev => ({
      ...prev,
      links: [...prev.links, { url: '', position: prev.links.length, is_active: true }]
    }));
  };

  const removeLink = (index: number) => {
    setFormData(prev => ({
      ...prev,
      links: prev.links.filter((_, i) => i !== index)
    }));
  };

  const updateLink = (index: number, value: string) => {
    const newLinks = [...formData.links];
    newLinks[index].url = value;
    setFormData(prev => ({ ...prev, links: newLinks }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/rotations/groups', formData);
      router.push('/rotations');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create rotation');
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Create Link Rotation</h1>
      
      {error && <div className="mb-4 bg-red-50 text-red-700 p-4 rounded-md">{error}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 shadow sm:rounded-md sm:overflow-hidden">
        <div>
          <label className="block text-sm font-medium text-gray-700">Rotation Name</label>
          <input
            type="text"
            required
            className="mt-1 block w-full rounded-md border-gray-300 border p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Campaign</label>
          <select
            required
            className="mt-1 block w-full rounded-md border-gray-300 border p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900"
            value={formData.campaign_id}
            onChange={(e) => setFormData({ ...formData, campaign_id: e.target.value })}
          >
            {campaigns.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Interval (Minutes)</label>
          <input
            type="number"
            min="1"
            required
            className="mt-1 block w-full rounded-md border-gray-300 border p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900"
            value={formData.interval_minutes === null || Number.isNaN(formData.interval_minutes) ? '' : formData.interval_minutes}
            onChange={(e) => setFormData({ ...formData, interval_minutes: e.target.value === '' ? 15 : parseInt(e.target.value, 10) || 15 })}
          />
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">Destination URLs</label>
            <button type="button" onClick={addLink} className="text-indigo-600 hover:text-indigo-900 text-sm font-medium flex items-center">
              <Plus className="h-4 w-4 mr-1" /> Add URL
            </button>
          </div>
          <div className="space-y-3">
            {formData.links.map((link, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-gray-500 text-sm w-6">{index + 1}.</span>
                <input
                  type="url"
                  required
                  className="block w-full rounded-md border-gray-300 border p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900 placeholder-gray-400"
                  value={link.url}
                  onChange={(e) => updateLink(index, e.target.value)}
                  placeholder="https://..."
                />
                {formData.links.length > 1 && (
                  <button type="button" onClick={() => removeLink(index)} className="text-red-500 hover:text-red-700 p-2">
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700"
          >
            Save Rotation
          </button>
        </div>
      </form>
    </div>
  );
}
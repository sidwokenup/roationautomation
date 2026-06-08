"use client";

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

export default function EditCampaignPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);
  
  const [formData, setFormData] = useState({
    name: '',
    target_link: '',
    bot_link: '',
    target_mode: 2,
    status: 'active'
  });
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCampaign = async () => {
      try {
        const { data } = await api.get(`/campaigns/${id}`);
        setFormData({
          name: data.name,
          target_link: data.target_link,
          bot_link: data.bot_link || '',
          target_mode: data.target_mode || 2,
          status: data.status
        });
      } catch (err) {
        setError('Failed to load campaign');
      }
    };
    fetchCampaign();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.put(`/campaigns/${id}`, { ...formData, target_mode: 2 });
      router.push('/campaigns');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update campaign');
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Edit Campaign</h1>
      
      {error && <div className="mb-4 bg-red-50 text-red-700 p-4 rounded-md">{error}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 shadow sm:rounded-md sm:overflow-hidden">
        <div>
          <label className="block text-sm font-medium text-gray-700">Campaign Name</label>
          <input
            type="text"
            required
            className="mt-1 block w-full rounded-md border-gray-300 border p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Target Link</label>
          <input
            type="url"
            required
            className="mt-1 block w-full rounded-md border-gray-300 border p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900"
            value={formData.target_link}
            onChange={(e) => setFormData({ ...formData, target_link: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Bot Link</label>
          <input
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 border p-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm text-gray-900"
            value={formData.bot_link}
            onChange={(e) => setFormData({ ...formData, bot_link: e.target.value })}
          />
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Update
          </button>
        </div>
      </form>
    </div>
  );
}
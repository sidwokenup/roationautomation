"use client";

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Link from 'next/link';

export default function EditRotationPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);
  
  const [formData, setFormData] = useState({
    name: '',
    interval_minutes: 15,
  });
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRotation = async () => {
      try {
        const { data } = await api.get(`/rotations/groups/${id}`);
        setFormData({
          name: data.name,
          interval_minutes: data.interval_minutes,
        });
      } catch (err) {
        setError('Failed to load rotation');
      }
    };
    fetchRotation();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.put(`/rotations/groups/${id}`, formData);
      router.push('/rotations');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update rotation');
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Edit Rotation</h1>
      
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
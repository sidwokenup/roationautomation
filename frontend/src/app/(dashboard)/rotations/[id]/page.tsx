"use client";

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Link from 'next/link';

export default function ViewRotationPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);
  const [group, setGroup] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [groupRes, historyRes] = await Promise.all([
          api.get(`/rotations/groups/${id}`),
          api.get(`/rotations/groups/${id}/history`)
        ]);
        setGroup(groupRes.data);
        setHistory(historyRes.data);
      } catch (err) {
        setError('Failed to load rotation data');
      }
    };
    fetchData();
  }, [id]);

  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!group) return <div className="p-4">Loading...</div>;

  const currentLink = group.links && group.links.length > 0 ? group.links[group.current_link_index]?.url : 'None';
  const nextIndex = (group.current_link_index + 1) % (group.links?.length || 1);
  const nextLink = group.links && group.links.length > 0 ? group.links[nextIndex]?.url : 'None';

  const successCount = history.filter(h => h.rotation_status === 'SUCCESS').length;
  const failCount = history.filter(h => h.rotation_status !== 'SUCCESS').length;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Rotation Details: {group.name}</h1>
        <Link 
          href={`/rotations/edit/${id}`}
          className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          Edit Settings
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Current URL</dt>
          <dd className="mt-1 text-lg font-semibold tracking-tight text-gray-900 truncate">{currentLink}</dd>
        </div>
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Next URL</dt>
          <dd className="mt-1 text-lg font-semibold tracking-tight text-gray-900 truncate">{nextLink}</dd>
        </div>
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Status</dt>
          <dd className="mt-1 text-lg font-semibold tracking-tight text-gray-900">
            {group.is_active && !group.is_paused ? 'Running' : group.is_active && group.is_paused ? 'Paused' : 'Stopped'}
          </dd>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Total Rotations</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">{history.length}</dd>
        </div>
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Successful</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-green-600">{successCount}</dd>
        </div>
        <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
          <dt className="truncate text-sm font-medium text-gray-500">Failed</dt>
          <dd className="mt-1 text-3xl font-semibold tracking-tight text-red-600">{failCount}</dd>
        </div>
      </div>

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">Rotation History</h3>
        </div>
        <div className="border-t border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Previous URL</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">New URL</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Exec (ms)</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.map((h, i) => (
                <tr key={i}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(h.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 truncate max-w-[200px]">{h.previous_url || 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 truncate max-w-[200px]">{h.new_url}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${h.rotation_status === 'SUCCESS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {h.rotation_status}
                    </span>
                    {h.error_message && <p className="text-xs text-red-500 mt-1 truncate max-w-xs">{h.error_message}</p>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{h.execution_time_ms}</td>
                </tr>
              ))}
              {history.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">No rotation history found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="mt-6">
        <button
          onClick={() => router.push('/rotations')}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          &larr; Back to Rotations
        </button>
      </div>
    </div>
  );
}
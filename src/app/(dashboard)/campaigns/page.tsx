"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Search, Plus, MoreVertical, Copy, Trash2, Edit, Eye, Download } from 'lucide-react';

interface Campaign {
  id: string;
  palladium_id: number;
  name: string;
  target_link: string;
  status: string;
  created_at: string;
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [search, setSearch] = useState('');
  const [skip, setSkip] = useState(0);
  const limit = 10;
  const router = useRouter();

  const fetchCampaigns = async () => {
    try {
      const { data } = await api.get('/campaigns/', {
        params: { skip, limit, search }
      });
      setCampaigns(data);
    } catch (error: any) {
      console.error('Failed to fetch campaigns', error.response?.data || error.message);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, [skip, search]);

  const handleSync = async () => {
    try {
      await api.post('/campaigns/sync');
      fetchCampaigns();
    } catch (error: any) {
      console.error('Failed to sync campaigns', error.response?.data || error.message);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this campaign?')) {
      try {
        await api.delete(`/campaigns/${id}`);
        fetchCampaigns();
      } catch (error: any) {
        console.error('Failed to delete', error.response?.data || error.message);
      }
    }
  };

  const handleDownload = async (id: string, type: 'zip' | 'wp') => {
    try {
      const endpoint = type === 'wp' ? 'downloadWp' : 'download';
      const response = await api.get(`/campaigns/${id}/${endpoint}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `campaign_${id}_${type}.zip`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('Download failed', error.response?.data || error.message);
      alert('Failed to download the ZIP file. Please try again.');
    }
  };

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-xl font-semibold text-gray-900">Campaigns</h1>
          <p className="mt-2 text-sm text-gray-700">A list of all campaigns including their name, target link, and status.</p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none flex space-x-3">
          <button onClick={handleSync} className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50">
            Sync API
          </button>
        </div>
      </div>

      <div className="mt-6 flex items-center">
        <div className="relative w-full max-w-md">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full rounded-md border-gray-300 pl-10 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2"
            placeholder="Search campaigns..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Name</th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Target Link</th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Palladium ID</th>
                    <th className="relative px-3 py-3.5"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {campaigns.map((campaign) => (
                    <tr key={campaign.id}>
                      <td className="whitespace-nowrap px-3 py-4 text-sm font-medium text-gray-900">{campaign.name}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500 truncate max-w-xs">{campaign.target_link}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${campaign.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                          {campaign.status}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{campaign.palladium_id}</td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <div className="flex justify-end space-x-2">
                          <Link href={`/campaigns/${campaign.id}`} className="text-indigo-600 hover:text-indigo-900" title="View"><Eye className="h-4 w-4" /></Link>
                          <Link href={`/campaigns/edit/${campaign.id}`} className="text-blue-600 hover:text-blue-900" title="Edit"><Edit className="h-4 w-4" /></Link>
                          <button onClick={() => handleDownload(campaign.id, 'zip')} className="text-gray-600 hover:text-gray-900" title="Download ZIP"><Download className="h-4 w-4" /></button>
                          <button onClick={() => handleDelete(campaign.id)} className="text-red-600 hover:text-red-900" title="Delete"><Trash2 className="h-4 w-4" /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="mt-4 flex items-center justify-between">
              <button
                onClick={() => setSkip(Math.max(0, skip - limit))}
                disabled={skip === 0}
                className="rounded border px-4 py-2 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setSkip(skip + limit)}
                disabled={campaigns.length < limit}
                className="rounded border px-4 py-2 text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}
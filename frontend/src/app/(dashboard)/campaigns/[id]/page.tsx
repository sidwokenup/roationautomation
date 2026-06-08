"use client";

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Link from 'next/link';
import { Edit } from 'lucide-react';

interface Campaign {
  id: string;
  palladium_id: number;
  name: string;
  target_link: string;
  bot_link: string;
  status: string;
  created_at: string;
}

export default function ViewCampaignPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCampaign = async () => {
      try {
        const { data } = await api.get(`/campaigns/${id}`);
        setCampaign(data);
      } catch (err) {
        setError('Failed to load campaign');
      }
    };
    fetchCampaign();
  }, [id]);

  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!campaign) return <div className="p-4">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Campaign Details</h1>
        <Link 
          href={`/campaigns/edit/${id}`}
          className="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          <Edit className="mr-2 h-4 w-4" /> Edit
        </Link>
      </div>

      <div className="overflow-hidden bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg font-medium leading-6 text-gray-900">{campaign.name}</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">Palladium ID: {campaign.palladium_id}</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Target Link</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">{campaign.target_link}</dd>
            </div>
            <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Bot Link</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">{campaign.bot_link || 'N/A'}</dd>
            </div>
            <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${campaign.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {campaign.status}
                </span>
              </dd>
            </div>
            <div className="py-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:py-5 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Created At</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">{new Date(campaign.created_at).toLocaleString()}</dd>
            </div>
          </dl>
        </div>
      </div>
      
      <div className="mt-6">
        <button
          onClick={() => router.push('/campaigns')}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          &larr; Back to Campaigns
        </button>
      </div>
    </div>
  );
}
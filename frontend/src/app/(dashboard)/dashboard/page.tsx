"use client";

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Layers, Activity, AlertTriangle } from 'lucide-react';

export default function Dashboard() {
  const [overview, setOverview] = useState<any>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const [campaignsRes, rotationsRes] = await Promise.all([
          api.get('/campaigns/'),
          api.get('/rotations/groups')
        ]);
        
        const campaigns = campaignsRes.data || [];
        const rotations = rotationsRes.data || [];
        
        setOverview({
          total_campaigns: campaigns.length,
          active_campaigns: campaigns.filter((c: any) => c.status === 'active').length,
          total_rotations: rotations.length,
          active_rotations: rotations.filter((r: any) => r.is_active && !r.is_paused).length,
        });
      } catch (err: any) {
        console.error('Failed to load overview', err);
        setError('Failed to load dashboard data. Please try again.');
      }
    };
    fetchOverview();
  }, []);

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center text-red-700">
          <AlertTriangle className="mr-3 h-5 w-5" />
          {error}
        </div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="animate-pulse">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6 sm:mb-8">Dashboard Overview</h1>
        <div className="grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-2xl"></div>
          ))}
        </div>
      </div>
    );
  }

  const stats = [
    { name: 'Total Campaigns', stat: overview.total_campaigns, icon: Layers, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { name: 'Active Campaigns', stat: overview.active_campaigns, icon: Activity, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    { name: 'Total Rotations', stat: overview.total_rotations, icon: Layers, color: 'text-blue-600', bg: 'bg-blue-50' },
    { name: 'Active Rotations', stat: overview.active_rotations, icon: Activity, color: 'text-amber-600', bg: 'bg-amber-50' },
  ];

  return (
    <div>
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Dashboard Overview</h1>
        <p className="text-sm sm:text-base text-gray-500 mt-1 sm:mt-2">Here's what's happening with your campaigns today.</p>
      </div>
      
      <div className="grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((item) => (
          <div
            key={item.name}
            className="relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center">
              <div className={`p-3 rounded-xl ${item.bg}`}>
                <item.icon className={`h-6 w-6 ${item.color}`} />
              </div>
              <div className="ml-4">
                <p className="truncate text-sm font-medium text-gray-500">{item.name}</p>
                <p className="text-2xl font-bold text-gray-900">{item.stat}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
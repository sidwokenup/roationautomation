"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { Plus, Eye, Edit, Trash2, Play, Pause, Square, RefreshCw } from 'lucide-react';

export default function RotationsPage() {
  const [groups, setGroups] = useState<any[]>([]);

  const fetchGroups = async () => {
    try {
      const { data } = await api.get('/rotations/groups');
      setGroups(data);
    } catch (error: any) {
      console.error('Failed to fetch rotations', error.response?.data || error.message);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleAction = async (id: string, action: string) => {
    try {
      await api.post(`/rotations/groups/${id}/${action}`);
      fetchGroups();
    } catch (error: any) {
      console.error(`Failed to ${action} rotation`, error.response?.data || error.message);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this rotation group?')) {
      try {
        await api.delete(`/rotations/groups/${id}`);
        fetchGroups();
      } catch (error: any) {
        console.error('Failed to delete', error.response?.data || error.message);
      }
    }
  };

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-xl font-semibold text-gray-900">Link Rotations</h1>
          <p className="mt-2 text-sm text-gray-700">Manage campaign link rotations and intervals.</p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Link href="/rotations/create" className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
            <Plus className="mr-2 h-4 w-4" /> New Rotation
          </Link>
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
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Interval (m)</th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th className="relative px-3 py-3.5"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {groups.map((group) => {
                    let statusLabel = 'Stopped';
                    let statusColor = 'bg-gray-100 text-gray-800';
                    if (group.is_active && !group.is_paused) {
                      statusLabel = 'Running';
                      statusColor = 'bg-green-100 text-green-800';
                    } else if (group.is_active && group.is_paused) {
                      statusLabel = 'Paused';
                      statusColor = 'bg-yellow-100 text-yellow-800';
                    }

                    return (
                      <tr key={group.id}>
                        <td className="whitespace-nowrap px-3 py-4 text-sm font-medium text-gray-900">{group.name}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{group.interval_minutes}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${statusColor}`}>
                            {statusLabel}
                          </span>
                        </td>
                        <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                          <div className="flex justify-end space-x-3">
                            {!group.is_active && <button onClick={() => handleAction(group.id, 'start')} className="text-green-600 hover:text-green-900" title="Start"><Play className="h-4 w-4" /></button>}
                            {group.is_active && !group.is_paused && <button onClick={() => handleAction(group.id, 'pause')} className="text-yellow-600 hover:text-yellow-900" title="Pause"><Pause className="h-4 w-4" /></button>}
                            {group.is_active && group.is_paused && <button onClick={() => handleAction(group.id, 'resume')} className="text-green-600 hover:text-green-900" title="Resume"><Play className="h-4 w-4" /></button>}
                            {group.is_active && <button onClick={() => handleAction(group.id, 'stop')} className="text-red-600 hover:text-red-900" title="Stop"><Square className="h-4 w-4" /></button>}
                            <button onClick={() => handleAction(group.id, 'rotate-now')} className="text-indigo-600 hover:text-indigo-900" title="Rotate Now"><RefreshCw className="h-4 w-4" /></button>
                            
                            <Link href={`/rotations/${group.id}`} className="text-indigo-600 hover:text-indigo-900" title="View"><Eye className="h-4 w-4" /></Link>
                            <Link href={`/rotations/edit/${group.id}`} className="text-blue-600 hover:text-blue-900" title="Edit"><Edit className="h-4 w-4" /></Link>
                            <button onClick={() => handleDelete(group.id)} className="text-gray-600 hover:text-gray-900" title="Delete"><Trash2 className="h-4 w-4" /></button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
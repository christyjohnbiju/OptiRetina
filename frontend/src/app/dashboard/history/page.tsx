'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import axios from 'axios';

interface Record {
  id: string;
  filename: string;
  prediction: string;
  confidence: number;
  date: string;
  report_url: string;
  is_noisy: boolean;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<Record[]>([]);
  const [filtered, setFiltered] = useState<Record[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchHistory = async () => {
        try {
            const res = await axios.get('http://localhost:8000/history');
            setHistory(res.data);
            setFiltered(res.data);
        } catch (e) {
            console.error(e);
        }
    };
    fetchHistory();
  }, []);

  useEffect(() => {
    const lower = search.toLowerCase();
    setFiltered(history.filter(h => 
        h.filename.toLowerCase().includes(lower) || 
        h.prediction.toLowerCase().includes(lower)
    ));
  }, [search, history]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight text-slate-800">Analysis History</h2>
      </div>

      <div className="flex items-center space-x-2 bg-white p-2 rounded-lg border shadow-sm max-w-md">
        <Search className="text-slate-400" />
        <Input 
            placeholder="Search by filename or result..." 
            className="border-none focus-visible:ring-0"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
              {filtered.length === 0 ? (
                  <div className="text-center py-10 text-slate-500">No records found.</div>
              ) : (
                  <div className="rounded-md border">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-50 text-slate-500 font-medium border-b">
                            <tr>
                                <th className="px-4 py-3">Date</th>
                                <th className="px-4 py-3">Filename</th>
                                <th className="px-4 py-3">Prediction</th>
                                <th className="px-4 py-3">Confidence</th>
                                <th className="px-4 py-3">Quality</th>
                                <th className="px-4 py-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map((rec) => (
                                <tr key={rec.id} className="border-b last:border-0 hover:bg-slate-50 transition-colors">
                                    <td className="px-4 py-3">{new Date(rec.date).toLocaleString()}</td>
                                    <td className="px-4 py-3 font-medium text-slate-700">{rec.filename}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${rec.prediction === 'No_DR' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                            {rec.prediction.replace('_', ' ')}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">{(rec.confidence * 100).toFixed(1)}%</td>
                                    <td className="px-4 py-3">
                                        {rec.is_noisy ? (
                                            <span className="text-yellow-600 flex items-center gap-1">⚠️ Noisy</span>
                                        ) : (
                                            <span className="text-slate-500">Good</span>
                                        )}
                                    </td>
                                    <td className="px-4 py-3">
                                        <a href={rec.report_url} target="_blank" rel="noopener noreferrer">
                                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                                <FileText className="h-4 w-4 text-blue-500" />
                                            </Button>
                                        </a>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                  </div>
              )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

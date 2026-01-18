'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, ArrowRight, Activity, Percent } from "lucide-react";
import Link from 'next/link';
import axios from 'axios';

interface Record {
  id: string;
  filename: string;
  prediction: string;
  confidence: number;
  date: string;
  report_url: string;
}

export default function DashboardPage() {
  const [history, setHistory] = useState<Record[]>([]);
  const [stats, setStats] = useState({ total: 0, healthy: 0, dr: 0 });

  useEffect(() => {
    // Fetch history
    const fetchHistory = async () => {
        try {
            const res = await axios.get('http://localhost:8000/history');
            const data = res.data;
            setHistory(data);
            
            // Calculate stats
            const total = data.length;
            const healthy = data.filter((r: any) => r.prediction === 'No_DR').length;
            const dr = total - healthy;
            setStats({ total, healthy, dr });
        } catch (e) {
            console.error("Failed to fetch history", e);
        }
    };
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight text-slate-800">Dashboard Overview</h2>
        <Link href="/dashboard/upload">
            <Button className="bg-blue-600 hover:bg-blue-700">
                Create New Analysis <ArrowRight className="ml-2 h-4 w-4"/>
            </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">Scans performed</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Healthy Eyes</CardTitle>
            <Percent className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.healthy}</div>
            <p className="text-xs text-muted-foreground">No DR Detected</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">DR Detected</CardTitle>
            <Activity className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.dr}</div>
            <p className="text-xs text-muted-foreground">Mild to Proliferative</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 lg:col-span-7">
          <CardHeader>
            <CardTitle>Recent Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
                {history.length === 0 ? (
                    <div className="text-center py-10 text-slate-500">No records found. Start your first analysis.</div>
                ) : (
                    history.map((rec) => (
                        <div key={rec.id} className="flex items-center justify-between p-4 border rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow">
                            <div className="flex items-center space-x-4">
                                <div className={`w-2 h-12 rounded-full ${rec.prediction === 'No_DR' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                <div>
                                    <p className="font-semibold text-slate-800">{rec.prediction.replace('_', ' ')}</p>
                                    <p className="text-sm text-slate-500">{new Date(rec.date).toLocaleString()}</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4">
                                <span className="text-sm font-medium bg-slate-100 px-3 py-1 rounded-full text-slate-600">
                                    {(rec.confidence * 100).toFixed(1)}% Conf.
                                </span>
                                <a href={rec.report_url} target="_blank" rel="noopener noreferrer">
                                    <Button variant="outline" size="sm">
                                        <FileText className="mr-2 h-4 w-4" /> PDF
                                    </Button>
                                </a>
                            </div>
                        </div>
                    ))
                )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

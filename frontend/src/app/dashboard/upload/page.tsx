'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { CloudUpload, AlertCircle, CheckCircle, FileText, Loader2 } from "lucide-react";
import axios from 'axios';

interface Result {
  prediction: string;
  confidence: number;
  report_url: string;
  is_noisy: boolean;
  tips: string[];
}

import { useSession } from "next-auth/react";

export default function UploadPage() {
  const { data: session } = useSession();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<Result | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResult(null);
      setProgress(0);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setProgress(10); // Start
    
    const formData = new FormData();
    formData.append('file', file);
    // Use session email or fallback
    formData.append('patient_id', session?.user?.email || 'Anonymous'); 

    try {
      // Simulate progress
      const interval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      const res = await axios.post('http://localhost:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      clearInterval(interval);
      setProgress(100);
      setResult(res.data);
    } catch (e) {
      console.error(e);
      alert('Analysis failed. Check backend connection.');
      setProgress(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h2 className="text-3xl font-bold tracking-tight text-slate-800">New Analysis</h2>
        <p className="text-slate-500">Upload a fundus image (JPEG/PNG) for immediate DR grading.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upload Section */}
        <Card className="h-fit">
          <CardHeader>
            <CardTitle>Image Upload</CardTitle>
            <CardDescription>Select a retinal image to analyze.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className={`border-2 border-dashed rounded-lg p-10 flex flex-col items-center justify-center text-center hover:bg-slate-50 transition-colors ${file ? 'border-blue-500' : 'border-slate-300'}`}>
                {preview ? (
                    <img src={preview} alt="Preview" className="max-h-64 object-contain rounded mb-4" />
                ) : (
                    <CloudUpload className="h-12 w-12 text-slate-400 mb-4" />
                )}
                
                <Label htmlFor="file-upload" className="cursor-pointer">
                    <span className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors inline-block">
                        {file ? "Change Image" : "Browse Files"}
                    </span>
                    <Input 
                        id="file-upload" 
                        type="file" 
                        accept="image/*" 
                        className="hidden" 
                        onChange={handleFileChange}
                    />
                </Label>
                <p className="text-xs text-slate-400 mt-2">Supported: JPEG, PNG. Max 5MB.</p>
            </div>

            {loading && (
                <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                        <span>Analyzing...</span>
                        <span>{progress}%</span>
                    </div>
                    <Progress value={progress} />
                </div>
            )}
            
            <Button 
                className="w-full bg-slate-900" 
                onClick={handleAnalyze} 
                disabled={!file || loading}
            >
                {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin"/> Processing</> : "Run Analysis"}
            </Button>
          </CardContent>
        </Card>

        {/* Results Section */}
        {result && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <Card className={`border-l-4 ${result.prediction === 'No_DR' ? 'border-l-green-500' : 'border-l-red-500'}`}>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            {result.prediction === 'No_DR' ? (
                                <CheckCircle className="text-green-500 h-6 w-6" />
                            ) : (
                                <AlertCircle className="text-red-500 h-6 w-6" />
                            )}
                            <span>Analysis Result: {result.prediction.replace('_', ' ')}</span>
                        </CardTitle>
                        <CardDescription>Confidence Score: {(result.confidence * 100).toFixed(2)}%</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid gap-2">
                            <h4 className="font-semibold text-sm text-slate-700">Medical Recommendations:</h4>
                            <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                {result.tips.map((tip, i) => (
                                    <li key={i}>{tip}</li>
                                ))}
                            </ul>
                        </div>
                        
                        {result.is_noisy && (
                            <div className="bg-yellow-50 text-yellow-800 p-3 rounded text-sm border border-yellow-200">
                                ⚠️ Low image quality detected. Preprocessing applied logic to enhance clarity.
                            </div>
                        )}
                    </CardContent>
                    <CardFooter>
                        <a href={result.report_url} target="_blank" rel="noopener noreferrer" className="w-full">
                            <Button variant="outline" className="w-full">
                                <FileText className="mr-2 h-4 w-4 text-blue-600" /> Download Full PDF Report
                            </Button>
                        </a>
                    </CardFooter>
                </Card>
            </div>
        )}
      </div>
    </div>
  )
}

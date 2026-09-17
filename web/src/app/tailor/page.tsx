'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { resumeAPI, tailorAPI, scoreAPI, exportAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Download, FileText, Wand2 } from 'lucide-react';
import Link from 'next/link';

interface Resume {
  id: number;
  title: string;
  content: any[];
}

export default function TailorPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('');
  const [jobDescription, setJobDescription] = useState('');
  
  const [analyzing, setAnalyzing] = useState(false);
  const [tailoring, setTailoring] = useState(false);
  
  const [score, setScore] = useState<any>(null);
  const [tailoredResume, setTailoredResume] = useState<any>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      resumeAPI.list().then(({ data }) => setResumes(data)).catch(console.error);
    }
  }, [isAuthenticated]);

  const handleAnalyze = async () => {
    if (!selectedResumeId || !jobDescription) return;
    setAnalyzing(true);
    try {
      const resume = resumes.find(r => r.id.toString() === selectedResumeId);
      if (resume) {
        const { data } = await scoreAPI.calculate({
          resume_content: resume.content,
          job_description: jobDescription
        });
        setScore(data);
      }
    } catch (error) {
      console.error('Failed to analyze:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleTailor = async () => {
    if (!selectedResumeId || !jobDescription) return;
    setTailoring(true);
    try {
      const resume = resumes.find(r => r.id.toString() === selectedResumeId);
      if (resume) {
        const { data } = await tailorAPI.tailor({
          resume_content: resume.content,
          job_description: jobDescription
        });
        setTailoredResume(data.tailored_resume);
        if (data.new_score) {
          setScore(data.new_score);
        }
      }
    } catch (error) {
      console.error('Failed to tailor:', error);
    } finally {
      setTailoring(false);
    }
  };

  const handleDownload = async (format: 'pdf' | 'docx') => {
    if (!tailoredResume) return;
    try {
      const apiCall = format === 'pdf' ? exportAPI.pdf : exportAPI.docx;
      const { data } = await apiCall({ sections: tailoredResume });
      
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `tailored_resume.${format}`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error(`Failed to download ${format}:`, error);
    }
  };

  if (isLoading || !isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Tailor Resume</h1>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Job Description</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="jd">Paste the job description here</Label>
                  <textarea
                    id="jd"
                    className="w-full min-h-[300px] p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="We are looking for a software engineer with experience in..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                  />
                </div>
                <Button 
                  onClick={handleAnalyze} 
                  disabled={!jobDescription || !selectedResumeId || analyzing}
                  className="w-full"
                >
                  {analyzing ? 'Analyzing...' : 'Analyze Match'}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Select Resume</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="resume">Choose a base resume</Label>
                  <select
                    id="resume"
                    className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                    value={selectedResumeId}
                    onChange={(e) => setSelectedResumeId(e.target.value)}
                  >
                    <option value="">Select a resume...</option>
                    {resumes.map(r => (
                      <option key={r.id} value={r.id}>{r.title}</option>
                    ))}
                  </select>
                </div>
                
                {score && (
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100 flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-blue-900">ATS Match Score</h4>
                      <p className="text-sm text-blue-700">Based on keyword matching</p>
                    </div>
                    <Badge className="text-lg px-3 py-1" variant={score.total_score > 80 ? "default" : "secondary"}>
                      {score.total_score}%
                    </Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tailor Output</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  size="lg" 
                  className="w-full" 
                  onClick={handleTailor}
                  disabled={!jobDescription || !selectedResumeId || tailoring}
                >
                  <Wand2 className="w-5 h-5 mr-2" />
                  {tailoring ? 'Tailoring in progress...' : 'Auto-Tailor Resume'}
                </Button>

                {tailoredResume && (
                  <div className="mt-6 pt-6 border-t space-y-4">
                    <div className="flex items-center justify-between text-green-700 bg-green-50 p-3 rounded-md">
                      <span className="font-medium">Tailoring Complete!</span>
                    </div>
                    
                    <div className="flex gap-4">
                      <Button variant="outline" className="flex-1" onClick={() => handleDownload('pdf')}>
                        <FileText className="w-4 h-4 mr-2" />
                        Download PDF
                      </Button>
                      <Button variant="outline" className="flex-1" onClick={() => handleDownload('docx')}>
                        <Download className="w-4 h-4 mr-2" />
                        Download DOCX
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

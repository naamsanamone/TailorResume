'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { resumeAPI, parseAPI, tailorAPI, scoreAPI, exportAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Download, FileText, Wand2, Upload, Check, X, Loader2 } from 'lucide-react';
import Link from 'next/link';

interface Resume {
  id: number;
  title: string;
  content: any[];
}

export default function TailorPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Resume state
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>('');
  const [uploadedSections, setUploadedSections] = useState<any[] | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // JD state
  const [jobDescription, setJobDescription] = useState('');

  // Processing state
  const [analyzing, setAnalyzing] = useState(false);
  const [tailoring, setTailoring] = useState(false);

  // Results
  const [score, setScore] = useState<any>(null);
  const [tailoredResult, setTailoredResult] = useState<any>(null);

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

  // Get the active resume content (either uploaded or selected from list)
  const getActiveResume = (): any[] | null => {
    if (uploadedSections) return uploadedSections;
    const selected = resumes.find(r => r.id.toString() === selectedResumeId);
    return selected?.content || null;
  };

  const hasResume = !!uploadedSections || !!selectedResumeId;

  // Handle file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.toLowerCase().split('.').pop();
    if (ext !== 'pdf' && ext !== 'docx') {
      setUploadError('Only PDF and DOCX files are supported');
      return;
    }

    setUploading(true);
    setUploadError('');
    setUploadedFileName(file.name);
    setSelectedResumeId(''); // Clear dropdown selection

    try {
      const { data } = await parseAPI.resume(file);
      setUploadedSections(data);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to parse resume';
      setUploadError(msg);
      setUploadedSections(null);
      setUploadedFileName('');
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const clearUpload = () => {
    setUploadedSections(null);
    setUploadedFileName('');
    setUploadError('');
  };

  const handleSelectResume = (value: string) => {
    setSelectedResumeId(value);
    if (value) clearUpload(); // Clear upload when selecting from dropdown
  };

  // Save uploaded resume to account
  const handleSaveResume = async () => {
    if (!uploadedSections) return;
    try {
      const title = uploadedFileName.replace(/\.(pdf|docx)$/i, '') || 'Uploaded Resume';
      const { data } = await resumeAPI.create({ title, content: uploadedSections });
      setResumes(prev => [...prev, data]);
      setSelectedResumeId(data.id.toString());
      clearUpload();
    } catch (err) {
      console.error('Failed to save resume:', err);
    }
  };

  // Analyze match score
  const handleAnalyze = async () => {
    const content = getActiveResume();
    if (!content || !jobDescription) return;

    setAnalyzing(true);
    try {
      const { data } = await scoreAPI.calculate({
        resume_content: content,
        job_description: jobDescription,
      });
      setScore(data);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to analyze';
      alert(msg);
    } finally {
      setAnalyzing(false);
    }
  };

  // Tailor resume
  const handleTailor = async () => {
    const content = getActiveResume();
    if (!content || !jobDescription) return;

    setTailoring(true);
    try {
      const { data } = await tailorAPI.tailor({
        resume_content: content,
        job_description: jobDescription,
      });
      setTailoredResult(data);
      if (data.ats_score) {
        setScore({ ats_score: data.ats_score, breakdown: data.score_breakdown });
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Failed to tailor resume';
      alert(msg);
    } finally {
      setTailoring(false);
    }
  };

  // Download
  const handleDownload = async (format: 'pdf' | 'docx') => {
    const sections = tailoredResult?.tailored_content || getActiveResume();
    if (!sections) return;

    try {
      const apiCall = format === 'pdf' ? exportAPI.pdf : exportAPI.docx;
      const { data } = await apiCall({ sections });

      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `tailored_resume.${format}`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(`Failed to download ${format}:`, err);
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
          {/* Left Column — JD Input */}
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
                    className="w-full min-h-[300px] p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    placeholder="We are looking for a software engineer with experience in..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                  />
                </div>
                <Button
                  onClick={handleAnalyze}
                  disabled={!jobDescription || !hasResume || analyzing}
                  className="w-full"
                >
                  {analyzing ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyzing...</>
                  ) : (
                    'Analyze Match'
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column — Resume + Results */}
          <div className="space-y-6">
            {/* Upload Resume */}
            <Card>
              <CardHeader>
                <CardTitle>Your Resume</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Upload area */}
                <div className="space-y-2">
                  <Label>Upload a resume (PDF or DOCX)</Label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={handleFileUpload}
                  />

                  {!uploadedSections && !uploading && (
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 hover:bg-blue-50/50 transition-colors cursor-pointer"
                    >
                      <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm font-medium text-gray-700">
                        Click to upload your resume
                      </p>
                      <p className="text-xs text-gray-500 mt-1">PDF or DOCX, max 10MB</p>
                    </button>
                  )}

                  {uploading && (
                    <div className="w-full border-2 border-dashed border-blue-300 rounded-lg p-6 text-center bg-blue-50/50">
                      <Loader2 className="w-8 h-8 mx-auto text-blue-500 mb-2 animate-spin" />
                      <p className="text-sm font-medium text-blue-700">
                        Parsing {uploadedFileName}...
                      </p>
                    </div>
                  )}

                  {uploadedSections && (
                    <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                      <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-green-800 truncate">
                          {uploadedFileName}
                        </p>
                        <p className="text-xs text-green-600">
                          {uploadedSections.length} sections parsed
                        </p>
                      </div>
                      <div className="flex gap-2 flex-shrink-0">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={handleSaveResume}
                          className="text-xs"
                        >
                          Save to Account
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={clearUpload}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  )}

                  {uploadError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-700">{uploadError}</p>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="mt-1 text-xs text-red-600"
                        onClick={() => { setUploadError(''); fileInputRef.current?.click(); }}
                      >
                        Try again
                      </Button>
                    </div>
                  )}
                </div>

                {/* OR divider */}
                {resumes.length > 0 && (
                  <>
                    <div className="flex items-center gap-3">
                      <Separator className="flex-1" />
                      <span className="text-xs text-gray-400 uppercase">or select existing</span>
                      <Separator className="flex-1" />
                    </div>

                    <div className="space-y-2">
                      <select
                        id="resume"
                        className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-sm"
                        value={selectedResumeId}
                        onChange={(e) => handleSelectResume(e.target.value)}
                      >
                        <option value="">Select a saved resume...</option>
                        {resumes.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.title}
                          </option>
                        ))}
                      </select>
                    </div>
                  </>
                )}

                {/* ATS Score */}
                {score && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold text-blue-900">ATS Match Score</h4>
                        <p className="text-xs text-blue-700 mt-0.5">
                          Keyword + Semantic + Format + Completeness
                        </p>
                      </div>
                      <Badge
                        className="text-lg px-3 py-1"
                        variant={score.ats_score > 80 ? 'default' : 'secondary'}
                      >
                        {Math.round(score.ats_score)}%
                      </Badge>
                    </div>
                    {score.breakdown && (
                      <div className="grid grid-cols-4 gap-2 mt-3">
                        {[
                          { label: 'Keywords', val: score.breakdown.keyword_score },
                          { label: 'Semantic', val: score.breakdown.semantic_score },
                          { label: 'Format', val: score.breakdown.format_score },
                          { label: 'Complete', val: score.breakdown.completeness_score },
                        ].map((item) => (
                          <div
                            key={item.label}
                            className="text-center p-2 bg-white rounded border"
                          >
                            <div className="text-sm font-bold text-blue-800">
                              {Math.round(item.val || 0)}%
                            </div>
                            <div className="text-[10px] text-gray-500">{item.label}</div>
                          </div>
                        ))}
                      </div>
                    )}
                    {score.missing_skills?.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs font-medium text-blue-800 mb-1">Missing Skills:</p>
                        <div className="flex flex-wrap gap-1">
                          {score.missing_skills.slice(0, 10).map((s: any, i: number) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              {typeof s === 'string' ? s : s.skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tailor + Download */}
            <Card>
              <CardHeader>
                <CardTitle>Tailor & Export</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  size="lg"
                  className="w-full"
                  onClick={handleTailor}
                  disabled={!jobDescription || !hasResume || tailoring}
                >
                  {tailoring ? (
                    <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Tailoring in progress...</>
                  ) : (
                    <><Wand2 className="w-5 h-5 mr-2" /> Auto-Tailor Resume</>
                  )}
                </Button>

                {tailoredResult && (
                  <div className="mt-4 pt-4 border-t space-y-4">
                    <div className="flex items-center gap-2 text-green-700 bg-green-50 p-3 rounded-md">
                      <Check className="w-4 h-4" />
                      <span className="font-medium text-sm">Tailoring Complete!</span>
                      {tailoredResult.keywords_added?.length > 0 && (
                        <span className="text-xs text-green-600 ml-auto">
                          +{tailoredResult.keywords_added.length} keywords added
                        </span>
                      )}
                    </div>

                    {tailoredResult.changes_summary?.length > 0 && (
                      <div className="text-sm space-y-1">
                        <p className="font-medium text-gray-700">Changes made:</p>
                        <ul className="list-disc pl-5 text-gray-600 text-xs space-y-0.5">
                          {tailoredResult.changes_summary.map((c: string, i: number) => (
                            <li key={i}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex gap-4">
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleDownload('docx')}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download DOCX
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleDownload('pdf')}
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        Download PDF
                      </Button>
                    </div>
                  </div>
                )}

                {/* Direct download without tailoring */}
                {!tailoredResult && hasResume && (
                  <div className="pt-2">
                    <p className="text-xs text-gray-500 mb-2">
                      Or download current resume without tailoring:
                    </p>
                    <div className="flex gap-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="flex-1 text-xs"
                        onClick={() => handleDownload('docx')}
                      >
                        <Download className="w-3 h-3 mr-1" />
                        DOCX
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="flex-1 text-xs"
                        onClick={() => handleDownload('pdf')}
                      >
                        <FileText className="w-3 h-3 mr-1" />
                        PDF
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

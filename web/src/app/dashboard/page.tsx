'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/auth-store';
import { resumeAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { PlusCircle, Wand2, LogOut } from 'lucide-react';

interface Resume {
  id: number;
  title: string;
  created_at: string;
  score?: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuthStore();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loadingResumes, setLoadingResumes] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchResumes();
    }
  }, [isAuthenticated]);

  const fetchResumes = async () => {
    try {
      const { data } = await resumeAPI.list();
      setResumes(data);
    } catch (error) {
      console.error('Failed to fetch resumes:', error);
    } finally {
      setLoadingResumes(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (isLoading || !isAuthenticated) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">TailorResume</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">Welcome, {user?.name || user?.email}</span>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Your Resumes</h2>
            <p className="text-gray-500">Manage and tailor your resumes</p>
          </div>
          <div className="flex gap-4">
            <Link href="/tailor">
              <Button variant="secondary">
                <Wand2 className="w-4 h-4 mr-2" />
                Quick Tailor
              </Button>
            </Link>
            <Button>
              <PlusCircle className="w-4 h-4 mr-2" />
              New Resume
            </Button>
          </div>
        </div>

        {loadingResumes ? (
          <div>Loading resumes...</div>
        ) : resumes.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-dashed">
            <h3 className="text-lg font-medium text-gray-900">No resumes yet</h3>
            <p className="text-gray-500 mt-1 mb-4">Create your first resume to get started.</p>
            <Button>
              <PlusCircle className="w-4 h-4 mr-2" />
              Create Resume
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resumes.map((resume) => (
              <Card key={resume.id} className="flex flex-col">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{resume.title}</CardTitle>
                    {resume.score !== undefined && (
                      <Badge variant={resume.score > 80 ? "default" : "secondary"}>
                        {resume.score} ATS
                      </Badge>
                    )}
                  </div>
                  <CardDescription>
                    {new Date(resume.created_at).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardFooter className="mt-auto pt-4 flex gap-2">
                  <Button variant="outline" className="flex-1">Edit</Button>
                  <Button variant="default" className="flex-1">Tailor</Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

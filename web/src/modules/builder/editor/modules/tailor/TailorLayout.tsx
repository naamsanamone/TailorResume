import React, { useState, useCallback } from 'react';
import { tailorResume, type TailorResponse } from '@/services/api';
import { zustandToSections, sectionsToUpdates, type TailoredUpdates } from '@/services/resumeMapper';
import { useBasicDetails } from '@/stores/basic';
import { useExperiences } from '@/stores/experience';
import { useEducations } from '@/stores/education';
import { useLanguages, useFrameworks, useTechnologies, useTools, useDatabases } from '@/stores/skills';
import { useAwards } from '@/stores/awards';
import { useVoluteeringStore } from '@/stores/volunteering';

const TailorLayout = () => {
  const [jd, setJd] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<TailorResponse | null>(null);
  const [updates, setUpdates] = useState<TailoredUpdates | null>(null);
  const [applied, setApplied] = useState(false);
  const [snapshot, setSnapshot] = useState<any>(null);

  const handleTailor = useCallback(async () => {
    if (jd.trim().length < 50) {
      setError('Please paste a job description (at least 50 characters).');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);
    setUpdates(null);
    setApplied(false);

    try {
      // Capture current state snapshot for revert
      const basicState = useBasicDetails.getState().values;
      const expState = useExperiences.getState().experiences;
      const eduState = useEducations.getState().academics;
      const langState = useLanguages.getState().values;
      const fwState = useFrameworks.getState().values;
      const techState = useTechnologies.getState().values;
      const toolState = useTools.getState().values;
      const dbState = useDatabases.getState().values;

      setSnapshot({
        basics: JSON.parse(JSON.stringify(basicState)),
        experiences: JSON.parse(JSON.stringify(expState)),
        academics: JSON.parse(JSON.stringify(eduState)),
        languages: [...langState],
        frameworks: [...fwState],
        technologies: [...techState],
        tools: [...toolState],
        databases: [...dbState],
      });

      // Build sections for API
      const sections = zustandToSections(
        basicState,
        expState as any,
        eduState as any,
        {
          languages: langState,
          frameworks: fwState,
          technologies: techState,
          tools: toolState,
          databases: dbState,
        },
        useAwards.getState().awards as any,
        useVoluteeringStore.getState().volunteeredExps || []
      );

      const res = await tailorResume(sections as any, jd);
      setResult(res);
      setUpdates(sectionsToUpdates(res.tailored_content as any));
    } catch (e: any) {
      setError(e.message || 'Failed to tailor resume. Is the backend running on port 8000?');
    } finally {
      setLoading(false);
    }
  }, [jd]);

  const applyChanges = useCallback(() => {
    if (!updates) return;

    // Apply summary
    if (updates.summary) {
      const current = useBasicDetails.getState().values;
      useBasicDetails.getState().reset({ ...current, summary: updates.summary });
    }

    // Apply label/headline
    if (updates.label) {
      const current = useBasicDetails.getState().values;
      useBasicDetails.getState().reset({ ...current, label: updates.label });
    }

    // Apply experience bullet updates
    if (updates.experiences) {
      const exps = useExperiences.getState().experiences;
      for (const upd of updates.experiences) {
        if (upd.index < exps.length) {
          useExperiences.getState().updateExperience(upd.index, {
            ...exps[upd.index],
            highlights: upd.highlights,
          });
        }
      }
    }

    // Apply skills
    if (updates.skills) {
      if (updates.skills.languages) useLanguages.getState().reset(updates.skills.languages);
      if (updates.skills.frameworks) useFrameworks.getState().reset(updates.skills.frameworks);
      if (updates.skills.technologies) useTechnologies.getState().reset(updates.skills.technologies);
      if (updates.skills.tools) useTools.getState().reset(updates.skills.tools);
      if (updates.skills.databases) useDatabases.getState().reset(updates.skills.databases);
    }

    setApplied(true);
  }, [updates]);

  const revertChanges = useCallback(() => {
    if (!snapshot) return;

    useBasicDetails.getState().reset(snapshot.basics);
    useExperiences.getState().reset(snapshot.experiences);
    useLanguages.getState().reset(snapshot.languages);
    useFrameworks.getState().reset(snapshot.frameworks);
    useTechnologies.getState().reset(snapshot.technologies);
    useTools.getState().reset(snapshot.tools);
    useDatabases.getState().reset(snapshot.databases);

    setApplied(false);
    setResult(null);
    setUpdates(null);
  }, [snapshot]);

  const scoreColor = (score: number) => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    return '#ef4444';
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">✨ Tailor Resume</h2>
      <p className="text-sm text-gray-600 mb-4">
        Paste a job description below and let AI optimize your resume for maximum ATS compatibility.
      </p>

      <textarea
        value={jd}
        onChange={(e) => setJd(e.target.value)}
        placeholder="Paste the full job description here..."
        rows={8}
        className="w-full p-3 border border-gray-300 rounded-md text-sm resize-y focus:outline-none focus:ring-2 focus:ring-blue-400"
        disabled={loading}
      />

      <div className="mt-3 flex gap-2">
        <button
          onClick={handleTailor}
          disabled={loading || jd.trim().length < 50}
          className="flex-1 py-2.5 px-4 bg-resume-800 text-white rounded-md font-semibold text-sm hover:bg-resume-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '⏳ Tailoring...' : '✨ Tailor My Resume'}
        </button>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4 space-y-4">
          {/* ATS Score */}
          <div className="p-4 bg-white rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700">ATS Score</span>
              <span
                className="text-3xl font-bold"
                style={{ color: scoreColor(result.ats_score) }}
              >
                {Math.round(result.ats_score)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(result.ats_score, 100)}%`,
                  backgroundColor: scoreColor(result.ats_score),
                }}
              />
            </div>
            <div className="grid grid-cols-2 gap-2 mt-3 text-xs text-gray-500">
              <div>Keywords: {Math.round(result.score_breakdown.keyword_score)}%</div>
              <div>Semantic: {Math.round(result.score_breakdown.semantic_score)}%</div>
              <div>Format: {Math.round(result.score_breakdown.format_score)}%</div>
              <div>Completeness: {Math.round(result.score_breakdown.completeness_score)}%</div>
            </div>
          </div>

          {/* Keywords Added */}
          {result.keywords_added.length > 0 && (
            <div className="p-3 bg-green-50 border border-green-200 rounded">
              <div className="text-sm font-semibold text-green-800 mb-1">Keywords Added</div>
              <div className="flex flex-wrap gap-1">
                {result.keywords_added.map((kw, i) => (
                  <span key={i} className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Changes Summary */}
          {result.changes_summary.length > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded">
              <div className="text-sm font-semibold text-blue-800 mb-1">Changes Made</div>
              <ul className="text-xs text-blue-700 space-y-1">
                {result.changes_summary.map((c, i) => (
                  <li key={i}>• {c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Apply / Revert */}
          <div className="flex gap-2">
            {!applied ? (
              <button
                onClick={applyChanges}
                className="flex-1 py-2 px-4 bg-green-600 text-white rounded-md font-semibold text-sm hover:bg-green-700"
              >
                ✅ Apply Changes
              </button>
            ) : (
              <button
                onClick={revertChanges}
                className="flex-1 py-2 px-4 bg-amber-500 text-white rounded-md font-semibold text-sm hover:bg-amber-600"
              >
                ↩️ Revert to Original
              </button>
            )}
          </div>

          {applied && (
            <div className="p-2 bg-green-50 border border-green-200 rounded text-xs text-green-700 text-center">
              Changes applied! Your resume preview has been updated.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TailorLayout;

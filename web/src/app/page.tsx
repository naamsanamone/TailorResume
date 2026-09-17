import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 max-w-6xl mx-auto">
        <div className="text-2xl font-bold tracking-tight">
          <span className="text-emerald-400">Tailor</span>Resume
        </div>
        <div className="flex gap-4">
          <Link
            href="/login"
            className="px-5 py-2 rounded-lg border border-slate-600 text-sm font-medium hover:bg-slate-700 transition-colors"
          >
            Log In
          </Link>
          <Link
            href="/register"
            className="px-5 py-2 rounded-lg bg-emerald-500 text-sm font-medium hover:bg-emerald-600 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="max-w-6xl mx-auto px-8 pt-24 pb-32">
        <div className="text-center space-y-8">
          <div className="inline-block px-4 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-sm font-medium">
            ATS Score 95+ Guaranteed
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-tight">
            Tailor Your Resume
            <br />
            <span className="text-emerald-400">Beat Every ATS</span>
          </h1>

          <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            AI-powered resume tailoring that analyzes job descriptions, matches
            your skills semantically, and rewrites your resume to score 95+ on
            any Applicant Tracking System.
          </p>

          <div className="flex gap-4 justify-center pt-4">
            <Link
              href="/register"
              className="px-8 py-3.5 rounded-xl bg-emerald-500 text-lg font-semibold hover:bg-emerald-600 transition-colors shadow-lg shadow-emerald-500/25"
            >
              Start Tailoring — Free
            </Link>
            <Link
              href="/login"
              className="px-8 py-3.5 rounded-xl border border-slate-600 text-lg font-medium hover:bg-slate-800 transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-32">
          <div className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/15 flex items-center justify-center text-2xl">
              🎯
            </div>
            <h3 className="text-xl font-semibold">Smart JD Analysis</h3>
            <p className="text-slate-400 leading-relaxed">
              AI extracts hard skills, soft skills, tools, and requirements from
              any job description in seconds.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-blue-500/15 flex items-center justify-center text-2xl">
              🧠
            </div>
            <h3 className="text-xl font-semibold">Semantic Matching</h3>
            <p className="text-slate-400 leading-relaxed">
              Goes beyond keyword matching — understands that &ldquo;React&rdquo; relates to
              &ldquo;frontend&rdquo; and &ldquo;UI development&rdquo; for deeper ATS scoring.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-purple-500/15 flex items-center justify-center text-2xl">
              📄
            </div>
            <h3 className="text-xl font-semibold">ATS-Safe Export</h3>
            <p className="text-slate-400 leading-relaxed">
              Single-column PDF and DOCX exports designed to pass every ATS
              parser — no tables, no text boxes, no graphics.
            </p>
          </div>
        </div>

        {/* Score breakdown */}
        <div className="mt-24 text-center space-y-8">
          <h2 className="text-3xl font-bold">Composite ATS Scoring</h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            Our 4-component scoring engine gives you a real ATS compatibility
            score, not just keyword counting.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
            {[
              { label: "Keyword Match", pct: "50%", color: "emerald" },
              { label: "Semantic Score", pct: "25%", color: "blue" },
              { label: "Format Score", pct: "15%", color: "purple" },
              { label: "Completeness", pct: "10%", color: "amber" },
            ].map((item) => (
              <div
                key={item.label}
                className="p-4 rounded-xl bg-slate-800/50 border border-slate-700"
              >
                <div className={`text-3xl font-bold text-${item.color}-400`}>
                  {item.pct}
                </div>
                <div className="text-sm text-slate-400 mt-1">{item.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-32 text-center p-12 rounded-3xl bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border border-emerald-500/20">
          <h2 className="text-3xl font-bold">
            Works with your Chrome Extension
          </h2>
          <p className="text-slate-400 mt-4 max-w-lg mx-auto">
            Integrates with LinkedApply Pro to tailor resumes right from
            LinkedIn job listings. One click, 95+ ATS score.
          </p>
          <Link
            href="/register"
            className="inline-block mt-8 px-8 py-3.5 rounded-xl bg-emerald-500 text-lg font-semibold hover:bg-emerald-600 transition-colors"
          >
            Get Started Now
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center text-sm text-slate-500">
        <p>© 2026 TailorResume. Built for job seekers who refuse to be filtered out.</p>
      </footer>
    </div>
  );
}

import { useContext } from 'react';
import {
  SortableRegion,
  SortableTemplateSection,
  useSectionLayoutRuntime,
} from '@/helpers/section-layout';
import { StateContext } from '@/modules/builder/resume/ResumeLayout';
import { pageStyle } from '@/templates/common/palette-ui';
import { useResumePalette } from '@/templates/common/resumePalette';
import type { ResumePalette } from '@/templates/common/resumePalette';
import type { IWorkIntrf, IEducation, IAwards, IItem } from '@/stores/index.interface';

/* ---------- Section Components ---------- */

const Header = ({ basics, p }: { basics: any; p: ResumePalette }) => (
  <div style={{ textAlign: 'center', marginBottom: '16px' }}>
    <h1 style={{ fontSize: '22px', fontWeight: 700, color: p.text, margin: 0, letterSpacing: '2px', textTransform: 'uppercase', fontFamily: p.headingFont }}>{basics.name}</h1>
    <div style={{ fontSize: '11px', color: p.muted, marginTop: '6px', display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
      {basics.phone && <span>{basics.phone}</span>}
      {basics.phone && basics.email && <span>|</span>}
      {basics.email && <span>{basics.email}</span>}
      {basics.email && basics.location?.city && <span>|</span>}
      {basics.location?.city && <span>{basics.location.city}</span>}
      {basics.url && <><span>|</span><span>{basics.url}</span></>}
    </div>
  </div>
);

const SectionTitle = ({ title, p }: { title: string; p: ResumePalette }) => (
  <div style={{ marginBottom: '8px', marginTop: '14px' }}>
    <h2 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1.5px', color: p.text, margin: 0, fontFamily: p.headingFont }}>{title}</h2>
    <div style={{ borderBottom: `1.5px solid ${p.text}`, marginTop: '3px' }} />
  </div>
);

const Summary = ({ summary, p }: { summary: string; p: ResumePalette }) =>
  summary ? (<div><SectionTitle title="Summary" p={p} /><p style={{ fontSize: '11px', color: p.text, lineHeight: 1.5, margin: 0 }}>{summary}</p></div>) : null;

const Work = ({ work, p }: { work: IWorkIntrf[]; p: ResumePalette }) =>
  work.length ? (
    <div>
      <SectionTitle title="Experience" p={p} />
      {work.map((w) => (
        <div key={w.id} style={{ marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <strong style={{ fontSize: '12px', color: p.text }}>{w.position}</strong>
            <span style={{ fontSize: '10px', color: p.muted }}>{w.years}</span>
          </div>
          <div style={{ fontSize: '11px', color: p.muted }}>{w.name}</div>
          {w.highlights.length > 0 && (
            <ul style={{ paddingLeft: '16px', margin: '3px 0 0' }}>
              {w.highlights.map((h, i) => <li key={i} style={{ fontSize: '11px', color: p.text, lineHeight: 1.5 }}>{h}</li>)}
            </ul>
          )}
        </div>
      ))}
    </div>
  ) : null;

const Education = ({ education, p }: { education: IEducation[]; p: ResumePalette }) =>
  education.length ? (
    <div>
      <SectionTitle title="Education" p={p} />
      {education.map((e) => (
        <div key={e.id} style={{ marginBottom: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <strong style={{ fontSize: '12px', color: p.text }}>{e.institution}</strong>
            <span style={{ fontSize: '10px', color: p.muted }}>{e.startDate ? `${new Date(e.startDate.toString()).getFullYear()}` : ''}{e.endDate ? ` – ${new Date(e.endDate.toString()).getFullYear()}` : e.isStudyingHere ? ' – Present' : ''}</span>
          </div>
          <div style={{ fontSize: '11px', color: p.muted, fontStyle: 'italic' }}>{e.studyType}{e.area ? ` in ${e.area}` : ''}{e.score ? ` | GPA: ${e.score}` : ''}</div>
        </div>
      ))}
    </div>
  ) : null;

const Skills = ({ languages, frameworks, tools, p }: { languages: IItem[]; frameworks: IItem[]; tools: IItem[]; p: ResumePalette }) => {
  const cats = [
    { label: 'Languages', items: languages },
    { label: 'Frameworks', items: frameworks },
    { label: 'Tools', items: tools },
  ].filter(c => c.items.length > 0);
  return cats.length ? (
    <div>
      <SectionTitle title="Skills" p={p} />
      {cats.map((c, i) => (
        <div key={i} style={{ fontSize: '11px', color: p.text, marginBottom: '3px' }}>
          <strong>{c.label}: </strong>{c.items.map(s => s.name).join(', ')}
        </div>
      ))}
    </div>
  ) : null;
};

const Awards = ({ awards, p }: { awards: IAwards[]; p: ResumePalette }) =>
  awards.length ? (
    <div>
      <SectionTitle title="Awards" p={p} />
      {awards.map((a) => (
        <div key={a.id} style={{ marginBottom: '6px' }}>
          <strong style={{ fontSize: '11px', color: p.text }}>{a.title}</strong>
          {a.awarder && <span style={{ fontSize: '10px', color: p.muted }}> — {a.awarder}</span>}
          {a.summary && <p style={{ fontSize: '10px', color: p.muted, margin: '2px 0 0' }}>{a.summary}</p>}
        </div>
      ))}
    </div>
  ) : null;

/* ---------- Main Template ---------- */

export default function SwissSingleTemplate() {
  const data = useContext(StateContext);
  const { regions } = useSectionLayoutRuntime();
  const p = useResumePalette();

  const renderSection = (id: string) => {
    switch (id) {
      case 'summary': return <Summary summary={data.basics.summary} p={p} />;
      case 'work': return <Work work={data.work} p={p} />;
      case 'education': return <Education education={data.education} p={p} />;
      case 'skills': return <Skills languages={data.skills.languages} frameworks={data.skills.frameworks} tools={data.skills.tools} p={p} />;
      case 'awards': return <Awards awards={data.awards} p={p} />;
      default: return null;
    }
  };

  return (
    <div style={{ ...pageStyle(p), padding: '36px 44px' }}>
      <Header basics={data.basics} p={p} />
      <SortableRegion regionId="main" items={regions.main}>
        {(id) => (<SortableTemplateSection key={id} id={id}>{renderSection(id)}</SortableTemplateSection>)}
      </SortableRegion>
    </div>
  );
}

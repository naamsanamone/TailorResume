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

const Heading = ({ title, p }: { title: string; p: ResumePalette }) => (
  <h2 style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', color: p.primary, margin: '16px 0 8px', paddingBottom: '4px', borderBottom: `2px solid ${p.accent}`, fontFamily: p.headingFont, letterSpacing: '0.5px' }}>{title}</h2>
);

const Summary = ({ summary, p }: { summary: string; p: ResumePalette }) =>
  summary ? (<div><Heading title="Summary" p={p} /><p style={{ fontSize: '11px', color: p.text, lineHeight: 1.6, margin: 0 }}>{summary}</p></div>) : null;

const Work = ({ work, p }: { work: IWorkIntrf[]; p: ResumePalette }) =>
  work.length ? (
    <div>
      <Heading title="Experience" p={p} />
      {work.map((w) => (
        <div key={w.id} style={{ marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <strong style={{ fontSize: '12px', color: p.text }}>{w.position}</strong>
            <span style={{ fontSize: '10px', color: p.muted }}>{w.years}</span>
          </div>
          <div style={{ fontSize: '11px', color: p.primary, fontWeight: 500 }}>{w.name}</div>
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
      <Heading title="Education" p={p} />
      {education.map((e) => (
        <div key={e.id} style={{ marginBottom: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
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
      <Heading title="Skills" p={p} />
      {cats.map((c, i) => (
        <div key={i} style={{ fontSize: '11px', color: p.text, marginBottom: '3px' }}>
          <strong style={{ color: p.primary }}>{c.label}: </strong>{c.items.map(s => s.name).join(', ')}
        </div>
      ))}
    </div>
  ) : null;
};

const Awards = ({ awards, p }: { awards: IAwards[]; p: ResumePalette }) =>
  awards.length ? (
    <div>
      <Heading title="Awards" p={p} />
      {awards.map((a) => (
        <div key={a.id} style={{ marginBottom: '5px' }}>
          <strong style={{ fontSize: '11px', color: p.text }}>{a.title}</strong>
          {a.awarder && <span style={{ fontSize: '10px', color: p.muted }}> — {a.awarder}</span>}
          {a.summary && <p style={{ fontSize: '10px', color: p.muted, margin: '2px 0 0' }}>{a.summary}</p>}
        </div>
      ))}
    </div>
  ) : null;

export default function RmModernTemplate() {
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
      {/* Header with accent underline */}
      <div style={{ textAlign: 'center', marginBottom: '12px', paddingBottom: '12px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: p.text, margin: 0, fontFamily: p.headingFont }}>{data.basics.name}</h1>
        <div style={{ width: '60px', height: '3px', background: p.accent, margin: '8px auto 0' }} />
        {data.basics.label && <div style={{ fontSize: '12px', color: p.primary, marginTop: '6px', fontWeight: 500 }}>{data.basics.label}</div>}
        <div style={{ fontSize: '10px', color: p.muted, marginTop: '5px', display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {data.basics.phone && <span>{data.basics.phone}</span>}
          {data.basics.email && <><span>|</span><span>{data.basics.email}</span></>}
          {data.basics.location?.city && <><span>|</span><span>{data.basics.location.city}</span></>}
          {data.basics.url && <><span>|</span><span>{data.basics.url}</span></>}
        </div>
      </div>
      <SortableRegion regionId="main" items={regions.main}>
        {(id) => (<SortableTemplateSection key={id} id={id}>{renderSection(id)}</SortableTemplateSection>)}
      </SortableRegion>
    </div>
  );
}

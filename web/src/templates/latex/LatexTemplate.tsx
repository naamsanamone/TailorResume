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

const Header = ({ basics, p }: { basics: any; p: ResumePalette }) => (
  <div style={{ textAlign: 'center', marginBottom: '14px', paddingBottom: '10px', borderBottom: `1px solid ${p.divider}` }}>
    <h1 style={{ fontSize: '24px', fontWeight: 700, color: p.text, margin: 0, fontFamily: p.headingFont }}>{basics.name}</h1>
    <div style={{ fontSize: '11px', color: p.muted, marginTop: '5px', display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
      {basics.phone && <span>{basics.phone}</span>}
      {basics.phone && basics.email && <span>|</span>}
      {basics.email && <span>{basics.email}</span>}
      {basics.url && <><span>|</span><span>{basics.url}</span></>}
      {basics.location?.city && <><span>|</span><span>{basics.location.city}</span></>}
    </div>
  </div>
);

const Heading = ({ title, p }: { title: string; p: ResumePalette }) => (
  <h2 style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1.5px', color: p.text, margin: '12px 0 6px', paddingBottom: '3px', borderBottom: `1px solid ${p.divider}`, fontFamily: p.headingFont }}>{title}</h2>
);

const Summary = ({ summary, p }: { summary: string; p: ResumePalette }) =>
  summary ? (<div><Heading title="Summary" p={p} /><p style={{ fontSize: '11px', color: p.text, lineHeight: 1.5, margin: 0 }}>{summary}</p></div>) : null;

const Work = ({ work, p }: { work: IWorkIntrf[]; p: ResumePalette }) =>
  work.length ? (
    <div>
      <Heading title="Experience" p={p} />
      {work.map((w) => (
        <div key={w.id} style={{ marginBottom: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <strong style={{ fontSize: '11px', color: p.text }}>{w.position}</strong>
            <span style={{ fontSize: '10px', color: p.muted }}>{w.years}</span>
          </div>
          <div style={{ fontSize: '10px', color: p.muted }}>{w.name}</div>
          {w.highlights.length > 0 && (
            <ul style={{ paddingLeft: '14px', margin: '2px 0 0' }}>
              {w.highlights.map((h, i) => <li key={i} style={{ fontSize: '10px', color: p.text, lineHeight: 1.5 }}>{h}</li>)}
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
        <div key={e.id} style={{ marginBottom: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <strong style={{ fontSize: '11px', color: p.text }}>{e.institution}</strong>
            <span style={{ fontSize: '10px', color: p.muted }}>{e.startDate ? `${new Date(e.startDate.toString()).getFullYear()}` : ''}{e.endDate ? ` – ${new Date(e.endDate.toString()).getFullYear()}` : e.isStudyingHere ? ' – Present' : ''}</span>
          </div>
          <div style={{ fontSize: '10px', color: p.muted, fontStyle: 'italic' }}>{e.studyType}{e.area ? ` in ${e.area}` : ''}{e.score ? ` | ${e.score}` : ''}</div>
        </div>
      ))}
    </div>
  ) : null;

const Skills = ({ languages, frameworks, tools, p }: { languages: IItem[]; frameworks: IItem[]; tools: IItem[]; p: ResumePalette }) => {
  const all = [...languages, ...frameworks, ...tools].filter(Boolean);
  return all.length ? (
    <div>
      <Heading title="Skills" p={p} />
      <div style={{ fontSize: '11px', color: p.text, lineHeight: 1.6 }}>{all.map(s => s.name).join(' • ')}</div>
    </div>
  ) : null;
};

const Awards = ({ awards, p }: { awards: IAwards[]; p: ResumePalette }) =>
  awards.length ? (
    <div>
      <Heading title="Awards" p={p} />
      {awards.map((a) => (
        <div key={a.id} style={{ marginBottom: '4px' }}>
          <strong style={{ fontSize: '11px', color: p.text }}>{a.title}</strong>
          {a.awarder && <span style={{ fontSize: '10px', color: p.muted }}> — {a.awarder}</span>}
        </div>
      ))}
    </div>
  ) : null;

export default function LatexTemplate() {
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
    <div style={{ ...pageStyle(p), padding: '32px 40px' }}>
      <Header basics={data.basics} p={p} />
      <SortableRegion regionId="main" items={regions.main}>
        {(id) => (<SortableTemplateSection key={id} id={id}>{renderSection(id)}</SortableTemplateSection>)}
      </SortableRegion>
    </div>
  );
}

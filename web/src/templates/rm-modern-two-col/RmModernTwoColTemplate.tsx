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
  <h2 style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: p.primary, margin: '14px 0 6px', paddingBottom: '3px', borderBottom: `2px solid ${p.accent}`, fontFamily: p.headingFont }}>{title}</h2>
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
          <div style={{ fontSize: '10px', color: p.primary }}>{w.name}</div>
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
          <strong style={{ fontSize: '11px', color: p.text }}>{e.institution}</strong>
          <div style={{ fontSize: '10px', color: p.muted, fontStyle: 'italic' }}>{e.studyType}{e.area ? ` in ${e.area}` : ''}</div>
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
        <div key={i} style={{ fontSize: '10px', color: p.text, marginBottom: '3px' }}>
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
        <div key={a.id} style={{ marginBottom: '4px' }}>
          <strong style={{ fontSize: '10px', color: p.text }}>{a.title}</strong>
          {a.awarder && <span style={{ fontSize: '10px', color: p.muted }}> — {a.awarder}</span>}
        </div>
      ))}
    </div>
  ) : null;

export default function RmModernTwoColTemplate() {
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
    <div style={{ ...pageStyle(p), padding: 0 }}>
      {/* Header spanning full width */}
      <div style={{ textAlign: 'center', padding: '28px 40px 14px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: p.text, margin: 0, fontFamily: p.headingFont }}>{data.basics.name}</h1>
        <div style={{ width: '50px', height: '3px', background: p.accent, margin: '6px auto 0' }} />
        {data.basics.label && <div style={{ fontSize: '11px', color: p.primary, marginTop: '5px' }}>{data.basics.label}</div>}
        <div style={{ fontSize: '10px', color: p.muted, marginTop: '4px', display: 'flex', justifyContent: 'center', gap: '6px', flexWrap: 'wrap' }}>
          {data.basics.phone && <span>{data.basics.phone}</span>}
          {data.basics.email && <><span>|</span><span>{data.basics.email}</span></>}
          {data.basics.location?.city && <><span>|</span><span>{data.basics.location.city}</span></>}
          {data.basics.url && <><span>|</span><span>{data.basics.url}</span></>}
        </div>
      </div>
      {/* Two columns */}
      <div style={{ display: 'flex', padding: '0 36px 28px' }}>
        <div style={{ flex: '0 0 63%', paddingRight: '18px' }}>
          <SortableRegion regionId="main" items={regions.main}>
            {(id) => (<SortableTemplateSection key={id} id={id}>{renderSection(id)}</SortableTemplateSection>)}
          </SortableRegion>
        </div>
        <div style={{ flex: '0 0 37%', paddingLeft: '18px', borderLeft: `2px solid ${p.accent}` }}>
          <SortableRegion regionId="sidebar" items={regions.sidebar}>
            {(id) => (<SortableTemplateSection key={id} id={id}>{renderSection(id)}</SortableTemplateSection>)}
          </SortableRegion>
        </div>
      </div>
    </div>
  );
}

import { SectionValidator } from '@/helpers/common/components/ValidSectionRenderer';
import { formatDateRange } from '@/templates/common/palette-ui';
import type { ResumePalette } from '@/templates/common/resumePalette';

export function Education({ education, p }: { education: any[]; p: ResumePalette }) {
  return (
    <SectionValidator value={education}>
      <section style={{ marginBottom: 16 }}>
        <h2
          style={{
            fontSize: 13,
            fontWeight: 700,
            textTransform: 'uppercase',
            color: p.text,
            borderBottom: `2px solid ${p.primary}`,
            paddingBottom: 4,
            marginBottom: 8,
            margin: 0,
            fontFamily: p.headingFont,
            letterSpacing: '0.04em',
          }}
        >
          Education
        </h2>
        {education.map((e: any) => (
          <div key={e.id} style={{ marginBottom: 8 }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
              }}
            >
              <strong style={{ fontSize: 12, color: p.text, fontFamily: p.headingFont }}>
                {e.institution}
              </strong>
              <span style={{ fontSize: 11, color: p.muted, whiteSpace: 'nowrap' }}>
                {formatDateRange(e.startDate, e.endDate, e.isStudyingHere)}
              </span>
            </div>
            <div style={{ fontSize: 11, color: p.text, fontStyle: 'italic', fontFamily: p.bodyFont }}>
              {e.studyType}
              {e.area ? `, ${e.area}` : ''}
              {e.score ? ` — GPA: ${e.score}` : ''}
            </div>
          </div>
        ))}
      </section>
    </SectionValidator>
  );
}

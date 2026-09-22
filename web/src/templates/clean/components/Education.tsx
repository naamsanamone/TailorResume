import { SectionValidator } from '@/helpers/common/components/ValidSectionRenderer';
import { formatDateRange } from '@/templates/common/palette-ui';
import type { ResumePalette } from '@/templates/common/resumePalette';

export function Education({ education, p }: { education: any[]; p: ResumePalette }) {
  return (
    <SectionValidator value={education}>
      <section style={{ marginBottom: 24 }}>
        <h2
          style={{
            fontFamily: p.headingFont,
            fontSize: 14,
            fontWeight: 400,
            color: p.muted,
            textTransform: 'uppercase',
            letterSpacing: '0.18em',
            margin: '0 0 10px 0',
            paddingBottom: 6,
            borderBottom: `1px solid ${p.divider}`,
          }}
        >
          Education
        </h2>

        {education.map((e: any) => (
          <div key={e.id} style={{ marginBottom: 10 }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
              }}
            >
              <strong style={{ fontSize: 12, fontWeight: 600, color: p.text }}>
                {e.studyType}
                {e.area ? `, ${e.area}` : ''}
              </strong>
              <span style={{ fontSize: 10.5, color: p.muted, whiteSpace: 'nowrap' }}>
                {formatDateRange(e.startDate, e.endDate, e.isStudyingHere)}
              </span>
            </div>
            <div style={{ fontSize: 11, color: p.muted, marginTop: 2 }}>{e.institution}</div>
            {e.score && (
              <div style={{ fontSize: 10.5, color: p.text, marginTop: 2 }}>GPA: {e.score}</div>
            )}
          </div>
        ))}
      </section>
    </SectionValidator>
  );
}

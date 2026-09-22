import { SectionValidator } from '@/helpers/common/components/ValidSectionRenderer';
import { formatDateRange, RichText } from '@/templates/common/palette-ui';
import type { ResumePalette } from '@/templates/common/resumePalette';

export function Work({ work, p }: { work: any[]; p: ResumePalette }) {
  return (
    <SectionValidator value={work}>
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
          Experience
        </h2>

        {work.map((w: any) => (
          <div key={w.id} style={{ marginBottom: 16 }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
              }}
            >
              <strong style={{ fontSize: 12, fontWeight: 600, color: p.text }}>
                {w.position}
              </strong>
              <span style={{ fontSize: 10.5, color: p.muted, whiteSpace: 'nowrap' }}>
                {w.years || formatDateRange(w.startDate, w.endDate, w.isWorkingHere)}
              </span>
            </div>

            <div style={{ fontSize: 11, color: p.muted, marginTop: 2 }}>{w.name}</div>

            <RichText html={w.summary} p={p} />
          </div>
        ))}
      </section>
    </SectionValidator>
  );
}

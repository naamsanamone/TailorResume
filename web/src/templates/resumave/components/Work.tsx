import { SectionValidator } from '@/helpers/common/components/ValidSectionRenderer';
import { formatDateRange } from '@/templates/common/palette-ui';
import type { ResumePalette } from '@/templates/common/resumePalette';

export function Work({ work, p }: { work: any[]; p: ResumePalette }) {
  return (
    <SectionValidator value={work}>
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
          Experience
        </h2>
        {work.map((w: any) => (
          <div key={w.id} style={{ marginBottom: 12 }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
              }}
            >
              <strong style={{ fontSize: 12, color: p.text, fontFamily: p.headingFont }}>
                {w.position}
              </strong>
              <span style={{ fontSize: 11, color: p.muted, whiteSpace: 'nowrap' }}>
                {formatDateRange(w.startDate, w.endDate, w.isWorkingHere)}
              </span>
            </div>
            <div style={{ fontSize: 11, color: p.muted, fontFamily: p.bodyFont }}>{w.name}</div>
            {w.highlights && w.highlights.length > 0 && (
              <ul
                style={{
                  paddingLeft: 16,
                  margin: '4px 0 0 0',
                  listStyleType: 'disc',
                }}
              >
                {w.highlights.map((h: string, i: number) => (
                  <li
                    key={i}
                    style={{
                      fontSize: 11,
                      color: p.text,
                      lineHeight: 1.5,
                      fontFamily: p.bodyFont,
                    }}
                  >
                    {h}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </section>
    </SectionValidator>
  );
}

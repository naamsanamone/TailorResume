import { SectionValidator } from '@/helpers/common/components/ValidSectionRenderer';
import type { ResumePalette } from '@/templates/common/resumePalette';

export function Awards({ awards, p }: { awards: any[]; p: ResumePalette }) {
  return (
    <SectionValidator value={awards}>
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
          Awards &amp; Certifications
        </h2>
        {awards.map((a: any) => (
          <div key={a.id} style={{ marginBottom: 6 }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
              }}
            >
              <strong style={{ fontSize: 11, color: p.text, fontFamily: p.headingFont }}>
                {a.title}
              </strong>
              {a.date && (
                <span style={{ fontSize: 10, color: p.muted, whiteSpace: 'nowrap' }}>
                  {a.date}
                </span>
              )}
            </div>
            {a.awarder && (
              <div style={{ fontSize: 11, color: p.muted, fontFamily: p.bodyFont }}>
                {a.awarder}
              </div>
            )}
          </div>
        ))}
      </section>
    </SectionValidator>
  );
}

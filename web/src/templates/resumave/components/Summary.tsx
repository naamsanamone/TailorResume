import { SectionValidator } from '@/helpers/common/components/ValidSectionRenderer';
import type { ResumePalette } from '@/templates/common/resumePalette';

export function Summary({ summary, p }: { summary: string; p: ResumePalette }) {
  return (
    <SectionValidator value={summary}>
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
          Summary
        </h2>
        <p
          style={{
            fontSize: 11,
            color: p.text,
            lineHeight: 1.5,
            margin: 0,
            fontFamily: p.bodyFont,
          }}
        >
          {summary}
        </p>
      </section>
    </SectionValidator>
  );
}

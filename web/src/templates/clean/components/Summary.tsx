import { SectionValidator } from '@/helpers/common/components/ValidSectionRenderer';
import { RichText } from '@/templates/common/palette-ui';
import type { ResumePalette } from '@/templates/common/resumePalette';

export function Summary({ summary, p }: { summary: string; p: ResumePalette }) {
  return (
    <SectionValidator value={summary}>
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
          Summary
        </h2>
        <RichText html={summary} p={p} />
      </section>
    </SectionValidator>
  );
}

import type { ResumePalette } from '@/templates/common/resumePalette';

export function Skills({
  languages,
  frameworks,
  tools,
  p,
}: {
  languages: { name: string }[];
  frameworks: { name: string }[];
  tools: { name: string }[];
  p: ResumePalette;
}) {
  const all = [...(languages || []), ...(frameworks || []), ...(tools || [])];

  if (all.length === 0) return null;

  return (
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
        Skills
      </h2>
      <div
        style={{
          fontSize: 11,
          color: p.text,
          lineHeight: 1.6,
          fontFamily: p.bodyFont,
        }}
      >
        {all.map((s) => s.name).join(' • ')}
      </div>
    </section>
  );
}

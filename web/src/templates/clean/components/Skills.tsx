import type { ResumePalette } from '@/templates/common/resumePalette';

type SkillGroup = { name: string; level?: number }[];

interface SkillsProps {
  skills: {
    languages: SkillGroup;
    frameworks: SkillGroup;
    technologies: SkillGroup;
    tools: SkillGroup;
    databases: SkillGroup;
  };
  p: ResumePalette;
}

export function Skills({ skills, p }: SkillsProps) {
  const categories: { label: string; items: SkillGroup }[] = [
    { label: 'Languages', items: skills.languages },
    { label: 'Frameworks', items: skills.frameworks },
    { label: 'Technologies', items: skills.technologies },
    { label: 'Tools', items: skills.tools },
    { label: 'Databases', items: skills.databases },
  ].filter((c) => c.items?.length > 0);

  if (categories.length === 0) return null;

  return (
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
        Skills
      </h2>

      {categories.map((cat) => (
        <div key={cat.label} style={{ marginBottom: 8 }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: p.text }}>{cat.label}: </span>
          <span style={{ fontSize: 11, color: p.text }}>
            {cat.items.map((s) => s.name).join(', ')}
          </span>
        </div>
      ))}
    </section>
  );
}

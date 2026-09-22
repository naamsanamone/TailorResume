import type { ResumePalette } from '@/templates/common/resumePalette';

type Basics = {
  name: string;
  label: string;
  email?: string;
  phone?: string;
  url?: string;
  location?: { city?: string };
};

export function Header({ basics, p }: { basics: Basics; p: ResumePalette }) {
  const contactItems = [basics.phone, basics.email, basics.location?.city, basics.url].filter(
    Boolean
  );

  return (
    <div style={{ marginBottom: 20 }}>
      <h1
        style={{
          margin: 0,
          fontSize: 28,
          fontWeight: 700,
          color: p.text,
          fontFamily: p.headingFont,
          letterSpacing: '0.01em',
        }}
      >
        {basics.name}
      </h1>
      {basics.label && (
        <div style={{ fontSize: 13, color: p.muted, marginTop: 2, fontFamily: p.bodyFont }}>
          {basics.label}
        </div>
      )}
      {contactItems.length > 0 && (
        <div
          style={{
            fontSize: 11,
            color: p.muted,
            marginTop: 8,
            fontFamily: p.bodyFont,
          }}
        >
          {contactItems.join('  |  ')}
        </div>
      )}
    </div>
  );
}

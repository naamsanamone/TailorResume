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
  const contacts = [basics.email, basics.phone, basics.location?.city, basics.url].filter(
    Boolean
  );

  return (
    <div
      style={{
        textAlign: 'center',
        paddingBottom: 28,
        marginBottom: 28,
      }}
    >
      <h1
        style={{
          fontFamily: p.headingFont,
          fontSize: 32,
          fontWeight: 300,
          margin: 0,
          color: p.text,
          letterSpacing: '0.04em',
        }}
      >
        {basics.name}
      </h1>

      {basics.label && (
        <div
          style={{
            fontSize: 12,
            color: p.muted,
            marginTop: 6,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            fontFamily: p.bodyFont,
          }}
        >
          {basics.label}
        </div>
      )}

      {contacts.length > 0 && (
        <div
          style={{
            fontSize: 10.5,
            color: p.muted,
            marginTop: 12,
            fontFamily: p.bodyFont,
          }}
        >
          {contacts.join('  |  ')}
        </div>
      )}
    </div>
  );
}

/**
 * TailorResume — Main ResumePDF Document Component
 * Cloned from: github.com/xitanggg/open-resume (MIT License)
 * Renders a complete ATS-friendly PDF using @react-pdf/renderer
 */
import { Page, View, Document, Font, Text } from "@react-pdf/renderer";
import { styles, spacing, DEFAULT_FONT_COLOR } from "./styles";
import { ResumePDFSection, ResumePDFText, ResumePDFBulletList } from "./common";
import type { MappedResume } from "./types";

// Register Roboto font for consistent rendering
Font.register({
  family: "Roboto",
  fonts: [
    { src: "https://cdnjs.cloudflare.com/ajax/libs/ink/3.1.10/fonts/Roboto/roboto-light-webfont.ttf", fontWeight: 300 },
    { src: "https://cdnjs.cloudflare.com/ajax/libs/ink/3.1.10/fonts/Roboto/roboto-regular-webfont.ttf", fontWeight: 400 },
    { src: "https://cdnjs.cloudflare.com/ajax/libs/ink/3.1.10/fonts/Roboto/roboto-medium-webfont.ttf", fontWeight: 500 },
    { src: "https://cdnjs.cloudflare.com/ajax/libs/ink/3.1.10/fonts/Roboto/roboto-bold-webfont.ttf", fontWeight: 700 },
  ],
});

// Disable hyphenation for clean ATS text
Font.registerHyphenationCallback((word) => [word]);

export const ResumePDF = ({
  resume,
  isPDF = false,
}: {
  resume: MappedResume;
  isPDF?: boolean;
}) => {
  const { profile, workExperiences, educations, projects, skills, customs } = resume;

  return (
    <Document
      title={`${profile.name} Resume`}
      author={profile.name}
      producer="TailorResume"
    >
      <Page
        size="LETTER"
        style={{
          ...styles.flexCol,
          color: DEFAULT_FONT_COLOR,
          fontFamily: "Roboto",
          fontSize: "10pt",
        }}
      >
        <View
          style={{
            ...styles.flexCol,
            padding: `${spacing[8]} ${spacing[20]}`,
          }}
        >
          {/* HEADER — Name + Contact */}
          <View style={{ alignItems: "center", marginBottom: spacing["1"] }}>
            <Text
              style={{
                fontWeight: "bold",
                fontSize: "20pt",
                textTransform: "uppercase",
                letterSpacing: "0.5pt",
              }}
            >
              {profile.name}
            </Text>
            {/* Contact line */}
            {(() => {
              const parts: string[] = [];
              if (profile.phone) parts.push(profile.phone);
              if (profile.email) parts.push(profile.email);
              // Split combined URL field back into parts
              if (profile.url) {
                profile.url.split(" | ").forEach((u) => {
                  if (u.trim()) parts.push(u.trim());
                });
              }
              if (profile.location) parts.push(profile.location);
              return parts.length > 0 ? (
                <Text style={{ fontSize: "9pt", marginTop: spacing["0.5"] }}>
                  {parts.join("  |  ")}
                </Text>
              ) : null;
            })()}
          </View>

          {/* SUMMARY */}
          {profile.summary && (
            <ResumePDFSection heading="PROFESSIONAL SUMMARY">
              <ResumePDFText style={{ lineHeight: 1.3 }}>
                {profile.summary}
              </ResumePDFText>
            </ResumePDFSection>
          )}

          {/* SKILLS */}
          {skills.descriptions.length > 0 && (
            <ResumePDFSection heading="TECHNICAL SKILLS">
              <View style={{ ...styles.flexCol }}>
                {skills.descriptions.map((desc, idx) => {
                  // Parse "Category: values" format
                  const colonIdx = desc.indexOf(":");
                  if (colonIdx > 0) {
                    const catName = desc.slice(0, colonIdx).trim();
                    const catVal = desc.slice(colonIdx + 1).trim();
                    return (
                      <View key={idx} style={{ ...styles.flexRow, marginBottom: spacing["0.5"] }}>
                        <ResumePDFText bold={true}>{catName}: </ResumePDFText>
                        <ResumePDFText style={{ flexGrow: 1, flexBasis: 0 }}>
                          {catVal}
                        </ResumePDFText>
                      </View>
                    );
                  }
                  return (
                    <ResumePDFText key={idx}>{desc}</ResumePDFText>
                  );
                })}
              </View>
            </ResumePDFSection>
          )}

          {/* EXPERIENCE */}
          {workExperiences.length > 0 && (
            <ResumePDFSection heading="PROFESSIONAL EXPERIENCE">
              {workExperiences.map(({ company, jobTitle, date, descriptions }, idx) => {
                const hideCompanyName =
                  idx > 0 && company === workExperiences[idx - 1].company;
                return (
                  <View key={idx} style={idx !== 0 ? { marginTop: spacing["2"] } : {}}>
                    {!hideCompanyName && (
                      <ResumePDFText bold={true}>{company}</ResumePDFText>
                    )}
                    <View
                      style={{
                        ...styles.flexRowBetween,
                        marginTop: hideCompanyName ? "-" + spacing["1"] : spacing["1"],
                      }}
                    >
                      <ResumePDFText style={{ fontStyle: "italic" }}>{jobTitle}</ResumePDFText>
                      <ResumePDFText>{date}</ResumePDFText>
                    </View>
                    <View style={{ ...styles.flexCol, marginTop: spacing["1"] }}>
                      <ResumePDFBulletList items={descriptions} />
                    </View>
                  </View>
                );
              })}
            </ResumePDFSection>
          )}

          {/* PROJECTS */}
          {projects.length > 0 && (
            <ResumePDFSection heading="PROJECTS">
              {projects.map(({ project, date, descriptions }, idx) => (
                <View key={idx}>
                  <View
                    style={{
                      ...styles.flexRowBetween,
                      marginTop: spacing["0.5"],
                    }}
                  >
                    <ResumePDFText bold={true}>{project}</ResumePDFText>
                    <ResumePDFText>{date}</ResumePDFText>
                  </View>
                  <View style={{ ...styles.flexCol, marginTop: spacing["0.5"] }}>
                    <ResumePDFBulletList items={descriptions} />
                  </View>
                </View>
              ))}
            </ResumePDFSection>
          )}

          {/* EDUCATION */}
          {educations.length > 0 && (
            <ResumePDFSection heading="EDUCATION">
              {educations.map(({ school, degree, date, gpa, descriptions }, idx) => {
                const hideSchoolName =
                  idx > 0 && school === educations[idx - 1].school;
                const showDescriptions = descriptions.join("") !== "";
                const degreeText = gpa
                  ? `${degree} - ${Number(gpa) ? gpa + " GPA" : gpa}`
                  : degree;
                return (
                  <View key={idx}>
                    {!hideSchoolName && (
                      <ResumePDFText bold={true}>{school}</ResumePDFText>
                    )}
                    <View
                      style={{
                        ...styles.flexRowBetween,
                        marginTop: hideSchoolName ? "-" + spacing["1"] : spacing["1"],
                      }}
                    >
                      <ResumePDFText style={{ fontStyle: "italic" }}>{degreeText}</ResumePDFText>
                      <ResumePDFText>{date}</ResumePDFText>
                    </View>
                    {showDescriptions && (
                      <View style={{ ...styles.flexCol, marginTop: spacing["1"] }}>
                        <ResumePDFBulletList items={descriptions} />
                      </View>
                    )}
                  </View>
                );
              })}
            </ResumePDFSection>
          )}

          {/* CUSTOM SECTIONS (Certifications, Achievements, etc.) */}
          {customs.map((custom, idx) => (
            <ResumePDFSection key={idx} heading={custom.heading.toUpperCase()}>
              <View style={{ ...styles.flexCol }}>
                <ResumePDFBulletList items={custom.descriptions} />
              </View>
            </ResumePDFSection>
          ))}
        </View>
      </Page>
    </Document>
  );
};

/**
 * TailorResume — Common PDF primitives
 * Cloned from: github.com/xitanggg/open-resume (MIT License)
 */
import { Text, View, Link } from "@react-pdf/renderer";
import type { Style } from "@react-pdf/types";
import { styles, spacing, DEFAULT_FONT_COLOR } from "./styles";

export const ResumePDFSection = ({
  heading,
  style = {},
  children,
}: {
  heading?: string;
  style?: Style;
  children: React.ReactNode;
}) => (
  <View
    style={{
      ...styles.flexCol,
      gap: spacing["2"],
      marginTop: spacing["5"],
      ...style,
    }}
  >
    {heading && (
      <View
        style={{
          ...styles.flexRow,
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: "#000",
          paddingBottom: spacing["0.5"],
        }}
      >
        <Text
          style={{
            fontWeight: "bold",
            letterSpacing: "0.3pt",
            textTransform: "uppercase",
            fontSize: "11pt",
          }}
        >
          {heading}
        </Text>
      </View>
    )}
    {children}
  </View>
);

export const ResumePDFText = ({
  bold = false,
  themeColor,
  style = {},
  children,
}: {
  bold?: boolean;
  themeColor?: string;
  style?: Style;
  children: React.ReactNode;
}) => {
  return (
    <Text
      style={{
        color: themeColor || DEFAULT_FONT_COLOR,
        fontWeight: bold ? "bold" : "normal",
        ...style,
      }}
    >
      {children}
    </Text>
  );
};

export const ResumePDFBulletList = ({
  items,
  showBulletPoints = true,
}: {
  items: string[];
  showBulletPoints?: boolean;
}) => {
  return (
    <>
      {items.map((item, idx) => {
        if (!item || !item.trim()) return null;
        // Strip leading bullet chars if present
        const cleanItem = item.replace(/^[•\-–·*▪►○]\s*/, "").trim();
        if (!cleanItem) return null;
        return (
          <View style={{ ...styles.flexRow }} key={idx}>
            {showBulletPoints && (
              <ResumePDFText
                style={{
                  paddingLeft: spacing["2"],
                  paddingRight: spacing["2"],
                  lineHeight: 1.3,
                }}
                bold={true}
              >
                {"•"}
              </ResumePDFText>
            )}
            {/* flexGrow & flexBasis fix for react-pdf text wrapping bug
                https://github.com/diegomura/react-pdf/issues/2182 */}
            <ResumePDFText style={{ lineHeight: 1.3, flexGrow: 1, flexBasis: 0 }}>
              {cleanItem}
            </ResumePDFText>
          </View>
        );
      })}
    </>
  );
};

export const ResumePDFLink = ({
  src,
  isPDF,
  children,
}: {
  src: string;
  isPDF: boolean;
  children: React.ReactNode;
}) => {
  if (isPDF) {
    return (
      <Link src={src} style={{ textDecoration: "none" }}>
        {children}
      </Link>
    );
  }
  return (
    <a
      href={src}
      style={{ textDecoration: "none" }}
      target="_blank"
      rel="noreferrer"
    >
      {children}
    </a>
  );
};

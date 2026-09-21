/**
 * TailorResume — OpenResume-based PDF styles
 * Cloned from: github.com/xitanggg/open-resume (MIT License)
 * Adapted for TailorResume data schema
 */
import { StyleSheet } from "@react-pdf/renderer";

// Tailwindcss Spacing Design System: https://tailwindcss.com/docs/theme#spacing
// Converted from rem to pt (1rem = 12pt) for react-pdf
export const spacing = {
  0: "0",
  0.5: "1.5pt",
  1: "3pt",
  1.5: "4.5pt",
  2: "6pt",
  2.5: "7.5pt",
  3: "9pt",
  3.5: "10.5pt",
  4: "12pt",
  5: "15pt",
  6: "18pt",
  7: "21pt",
  8: "24pt",
  9: "27pt",
  10: "30pt",
  11: "33pt",
  12: "36pt",
  14: "42pt",
  16: "48pt",
  20: "60pt",
  24: "72pt",
  full: "100%",
} as const;

export const styles = StyleSheet.create({
  flexRow: {
    display: "flex",
    flexDirection: "row",
  },
  flexRowBetween: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  flexCol: {
    display: "flex",
    flexDirection: "column",
  },
});

// Jake's Resume uses black/dark, no color theme
export const DEFAULT_FONT_COLOR = "#171717";
export const THEME_COLOR = "#171717"; // Black headings, like Jake's

import '@emotion/react';

/**
 * Augment @emotion/react Theme to include the custom color properties
 * that are injected into the MUI theme by the resume builder's color picker.
 * These are set dynamically by the templates (see useResumePalette).
 */
declare module '@emotion/react' {
  export interface Theme {
    backgroundColor?: string;
    fontColor?: string;
    titleColor?: string;
    highlighterColor?: string;
  }
}

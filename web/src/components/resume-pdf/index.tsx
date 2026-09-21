/**
 * TailorResume — Client-side PDF Download Button
 * Uses @react-pdf/renderer (same as OpenResume) to generate PDF blob in browser
 */
"use client";

import { useState } from "react";
import { pdf } from "@react-pdf/renderer";
import { ResumePDF } from "./ResumePDF";
import { mapSectionsToResume, type TailorSection } from "./types";

/**
 * Generate a PDF blob from resume sections entirely in the browser.
 * No backend call needed!
 */
export async function generatePDFBlob(sections: TailorSection[]): Promise<Blob> {
  const resume = mapSectionsToResume(sections);
  const blob = await pdf(<ResumePDF resume={resume} isPDF={true} />).toBlob();
  return blob;
}

/**
 * Trigger download of the generated PDF
 */
export async function downloadPDF(sections: TailorSection[], filename = "tailored_resume.pdf") {
  const blob = await generatePDFBlob(sections);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

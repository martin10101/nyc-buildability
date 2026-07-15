import type { Metadata } from "next";
import type { ReactNode } from "react";
import { REQUIRED_DISCLAIMER } from "@/lib/disclaimer";

export const metadata: Metadata = {
  title: "NYC Buildability",
  description:
    "Preliminary NYC development feasibility and zoning intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily:
            "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
          color: "#1a1a1a",
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
        }}
      >
        <main style={{ flex: 1 }}>{children}</main>
        <footer
          role="contentinfo"
          aria-label="Required disclaimer"
          style={{
            borderTop: "1px solid #d9d9d9",
            background: "#f7f7f5",
            padding: "1rem 1.5rem",
            fontSize: "0.85rem",
            lineHeight: 1.5,
            color: "#3d3d3d",
          }}
        >
          <p style={{ maxWidth: "80ch", margin: 0 }}>{REQUIRED_DISCLAIMER}</p>
        </footer>
      </body>
    </html>
  );
}

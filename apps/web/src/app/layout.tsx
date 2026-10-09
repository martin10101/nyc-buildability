import type { Metadata } from "next";
import type { ReactNode } from "react";
import { REQUIRED_DISCLAIMER } from "@/lib/disclaimer";
import "./globals.css";
// M5-T023: MapLibre GL JS stylesheet for the lot-outline map controls and
// canvas positioning (its FIRST use is the address confirm card's
// LotOutlineMap). Imported once at the app root — a static CSS side-effect that
// never pulls the browser-only maplibre-gl JS runtime into SSR (that stays a
// dynamic import inside the client-only map effect).
import "maplibre-gl/dist/maplibre-gl.css";

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

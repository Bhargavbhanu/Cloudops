import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Right LLM",
  description: "Autonomous LLM Cost Optimization and AI FinOps Platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

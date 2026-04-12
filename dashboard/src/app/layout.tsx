import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { agent, branding, business } from "@/lib/config";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: `${agent.name} AI — ${branding.dashboardTitle}`,
  description: `Panel de control del agente de voz para ${business.name}`,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${inter.variable} ${playfair.variable} dark h-full antialiased`}
    >
      <body
        className="min-h-full flex flex-col font-sans bg-neutral-950 text-neutral-50"
        style={{ "--brand-color": branding.primaryColor } as React.CSSProperties}
      >
        {children}
      </body>
    </html>
  );
}

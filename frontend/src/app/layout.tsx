import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI APK-to-iOS Migration Platform",
  description: "Automatically reverse engineer Android APKs, recover architecture, generate SwiftUI Xcode projects, compile, and validate with AI self-healing repair loops.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

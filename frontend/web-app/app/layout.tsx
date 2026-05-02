import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "InfluenceHub",
  description: "Influencer Campaign Management Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <nav className="bg-gray-900 text-white px-6 py-4 flex items-center gap-8">
          <Link href="/" className="text-xl font-bold">InfluenceHub</Link>
          <Link href="/campaigns" className="hover:text-blue-400">Campaigns</Link>
          <Link href="/report" className="hover:text-blue-400">Report</Link>
        </nav>
        <main className="max-w-6xl mx-auto p-6">
          {children}
        </main>
      </body>
    </html>
  );
}

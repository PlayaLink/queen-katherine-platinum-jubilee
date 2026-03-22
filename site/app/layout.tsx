import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Happy 70th Birthday, Katherine!",
  description:
    "A collection of memories and love from friends and family for Katherine's 70th birthday.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

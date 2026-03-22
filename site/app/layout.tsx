import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Platinum Jubilee of Queen Katherine",
  description:
    "A celebration of Katherine's 70th birthday — memories from loved ones.",
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

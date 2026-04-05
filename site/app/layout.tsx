import type { Metadata } from "next";
import {
  Playfair_Display,
  Caveat,
  Lora,
  Cormorant_Garamond,
} from "next/font/google";
import "./globals.css";

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
  display: "swap",
});

const caveat = Caveat({
  subsets: ["latin"],
  variable: "--font-caveat",
  display: "swap",
});

const lora = Lora({
  subsets: ["latin"],
  variable: "--font-lora",
  display: "swap",
});

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  variable: "--font-cormorant",
  weight: ["300", "400", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Queen Katherine Jubilee",
  description: "Words of Tribute from Her Royal Subjects",
  metadataBase: new URL("https://queenkatherinejubilee.com"),
  openGraph: {
    title: "Queen Katherine Jubilee",
    description: "Words of Tribute from Her Royal Subjects",
    url: "https://queenkatherinejubilee.com",
    siteName: "Queen Katherine Jubilee",
    type: "website",
    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Katherine with her dog in her art studio",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Queen Katherine Jubilee",
    description: "Words of Tribute from Her Royal Subjects",
    images: ["/og-image.jpg"],
  },
};

/* Inline script that runs before paint to apply persisted theme,
   preventing a flash of the default theme. */
const themeScript = `(function(){try{var t=sessionStorage.getItem('kb70-theme');if(t&&['mosaic','journal','garden-party','collage','gallery'].includes(t)){document.documentElement.setAttribute('data-theme',t)}}catch(e){}})()`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      data-theme="mosaic"
      className={`${playfair.variable} ${caveat.variable} ${lora.variable} ${cormorant.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}

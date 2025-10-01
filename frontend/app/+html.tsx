// app/+html.tsx
import * as React from "react";

export default function HTML({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <style>{`
          html, body, #root { height: 100%; }
          body { margin: 0; background: #0f172a; color: #dbeafe; }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}

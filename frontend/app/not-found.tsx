'use client';

// Render the default Next.js 404 page when a route
// is requested that doesn't match the middleware and
// therefore doesn't have a locale associated with it.

export default function NotFound() {
  return (
    <html lang="en">
      <body>
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '100vh',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>404</h1>
          <p style={{ fontSize: '1.25rem', marginBottom: '2rem' }}>Page not found</p>
          <a href="/en" style={{ color: '#0070f3', textDecoration: 'underline' }}>
            Go to homepage
          </a>
        </div>
      </body>
    </html>
  );
}
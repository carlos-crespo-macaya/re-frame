// This script runs before React hydration to prevent FOUC
export const themeScript = `
  (function() {
    const theme = localStorage.getItem('reframe-theme') || 'system';
    let resolved = theme;
    
    if (theme === 'system') {
      resolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    document.documentElement.setAttribute('data-theme', resolved);
    
    // Update meta theme-color
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute('content', resolved === 'dark' ? '#0a0a0a' : '#ffffff');
    }
  })();
`;
import React, { useState } from 'react';

interface PdfChipProps {
  pdfUrl?: string;
  fileName?: string;
  onDownload?: () => void;
  isOffline?: boolean;
}

export const PdfChip: React.FC<PdfChipProps> = ({ 
  pdfUrl, 
  fileName = 'reframe-summary.pdf',
  onDownload,
  isOffline = false
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);

  const handleDownload = async () => {
    if (isOffline) {
      // Dummy download for offline mode
      setIsDownloading(true);
      setDownloadProgress(0);
      
      // Simulate download progress
      const interval = setInterval(() => {
        setDownloadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsDownloading(false);
            if (onDownload) onDownload();
            return 100;
          }
          return prev + 10;
        });
      }, 200);
      
      return;
    }

    if (!pdfUrl) {
      console.error('No PDF URL provided');
      return;
    }

    try {
      setIsDownloading(true);
      setDownloadProgress(0);

      const response = await fetch(pdfUrl);
      const total = parseInt(response.headers.get('content-length') || '0', 10);
      const reader = response.body?.getReader();
      
      if (!reader) throw new Error('Failed to get reader');

      const chunks: Uint8Array[] = [];
      let received = 0;

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        chunks.push(value);
        received += value.length;
        
        if (total > 0) {
          setDownloadProgress(Math.round((received / total) * 100));
        }
      }

      // Create blob and download
      const blob = new Blob(chunks, { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      if (onDownload) onDownload();
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsDownloading(false);
      setDownloadProgress(0);
    }
  };

  return (
    <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-full">
      <svg 
        className="w-5 h-5 text-blue-600 dark:text-blue-400" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" 
        />
      </svg>
      
      <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
        {fileName}
      </span>
      
      <button
        onClick={handleDownload}
        disabled={isDownloading}
        className={`
          ml-2 p-1 rounded-full transition-colors
          ${isDownloading 
            ? 'bg-gray-200 dark:bg-gray-700 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600'
          }
        `}
        aria-label="Download PDF"
      >
        {isDownloading ? (
          <div className="relative w-5 h-5">
            <svg className="w-5 h-5 text-white animate-spin" fill="none" viewBox="0 0 24 24">
              <circle 
                className="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                strokeWidth="4"
              />
              <path 
                className="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            {downloadProgress > 0 && (
              <span className="absolute inset-0 flex items-center justify-center text-xs text-white font-bold">
                {downloadProgress}%
              </span>
            )}
          </div>
        ) : (
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
            />
          </svg>
        )}
      </button>
    </div>
  );
};

export default PdfChip;
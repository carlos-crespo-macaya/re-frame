import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: process.env.SERVICE_NAME || 're-frame-frontend',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    proxyEnabled: !!process.env.BACKEND_INTERNAL_HOST,
    backendHost: process.env.BACKEND_INTERNAL_HOST || 'not configured',
  }, {
    headers: {
      'Cache-Control': 'no-store, no-cache, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    }
  });
}

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: process.env.SERVICE_NAME || 're-frame-frontend',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    proxyEnabled: !!process.env.BACKEND_INTERNAL_HOST,
    backendHost: process.env.BACKEND_INTERNAL_HOST || 'not configured',
  });
}

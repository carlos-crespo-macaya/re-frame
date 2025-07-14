import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: process.env.SERVICE_NAME || 're-frame-frontend',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'not configured',
  });
}
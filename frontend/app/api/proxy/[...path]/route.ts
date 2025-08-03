import { NextRequest, NextResponse } from 'next/server';
import { GoogleAuth } from 'google-auth-library';

const backendHost = process.env.BACKEND_INTERNAL_HOST;
const backendPublicUrl = process.env.BACKEND_PUBLIC_URL || 'https://re-frame-backend-yeetrlkwzq-ew.a.run.app';

async function proxy(req: NextRequest, { params }: { params: { path: string[] } }) {
  if (!backendHost) {
    return NextResponse.json(
      { error: 'Proxy disabled in dev' },
      { status: 502 }
    );
  }

  // Optional: Request size guard
  const MAX = 50 * 1024 * 1024; // 50 MB
  const contentLength = Number(req.headers.get('content-length')) || 0;
  if (contentLength > MAX) {
    return NextResponse.json(
      { error: 'File too large' },
      { status: 413 }
    );
  }

  const targetUrl = `https://${backendHost}/${params.path.join('/')}${req.nextUrl.search}`;

  try {
    // Initialize GoogleAuth for Cloud Run service-to-service authentication
    const auth = new GoogleAuth();

    // For Cloud Run service-to-service auth, the audience must be the public service URL
    // even when using internal traffic routing
    const audience = backendPublicUrl;
    const client = await auth.getIdTokenClient(audience);

    // Prepare request headers (remove problematic headers)
    const requestHeaders = Object.fromEntries(req.headers.entries());
    delete requestHeaders.host; // Remove to avoid conflicts
    delete requestHeaders['content-length']; // Will be recalculated

    // Use the client's request method which automatically adds the Authorization header
    const response = await client.request({
      url: targetUrl,
      method: req.method as any,
      headers: requestHeaders,
      data: ['GET', 'HEAD'].includes(req.method)
        ? undefined
        : await req.arrayBuffer(),
      responseType: 'stream',
    });

    // Process response headers
    const responseHeaders = response.headers as Record<string, string> | Headers;
    const isHeadersObject = responseHeaders.constructor === Headers;

    // Extract header entries properly
    const headerEntries: [string, string][] = isHeadersObject
      ? Array.from((responseHeaders as Headers).entries())
      : Object.entries(responseHeaders as Record<string, string>);

    // Build clean response headers
    const cleanHeaders: Record<string, string> = {
      'cache-control': 'no-store', // Always override cache control
    };

    // Add all headers except problematic ones
    const excludedHeaders = ['host', 'content-encoding', 'transfer-encoding', 'cache-control'];
    for (const [key, value] of headerEntries) {
      if (!excludedHeaders.includes(key.toLowerCase())) {
        cleanHeaders[key] = value;
      }
    }

    // Ensure content-type is set
    if (!cleanHeaders['content-type']) {
      cleanHeaders['content-type'] = 'application/octet-stream';
    }

    // Return the response with proper headers
    return new NextResponse(response.data as BodyInit, {
      status: response.status,
      headers: cleanHeaders,
    });
  } catch (error: any) {
    console.error('Proxy error:', {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      statusText: error.response?.statusText,
      targetUrl,
      audience,
      backendHost,
      method: req.method,
    });

    // Handle specific auth errors
    if (error.code === 'ECONNREFUSED') {
      return NextResponse.json(
        { error: 'Backend service unavailable' },
        { status: 503 }
      );
    }

    if (error.response?.status === 403) {
      return NextResponse.json(
        { error: 'Authentication failed - service account may lack permissions' },
        { status: 403 }
      );
    }

    if (error.response?.status === 401) {
      return NextResponse.json(
        { error: 'Authentication failed - invalid or missing token' },
        { status: 401 }
      );
    }

    // Generic error response
    return NextResponse.json(
      { error: error.message || 'Proxy request failed' },
      { status: error.response?.status || 500 }
    );
  }
}

// Export for every HTTP method
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;

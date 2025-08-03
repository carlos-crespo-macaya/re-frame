import { NextRequest, NextResponse } from 'next/server';
import { GoogleAuth } from 'google-auth-library';

const backendHost = process.env.BACKEND_INTERNAL_HOST;

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

    // For Cloud Run service-to-service auth, the audience must be the full service URL
    const audience = `https://${backendHost}`;
    const client = await auth.getIdTokenClient(audience);

    // Use the client's request method which automatically adds the Authorization header
    const response = await client.request({
      url: targetUrl,
      method: req.method as any,
      headers: {
        ...Object.fromEntries(req.headers),
        // Remove host header to avoid conflicts
        host: undefined,
        // Remove content-length as it will be recalculated
        'content-length': undefined,
      },
      data: ['GET', 'HEAD'].includes(req.method)
        ? undefined
        : await req.arrayBuffer(),
      responseType: 'stream',
    });

    // Return the response with proper headers
    return new NextResponse(response.data, {
      status: response.status,
      headers: {
        'content-type': response.headers['content-type'] || 'application/octet-stream',
        'cache-control': 'no-store',
        ...Object.fromEntries(
          Object.entries(response.headers).filter(([key]) =>
            !['host', 'content-encoding', 'transfer-encoding'].includes(key.toLowerCase())
          )
        ),
      },
    });
  } catch (error: any) {
    console.error('Proxy error:', error);

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

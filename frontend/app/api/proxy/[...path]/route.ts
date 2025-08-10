import { NextRequest, NextResponse } from 'next/server';
import { GoogleAuth } from 'google-auth-library';

async function proxy(req: NextRequest, { params }: { params: { path: string[] } }) {
  // Resolve env dynamically per request for stability across deployments
  const envBackendHost = process.env.BACKEND_INTERNAL_HOST;
  const envBackendPublic = process.env.BACKEND_PUBLIC_URL;
  const envNextPublic = process.env.NEXT_PUBLIC_BACKEND_URL;

  // In production, fall back to public domain if unset; in dev, preserve strict checks
  const isProd = process.env.NODE_ENV === 'production';
  const backendHost = envBackendHost || (isProd ? 'api.re-frame.social' : '');
  const backendPublicUrl = envBackendPublic || envNextPublic || (isProd ? 'https://api.re-frame.social' : '');

  // Derive protocol from BACKEND_PUBLIC_URL (defaults to https)
  // This allows local dev with http://localhost:8000 without TLS
  let protocol: 'http' | 'https' = 'https';
  try {
    if (backendPublicUrl) {
      const u = new URL(backendPublicUrl);
      protocol = (u.protocol === 'http:') ? 'http' : 'https';
    }
  } catch {
    // keep default https
  }

  if (!backendHost) {
    return NextResponse.json(
      { error: 'Proxy disabled in dev' },
      { status: 502 }
    );
  }

  if (!backendPublicUrl) {
    console.error('BACKEND_PUBLIC_URL environment variable is not configured');
    return NextResponse.json(
      {
        error: 'Service configuration error',
        details: 'Backend URL not configured. Please check deployment configuration.'
      },
      { status: 500 }
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

  // Use internal host for request routing with derived protocol
  const targetUrl = `${protocol}://${backendHost}/${params.path.join('/')}${req.nextUrl.search}`;

  // For Cloud Run service-to-service auth, the audience must be the public service URL
  // even when using internal traffic routing
  const audience = backendPublicUrl;

  try {
    // If localhost/127.* or explicitly allowed (non-production only), skip Cloud Run IAM and proxy directly
    // Avoid broadly skipping IAM just because protocol is http
    const allowInsecure = process.env.PROXY_ALLOW_INSECURE === 'true' && process.env.NODE_ENV !== 'production';
    const isLocalPlainHttp = /^(localhost|127\.)/i.test(backendHost) || allowInsecure;
    if (isLocalPlainHttp) {
      const requestHeaders = Object.fromEntries(req.headers.entries());
      delete requestHeaders.host;
      delete requestHeaders['content-length'];

      const isSSE = params.path.includes('events') ||
        requestHeaders.accept?.includes('text/event-stream');

      const init: RequestInit & { duplex?: 'half' } = {
        method: req.method,
        headers: {
          ...requestHeaders,
        },
        body: ['GET', 'HEAD'].includes(req.method) ? undefined : await req.arrayBuffer(),
      };
      if (isSSE) {
        (init.headers as Record<string, string>)['Accept'] = 'text/event-stream';
        (init.headers as Record<string, string>)['Cache-Control'] = 'no-cache';
        init.duplex = 'half';
      }

      const response = await fetch(targetUrl, init);

      if (!response.ok && response.body) {
        // forward non-OK with body
        return new NextResponse(response.body, { status: response.status, headers: response.headers });
      }

      return new NextResponse(response.body, { status: response.status, headers: response.headers });
    }

    // Initialize GoogleAuth for Cloud Run service-to-service authentication
    const auth = new GoogleAuth();
    const client = await auth.getIdTokenClient(audience);

    // Prepare request headers (remove problematic headers)
    const requestHeaders = Object.fromEntries(req.headers.entries());
    delete requestHeaders.host; // Remove to avoid conflicts
    delete requestHeaders['content-length']; // Will be recalculated

    // Check if this is an SSE request
    const isSSE = params.path.includes('events') ||
                  requestHeaders.accept?.includes('text/event-stream');

    // For SSE, we need to handle streaming differently
    if (isSSE) {
      // Make a fetch request with auth header instead of using the client
      const authClient = await auth.getClient();
      const authHeaders = await authClient.getRequestHeaders(targetUrl);

      const response = await fetch(targetUrl, {
        method: req.method,
        headers: {
          ...requestHeaders,
          ...authHeaders,
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
        // Required by Node.js fetch for streaming requests in some environments
        // and validated by unit tests to ensure correct handling of SSE
        // @ts-expect-error - duplex is not yet in the standard lib types
        duplex: 'half',
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }

      // Return the SSE stream directly
      return new NextResponse(response.body, {
        status: response.status,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          'X-Accel-Buffering': 'no', // Disable buffering for SSE
        },
      });
    }

    // Use the client's request method which automatically adds the Authorization header
    const requestOptions: any = {
      url: targetUrl,
      method: req.method,
      headers: requestHeaders,
      data: ['GET', 'HEAD'].includes(req.method)
        ? undefined
        : await req.arrayBuffer(),
      responseType: 'stream',
    };
    // In production, prevent axios from throwing on non-2xx so we can forward status/body
    if (isProd) {
      requestOptions.validateStatus = () => true;
    }
    const response = await client.request(requestOptions);

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

    // Return the response with proper headers and original status
    return new NextResponse(response.data as unknown as BodyInit, {
      status: response.status,
      headers: cleanHeaders,
    });
  } catch (error: unknown) {
    const err = error as { message?: string; code?: string; response?: { status?: number; statusText?: string } };
    console.error('Proxy error:', {
      message: err?.message,
      code: err?.code,
      status: err?.response?.status,
      statusText: err?.response?.statusText,
      targetUrl,
      audience,
      backendHost,
      method: req.method,
    });

    // Handle specific auth errors
    if (err?.code === 'ECONNREFUSED') {
      return NextResponse.json(
        { error: 'Backend service unavailable' },
        { status: 503 }
      );
    }

    if (err?.response?.status === 403) {
      return NextResponse.json(
        { error: 'Authentication failed - service account may lack permissions' },
        { status: 403 }
      );
    }

    if (err?.response?.status === 401) {
      return NextResponse.json(
        { error: 'Authentication failed - invalid or missing token' },
        { status: 401 }
      );
    }

    // Generic error response
    return NextResponse.json(
      { error: err?.message || 'Proxy request failed' },
      { status: err?.response?.status || 500 }
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

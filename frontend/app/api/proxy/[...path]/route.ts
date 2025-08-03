import { NextRequest, NextResponse } from 'next/server';
import { GoogleAuth } from 'google-auth-library';

const backendHost = process.env.BACKEND_INTERNAL_HOST;
const auth = new GoogleAuth();

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

  const target = `https://${backendHost}/${params.path.join('/')}${req.nextUrl.search}`;

  // Get ID token for backend (audience = backend host origin)
  const client = await auth.getIdTokenClient(`https://${backendHost}`);
  const headers = await client.getRequestHeaders();

  // Build request init
  const init: RequestInit & { duplex?: string } = {
    method: req.method,
    headers: {
      ...Object.fromEntries(req.headers),
      ...headers,
      host: backendHost
    },
    // Important for SSE/WebSocket support
    duplex: 'half',
    body: ['GET', 'HEAD'].includes(req.method)
      ? undefined
      : await req.arrayBuffer(),
    cache: 'no-store',
  };

  const resp = await fetch(target, init);

  // Pipe the response stream straight back
  return new NextResponse(resp.body, {
    status: resp.status,
    headers: resp.headers,
  });
}

// Export for every HTTP method
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;

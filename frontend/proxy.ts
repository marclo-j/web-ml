import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Comprobación optimista: sin cookie de sesión, directo al login. La
// verificación real del token la hace el backend en cada llamada.
export function proxy(request: NextRequest) {
  if (!request.cookies.has("sesion")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!login|_next/static|_next/image|favicon.ico).*)"],
};

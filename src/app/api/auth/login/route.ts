import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { username, password } = await req.json();

  const adminUser = process.env.ADMIN_USER;
  const adminPassword = process.env.ADMIN_PASSWORD;
  const sessionToken = process.env.ADMIN_SESSION_TOKEN;

  if (!adminUser || !adminPassword || !sessionToken) {
    return NextResponse.json({ error: "Auth non configurée" }, { status: 500 });
  }

  if (username !== adminUser || password !== adminPassword) {
    return NextResponse.json({ error: "Identifiants invalides" }, { status: 401 });
  }

  const res = NextResponse.json({ ok: true });
  res.cookies.set("karohy_admin", sessionToken, {
    httpOnly: true,
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7,
    path: "/",
  });
  return res;
}

import type { User } from "../types";

const BASE = "/api";

async function unwrap(res: Response): Promise<string> {
  try {
    const j = await res.json();
    return j?.detail || j?.message || res.statusText;
  } catch {
    return res.statusText;
  }
}

export async function getMe(): Promise<User | null> {
  const res = await fetch(`${BASE}/auth/me`, { credentials: "include" });
  if (!res.ok) return null;
  const data = await res.json();
  return data || null;
}

export async function login(username: string, password: string): Promise<User> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(await unwrap(res));
  return res.json();
}

export async function signup(
  username: string,
  password: string,
  full_name?: string,
  email?: string,
): Promise<User> {
  const res = await fetch(`${BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password, full_name, email }),
  });
  if (!res.ok) throw new Error(await unwrap(res));
  return res.json();
}

export async function logout(): Promise<void> {
  await fetch(`${BASE}/auth/logout`, { method: "POST", credentials: "include" });
}

export async function connectToPrestataire(
  prestataire_id: string,
  message: string = "",
): Promise<{ ok: boolean; created: boolean; prestataire_name: string }> {
  const res = await fetch(`${BASE}/connect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ prestataire_id, message }),
  });
  if (res.status === 401) {
    const err: Error & { code?: string } = new Error("Login required");
    err.code = "LOGIN_REQUIRED";
    throw err;
  }
  if (!res.ok) throw new Error(await unwrap(res));
  return res.json();
}

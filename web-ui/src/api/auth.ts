import { api, setToken, clearToken } from "./client";

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type MeResponse = {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  expires_at: string | null;
};

export async function login(username: string, password: string) {
  const data = await api<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: { username, password },
  });
  setToken(data.access_token);
  return data;
}

export async function me() {
  return api<MeResponse>("/api/v1/auth/me", { auth: true });
}

export function logout() {
  clearToken();
}

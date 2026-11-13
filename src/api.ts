import { invoke } from "@tauri-apps/api/core";

export interface ProfileInfo {
  name: string;
  path: string;
  isDefaultProfile: boolean;
  isSelected: boolean;
  loggedIn: boolean;
  email: string | null;
  displayName: string | null;
  organization: string | null;
  plan: string | null;
  subscriptionType: string | null;
  rateLimitTier: string | null;
  scopes: string[];
  hasRefreshToken: boolean;
  expiresAt: number;
  refreshExpiresAt: number | null;
  error: string | null;
}

export interface State {
  profilesRoot: string;
  envValue: string | null;
  envUnknown: boolean;
  profiles: ProfileInfo[];
}

export interface Created {
  name: string;
  warnings: string[];
  state: State;
}

export const api = {
  getState: () => invoke<State>("get_state"),
  setDefault: (name: string) => invoke<State>("set_default", { name }),
  createProfile: (name: string) => invoke<Created>("create_profile", { name }),
  renameProfile: (old: string, newName: string) => invoke<State>("rename_profile", { old, new: newName }),
  deleteProfile: (name: string) => invoke<State>("delete_profile", { name }),
  openClaude: (name: string) => invoke<void>("open_claude", { name }),
  openFolder: (name: string) => invoke<void>("open_folder", { name }),
};

export type Tone = "ok" | "warn" | "bad" | "idle";

export function sessionStatus(p: ProfileInfo): { text: string; tone: Tone } {
  if (p.error) return { text: p.error, tone: "bad" };
  if (!p.loggedIn) return { text: "Sem login — abra o Claude e use /login", tone: "idle" };
  const now = Date.now();
  if (p.refreshExpiresAt && p.refreshExpiresAt <= now) return { text: "Sessão expirada — faça /login de novo", tone: "bad" };
  if (!p.hasRefreshToken) return { text: "Sem refresh token", tone: "warn" };
  return { text: "Conectada", tone: "ok" };
}

export function formatLeft(ms: number): string {
  const h = Math.max(0, ms - Date.now()) / 3_600_000;
  return h >= 24 ? `${(h / 24).toFixed(1)} dias` : `${h.toFixed(1)} h`;
}

export function formatDate(ms: number | null): string {
  return ms && ms > 0 ? new Date(ms).toLocaleString("pt-BR") : "—";
}

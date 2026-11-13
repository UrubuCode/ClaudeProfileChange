import { invoke } from "@tauri-apps/api/core";

export type ToolId = "claude" | "codex" | "agy";

export interface Detail {
  label: string;
  value: string;
}

export interface ProfileInfo {
  tool: ToolId;
  name: string;
  path: string;
  isDefaultProfile: boolean;
  isSelected: boolean;
  loggedIn: boolean;
  email: string | null;
  organization: string | null;
  plan: string | null;
  expiresAt: number | null;
  refreshExpiresAt: number | null;
  scopes: string[];
  details: Detail[];
  error: string | null;
}

export interface ToolState {
  tool: ToolId;
  label: string;
  command: string;
  installed: boolean;
  supportsDefault: boolean;
  envVar: string | null;
  profilesRoot: string;
  envValue: string | null;
  envUnknown: boolean;
  profiles: ProfileInfo[];
}

export interface AppState {
  tools: ToolState[];
}

export interface Created {
  name: string;
  warnings: string[];
  state: AppState;
}

export const api = {
  getState: () => invoke<AppState>("get_state"),
  setDefault: (tool: ToolId, name: string) => invoke<AppState>("set_default", { tool, name }),
  createProfile: (tool: ToolId, name: string) => invoke<Created>("create_profile", { tool, name }),
  renameProfile: (tool: ToolId, old: string, newName: string) =>
    invoke<AppState>("rename_profile", { tool, old, new: newName }),
  deleteProfile: (tool: ToolId, name: string) => invoke<AppState>("delete_profile", { tool, name }),
  openTool: (tool: ToolId, name: string) => invoke<void>("open_tool", { tool, name }),
  openFolder: (tool: ToolId, name: string) => invoke<void>("open_folder", { tool, name }),
};

export type Tone = "ok" | "warn" | "bad" | "idle";

export function sessionStatus(p: ProfileInfo): { text: string; tone: Tone } {
  if (p.error) return { text: p.error, tone: "bad" };
  if (!p.loggedIn) return { text: "Sem login", tone: "idle" };
  if (p.refreshExpiresAt && p.refreshExpiresAt <= Date.now()) return { text: "Sessão expirada — faça login de novo", tone: "bad" };
  return { text: "Conectada", tone: "ok" };
}

export function formatLeft(ms: number): string {
  const h = Math.max(0, ms - Date.now()) / 3_600_000;
  return h >= 24 ? `${(h / 24).toFixed(1)} dias` : `${h.toFixed(1)} h`;
}

export function formatDate(ms: number | null): string {
  return ms && ms > 0 ? new Date(ms).toLocaleString("pt-BR") : "—";
}

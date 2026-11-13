//! Ferramentas de IA suportadas e como cada uma isola um perfil.
//!
//! | Ferramenta  | Isolamento                                   | Login do perfil            |
//! |-------------|----------------------------------------------|----------------------------|
//! | Claude Code | `CLAUDE_CONFIG_DIR=<perfil>`                 | `.credentials.json`        |
//! | Codex       | `CODEX_HOME=<perfil>`                        | `auth.json`                |
//! | Antigravity | `USERPROFILE=<perfil>` + `SSH_CONNECTION`    | `antigravity-oauth-token`  |
//!
//! O `agy` não tem variável própria: o perfil é uma "home" falsa. Com
//! `SSH_CONNECTION` definida ele guarda o login em arquivo (`shouldBypassKeyring`)
//! em vez da entrada fixa `gemini:antigravity` do Gerenciador de Credenciais.

use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Tool {
    Claude,
    Codex,
    Agy,
}

/// Valor fictício: só precisa existir para o agy usar o armazenamento em arquivo.
const AGY_SSH_MARKER: &str = "127.0.0.1 0 127.0.0.1 22";

impl Tool {
    pub const ALL: [Tool; 3] = [Tool::Claude, Tool::Codex, Tool::Agy];

    pub fn id(self) -> &'static str {
        match self {
            Tool::Claude => "claude",
            Tool::Codex => "codex",
            Tool::Agy => "agy",
        }
    }

    pub fn from_id(s: &str) -> Option<Tool> {
        Tool::ALL.into_iter().find(|t| t.id() == s)
    }

    pub fn label(self) -> &'static str {
        match self {
            Tool::Claude => "Claude Code",
            Tool::Codex => "Codex",
            Tool::Agy => "Antigravity",
        }
    }

    pub fn short(self) -> &'static str {
        match self {
            Tool::Claude => "Claude",
            Tool::Codex => "Codex",
            Tool::Agy => "Antigravity",
        }
    }

    /// Comando de terminal da ferramenta.
    pub fn command(self) -> &'static str {
        match self {
            Tool::Claude => "claude",
            Tool::Codex => "codex",
            Tool::Agy => "agy",
        }
    }

    /// Variável de ambiente que escolhe a pasta (e pode virar o padrão do sistema).
    pub fn env_var(self) -> Option<&'static str> {
        match self {
            Tool::Claude => Some("CLAUDE_CONFIG_DIR"),
            Tool::Codex => Some("CODEX_HOME"),
            Tool::Agy => None,
        }
    }

    pub fn supports_default(self) -> bool {
        self.env_var().is_some()
    }

    pub fn profiles_root(self, home: &Path) -> PathBuf {
        home.join(match self {
            Tool::Claude => ".claude-profiles",
            Tool::Codex => ".codex-profiles",
            Tool::Agy => ".agy-profiles",
        })
    }

    /// Pasta do perfil "padrão" (a instalação original).
    pub fn default_dir(self, home: &Path) -> PathBuf {
        match self {
            Tool::Claude => home.join(".claude"),
            Tool::Codex => home.join(".codex"),
            Tool::Agy => home.to_path_buf(),
        }
    }

    /// Pastas da instalação original ligadas (junction) em cada perfil novo.
    /// Caminhos relativos à pasta do perfil / à pasta padrão.
    pub fn shared_dirs(self) -> &'static [&'static str] {
        match self {
            // `sessions`: registro de sessões abertas — Claudes de perfis
            // diferentes se enxergam (ListAgents/SendMessage).
            Tool::Claude => &["skills", "plugins", "agents", "commands", "sessions"],
            Tool::Codex => &["skills", "plugins", "rules"],
            // home falsa: comandos do agente continuam achando as chaves SSH.
            Tool::Agy => &[".ssh"],
        }
    }

    /// Arquivos copiados uma vez na criação (junction só funciona com pastas).
    pub fn copied_files(self) -> &'static [&'static str] {
        match self {
            Tool::Claude => &["settings.json", "CLAUDE.md"],
            Tool::Codex => &["config.toml", "AGENTS.md"],
            Tool::Agy => &[".gitconfig"],
        }
    }

    /// Variáveis para rodar a ferramenta no perfil. `None` = remover a variável.
    pub fn launch_env(self, profile_dir: &Path, is_default: bool) -> Vec<(&'static str, Option<String>)> {
        let dir = profile_dir.display().to_string();
        match self {
            Tool::Claude | Tool::Codex => {
                let var = self.env_var().unwrap();
                vec![(var, (!is_default).then_some(dir))]
            }
            Tool::Agy if is_default => vec![],
            Tool::Agy => vec![
                ("USERPROFILE", Some(dir.clone())),
                ("HOME", Some(dir)),
                ("SSH_CONNECTION", Some(AGY_SSH_MARKER.into())),
            ],
        }
    }

    /// A ferramenta está instalada (comando encontrado no PATH)?
    pub fn installed(self) -> bool {
        which(self.command()).is_some()
    }
}

/// Procura um comando no PATH (com as extensões do Windows).
pub fn which(cmd: &str) -> Option<PathBuf> {
    let exts: Vec<String> = if cfg!(windows) {
        std::env::var("PATHEXT")
            .unwrap_or_else(|_| ".EXE;.CMD;.BAT;.PS1".into())
            .split(';')
            .map(|e| e.to_lowercase())
            .chain(std::iter::once(String::new()))
            .collect()
    } else {
        vec![String::new()]
    };
    let path = std::env::var_os("PATH")?;
    for dir in std::env::split_paths(&path) {
        for e in &exts {
            let p = dir.join(format!("{cmd}{e}"));
            if p.is_file() {
                return Some(p);
            }
        }
    }
    None
}

//! Abre um terminal rodando a ferramenta de IA num perfil e numa pasta.
//!
//! Usa o Windows Terminal quando disponível (cores, links clicáveis mesmo
//! quebrados em várias linhas); senão, uma janela do PowerShell. As variáveis
//! do perfil são aplicadas dentro do próprio comando (`-EncodedCommand`), então
//! funciona mesmo quando o Windows Terminal reaproveita uma janela existente.

use crate::profiles::Store;
use crate::tools::Tool;
use base64::Engine;
use std::path::{Path, PathBuf};
use std::process::Command;

/// Marcadores de uma sessão do Claude Code que tenha aberto o app (ex.:
/// CLAUDE_CODE_CHILD_SESSION desliga o salvamento do histórico).
const SESSION_MARKERS: &[&str] = &[
    "CLAUDECODE",
    "CLAUDE_PID",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_CODE_CHILD_SESSION",
    "CLAUDE_CODE_BRIDGE_SESSION_ID",
    "CLAUDE_CODE_MESSAGING_SOCKET",
    "CLAUDE_CODE_MESSAGING_TOKEN",
    "CLAUDE_CODE_SESSION_ATTENDED",
];

fn ps_quote(s: &str) -> String {
    format!("'{}'", s.replace('\'', "''"))
}

/// Script PowerShell que prepara o ambiente e roda a ferramenta.
pub fn script(tool: Tool, env: &[(&str, Option<String>)], folder: &Path, color_hint: bool) -> String {
    let mut lines: Vec<String> = SESSION_MARKERS
        .iter()
        .map(|k| format!("Remove-Item Env:{k} -ErrorAction SilentlyContinue"))
        .collect();
    for (k, v) in env {
        match v {
            Some(v) => lines.push(format!("$env:{k} = {}", ps_quote(v))),
            None => lines.push(format!("Remove-Item Env:{k} -ErrorAction SilentlyContinue")),
        }
    }
    if color_hint {
        lines.push("if (-not $env:COLORTERM) { $env:COLORTERM = 'truecolor' }".into());
    }
    lines.push(format!("Set-Location -LiteralPath {}", ps_quote(&folder.display().to_string())));
    lines.push(tool.command().into());
    lines.join("; ")
}

fn encode(script: &str) -> String {
    let utf16: Vec<u8> = script.encode_utf16().flat_map(|u| u.to_le_bytes()).collect();
    base64::engine::general_purpose::STANDARD.encode(utf16)
}

fn windows_terminal() -> Option<PathBuf> {
    crate::tools::which("wt")
}

pub fn open(store: &Store, name: &str, cwd: Option<&Path>) -> Result<(), String> {
    let tool = store.tool;
    store.ensure_shared_links(name); // perfis antigos ganham links novos
    let env = store.launch_env(name)?;
    let folder = cwd.map(Path::to_path_buf).or_else(dirs::home_dir).unwrap_or_else(|| PathBuf::from("."));
    let title = match folder.file_name() {
        Some(f) => format!("{} [{name}] - {}", tool.short(), f.to_string_lossy()),
        None => format!("{} [{name}] - {}", tool.short(), folder.display()),
    };
    let wt = windows_terminal();
    let encoded = encode(&script(tool, &env, &folder, wt.is_none()));

    let mut cmd = match &wt {
        Some(wt) => {
            let mut c = Command::new(wt);
            c.args(["-w", "0", "new-tab", "--title", &title, "-d"])
                .arg(&folder)
                .args(["powershell", "-NoLogo", "-NoExit", "-EncodedCommand", &encoded]);
            c
        }
        None => {
            let mut c = Command::new("cmd");
            c.args(["/c", "start", &title, "powershell", "-NoLogo", "-NoExit", "-EncodedCommand", &encoded]);
            c
        }
    };
    cmd.current_dir(&folder);
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        cmd.creation_flags(0x0800_0000); // CREATE_NO_WINDOW para o processo intermediário
    }
    cmd.spawn().map(|_| ()).map_err(|e| format!("Não foi possível abrir o terminal: {e}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn script_sets_and_removes_vars() {
        let s = script(
            Tool::Agy,
            &[("USERPROFILE", Some(r"C:\Users\o'neil\.agy-profiles\x".into())), ("CODEX_HOME", None)],
            Path::new(r"C:\proj"),
            true,
        );
        assert!(s.contains(r"$env:USERPROFILE = 'C:\Users\o''neil\.agy-profiles\x'"));
        assert!(s.contains("Remove-Item Env:CODEX_HOME"));
        assert!(s.contains("Remove-Item Env:CLAUDE_CODE_CHILD_SESSION"));
        assert!(s.contains("COLORTERM"));
        assert!(s.trim_end().ends_with("agy"));
        // base64 sem ';' — o Windows Terminal trata ';' como separador
        assert!(!encode(&s).contains(';'));
    }
}

//! Menu de contexto do Explorer: "Abrir IA aqui ▸ <ferramenta · perfil>".
//!
//! Registrado só para o usuário (HKCU\Software\Classes), sem admin. Cada item
//! chama este próprio executável com `--open <ferramenta> <perfil> <pasta>`,
//! que abre um terminal na pasta com o perfil e encerra.

use crate::profiles::{ToolState, DEFAULT_NAME};
#[cfg(windows)]
use crate::tools::Tool;

pub const CLI_FLAG: &str = "--open";

#[cfg(windows)]
mod imp {
    use super::*;
    use winreg::enums::HKEY_CURRENT_USER;
    use winreg::RegKey;

    const CLASSES: &str = r"Software\Classes";
    const VERB: &str = "AISessionManager";
    const SUBMENU: &str = r"Directory\ContextMenus\AISessionManager";
    /// Chaves gravadas pelas versões "Claude Profile Manager" (removidas na migração).
    const LEGACY_VERB: &str = "ClaudeProfileManager";
    const LEGACY_SUBMENU: &str = r"Directory\ContextMenus\ClaudeProfileManager";
    /// (onde aparece, placeholder da pasta)
    const TARGETS: &[(&str, &str)] = &[
        (r"Directory\shell", "%1"),            // clique direito numa pasta
        (r"Directory\Background\shell", "%V"), // clique direito no fundo da pasta
        (r"Drive\shell", "%1"),                // clique direito num drive
    ];

    fn classes() -> Result<RegKey, String> {
        RegKey::predef(HKEY_CURRENT_USER)
            .create_subkey(CLASSES)
            .map(|(k, _)| k)
            .map_err(|e| e.to_string())
    }

    fn exe() -> String {
        std::env::current_exe()
            .map(|p| p.display().to_string())
            .unwrap_or_default()
    }

    /// Ícones próprios embutidos no app (os CLIs `codex.exe`/`agy.exe` não têm ícone).
    fn bundled_icon(tool: Tool) -> Option<String> {
        let bytes: &[u8] = match tool {
            Tool::Claude => include_bytes!("../icons/tools/claude.ico"),
            Tool::Codex => include_bytes!("../icons/tools/codex.ico"),
            Tool::Agy => include_bytes!("../icons/tools/agy.ico"),
        };
        let dir = dirs::data_local_dir()?.join("AISessionManager").join("icons");
        let path = dir.join(format!("{}.ico", tool.id()));
        if std::fs::read(&path).ok().as_deref() != Some(bytes) {
            std::fs::create_dir_all(&dir).ok()?;
            std::fs::write(&path, bytes).ok()?;
        }
        Some(format!("{},0", path.display()))
    }

    /// Ícone do item: o do app oficial quando existir, senão o nosso.
    fn tool_icon(tool: Tool, fallback: &str) -> String {
        let local = dirs::data_local_dir().unwrap_or_default();
        let official = match tool {
            Tool::Claude => crate::tools::which("claude").filter(|p| p.extension().is_some_and(|e| e.eq_ignore_ascii_case("exe"))),
            Tool::Codex => None,
            Tool::Agy => Some(local.join(r"Programs\antigravity\Antigravity.exe")).filter(|p| p.is_file()),
        };
        official
            .map(|p| format!("{},0", p.display()))
            .or_else(|| bundled_icon(tool))
            .unwrap_or_else(|| format!("{fallback},0"))
    }

    pub fn disable() -> Result<(), String> {
        let c = classes()?;
        for (i, (t, _)) in TARGETS.iter().enumerate() {
            let _ = c.delete_subkey_all(format!(r"{t}\{VERB}"));
            let _ = c.delete_subkey_all(format!("{SUBMENU}{i}"));
            let _ = c.delete_subkey_all(format!(r"{t}\{LEGACY_VERB}"));
            let _ = c.delete_subkey_all(format!("{LEGACY_SUBMENU}{i}"));
        }
        Ok(())
    }

    /// (Re)escreve o menu com as ferramentas instaladas e seus perfis.
    pub fn enable(tools: &[ToolState]) -> Result<(), String> {
        disable()?;
        let c = classes()?;
        let exe = exe();
        let err = |e: std::io::Error| format!("Falha ao gravar o menu no registro: {e}");
        let tools: Vec<&ToolState> = tools.iter().filter(|t| t.installed).collect();
        if tools.is_empty() {
            return Ok(());
        }
        let only_one = tools.len() == 1;

        for (i, (target, placeholder)) in TARGETS.iter().enumerate() {
            let (k, _) = c.create_subkey(format!(r"{target}\{VERB}")).map_err(err)?;
            let title = if only_one { format!("Abrir {} aqui", tools[0].label) } else { "Abrir IA aqui".into() };
            k.set_value("MUIVerb", &title).map_err(err)?;
            k.set_value("Icon", &format!("{exe},0")).map_err(err)?;
            // Um submenu por alvo, porque o placeholder da pasta (%1/%V) muda.
            let sub = format!("{SUBMENU}{i}");
            k.set_value("ExtendedSubCommandsKey", &sub).map_err(err)?;

            let mut n = 0;
            for (ti, t) in tools.iter().enumerate() {
                let icon = tool_icon(t.tool, &exe);
                for p in &t.profiles {
                    let (item, _) = c.create_subkey(format!(r"{sub}\shell\{n:03}")).map_err(err)?;
                    n += 1;
                    let who = match (&p.email, p.name.as_str()) {
                        (Some(e), DEFAULT_NAME) => format!("Padrão — {e}"),
                        (None, DEFAULT_NAME) => "Padrão".to_string(),
                        (Some(e), name) => format!("{name} — {e}"),
                        (None, name) => name.to_string(),
                    };
                    let label = if only_one { who } else { format!("{} · {who}", t.label) };
                    let label = if p.is_selected && t.supports_default { format!("{label}  ✓") } else { label };
                    item.set_value("MUIVerb", &label).map_err(err)?;
                    item.set_value("Icon", &icon).map_err(err)?;
                    // Separador antes do primeiro perfil de cada ferramenta seguinte.
                    if ti > 0 && p.name == DEFAULT_NAME {
                        item.set_value("CommandFlags", &0x20u32).map_err(err)?; // ECF_SEPARATORBEFORE
                    }
                    let (cmd, _) = item.create_subkey("command").map_err(err)?;
                    cmd.set_value(
                        "",
                        &format!(r#""{exe}" {CLI_FLAG} {} "{}" "{placeholder}""#, t.tool.id(), p.name),
                    )
                    .map_err(err)?;
                }
            }
        }
        Ok(())
    }
}

#[cfg(not(windows))]
mod imp {
    use super::*;
    pub fn enable(_: &[ToolState]) -> Result<(), String> {
        Err("Menu de contexto só é suportado no Windows.".into())
    }
    pub fn disable() -> Result<(), String> {
        Ok(())
    }
}

pub use imp::{disable, enable};

/// Corrige o caminho quando o Explorer passa a raiz de um drive: `"C:\"` chega
/// como `C:"` porque `\"` é lido como aspas escapadas.
pub fn fix_dir_arg(s: &str) -> String {
    match s.strip_suffix('"') {
        Some(rest) => format!("{rest}\\"),
        None => s.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::fix_dir_arg;

    #[test]
    fn fixes_drive_root() {
        assert_eq!(fix_dir_arg("C:\""), "C:\\");
        assert_eq!(fix_dir_arg(r"C:\Users\x y"), r"C:\Users\x y");
    }
}

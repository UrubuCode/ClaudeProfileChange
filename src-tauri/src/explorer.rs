//! Menu de contexto do Explorer: "Abrir Claude aqui ▸ <perfil>".
//!
//! Registrado só para o usuário (HKCU\Software\Classes), sem admin. Cada item
//! chama este próprio executável com `--open <perfil> <pasta>`, que abre um
//! terminal na pasta com o CLAUDE_CONFIG_DIR do perfil e encerra.

use crate::profiles::{ProfileInfo, DEFAULT_NAME};

pub const CLI_FLAG: &str = "--open";

#[cfg(windows)]
mod imp {
    use super::*;
    use winreg::enums::HKEY_CURRENT_USER;
    use winreg::RegKey;

    const CLASSES: &str = r"Software\Classes";
    const VERB: &str = "ClaudeProfileManager";
    const SUBMENU: &str = r"Directory\ContextMenus\ClaudeProfileManager";
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

    fn icon() -> String {
        let claude = dirs::home_dir().map(|h| h.join(r".local\bin\claude.exe"));
        match claude {
            Some(p) if p.is_file() => format!("{},0", p.display()),
            _ => format!("{},0", exe()),
        }
    }

    fn exe() -> String {
        std::env::current_exe()
            .map(|p| p.display().to_string())
            .unwrap_or_default()
    }

    pub fn disable() -> Result<(), String> {
        let c = classes()?;
        for (i, (t, _)) in TARGETS.iter().enumerate() {
            let _ = c.delete_subkey_all(format!(r"{t}\{VERB}"));
            let _ = c.delete_subkey_all(format!("{SUBMENU}{i}"));
        }
        Ok(())
    }

    /// (Re)escreve o menu com a lista atual de perfis.
    pub fn enable(profiles: &[ProfileInfo]) -> Result<(), String> {
        disable()?;
        let c = classes()?;
        let icon = icon();
        let exe = exe();
        let err = |e: std::io::Error| format!("Falha ao gravar o menu no registro: {e}");

        for (i, (target, placeholder)) in TARGETS.iter().enumerate() {
            let (k, _) = c.create_subkey(format!(r"{target}\{VERB}")).map_err(err)?;
            k.set_value("MUIVerb", &"Abrir Claude aqui").map_err(err)?;
            k.set_value("Icon", &icon).map_err(err)?;
            // Um submenu por alvo, porque o placeholder da pasta (%1/%V) muda.
            let sub = format!("{SUBMENU}{i}");
            k.set_value("ExtendedSubCommandsKey", &sub).map_err(err)?;

            for (n, p) in profiles.iter().enumerate() {
                let (item, _) = c
                    .create_subkey(format!(r"{sub}\shell\{n:02}"))
                    .map_err(err)?;
                let label = match (&p.email, p.name.as_str()) {
                    (Some(e), DEFAULT_NAME) => format!("Padrão — {e}"),
                    (None, DEFAULT_NAME) => "Padrão".to_string(),
                    (Some(e), n) => format!("{n} — {e}"),
                    (None, n) => n.to_string(),
                };
                let label = if p.is_selected { format!("{label}  ✓") } else { label };
                item.set_value("MUIVerb", &label).map_err(err)?;
                item.set_value("Icon", &icon).map_err(err)?;
                let (cmd, _) = item.create_subkey("command").map_err(err)?;
                cmd.set_value(
                    "",
                    &format!(r#""{exe}" {CLI_FLAG} "{}" "{placeholder}""#, p.name),
                )
                .map_err(err)?;
            }
        }
        Ok(())
    }
}

#[cfg(not(windows))]
mod imp {
    use super::*;
    pub fn enable(_: &[ProfileInfo]) -> Result<(), String> {
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

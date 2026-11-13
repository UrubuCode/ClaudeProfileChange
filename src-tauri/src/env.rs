//! Leitura/gravação de `CLAUDE_CONFIG_DIR` no ambiente do usuário (HKCU\Environment).

pub const VAR: &str = "CLAUDE_CONFIG_DIR";

#[cfg(windows)]
mod imp {
    use super::VAR;
    use winreg::enums::{HKEY_CURRENT_USER, KEY_READ, KEY_SET_VALUE};
    use winreg::RegKey;

    fn key(write: bool) -> Result<RegKey, String> {
        let flags = if write { KEY_READ | KEY_SET_VALUE } else { KEY_READ };
        RegKey::predef(HKEY_CURRENT_USER)
            .open_subkey_with_flags("Environment", flags)
            .map_err(|e| format!("Não foi possível abrir HKCU\\Environment: {e}"))
    }

    pub fn get() -> Option<String> {
        key(false).ok()?.get_value::<String, _>(VAR).ok()
    }

    pub fn set(value: Option<&str>) -> Result<(), String> {
        let k = key(true)?;
        match value {
            Some(v) => k.set_value(VAR, &v).map_err(|e| e.to_string())?,
            None => match k.delete_value(VAR) {
                Ok(()) => {}
                Err(e) if e.kind() == std::io::ErrorKind::NotFound => {}
                Err(e) => return Err(e.to_string()),
            },
        }
        broadcast();
        Ok(())
    }

    /// Avisa o Explorer/terminais novos que o ambiente mudou.
    fn broadcast() {
        use windows_sys::Win32::UI::WindowsAndMessaging::{
            SendMessageTimeoutW, HWND_BROADCAST, SMTO_ABORTIFHUNG, WM_SETTINGCHANGE,
        };
        let s: Vec<u16> = "Environment\0".encode_utf16().collect();
        let mut out = 0usize;
        unsafe {
            SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                s.as_ptr() as isize,
                SMTO_ABORTIFHUNG,
                3000,
                &mut out,
            );
        }
    }
}

#[cfg(not(windows))]
mod imp {
    pub fn get() -> Option<String> {
        std::env::var(super::VAR).ok()
    }
    pub fn set(_value: Option<&str>) -> Result<(), String> {
        Err("Definir o perfil padrão só é suportado no Windows por enquanto.".into())
    }
}

pub use imp::{get, set};

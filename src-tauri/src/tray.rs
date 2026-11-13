//! Ícone na bandeja do Windows: abrir/trocar perfis sem abrir a janela.
//!
//! Um submenu por ferramenta instalada:
//!   Claude Code ▸  Abrir ▸ <perfis>  ·  Usar como padrão ▸ <perfis>

use crate::profiles::{ProfileInfo, DEFAULT_NAME};
use crate::tools::Tool;
use crate::AppState;
use tauri::menu::{CheckMenuItem, IsMenuItem, Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::{AppHandle, Emitter, Manager, Wry};
use tauri_plugin_notification::NotificationExt;

const TRAY_ID: &str = "main";

fn label(p: &ProfileInfo) -> String {
    let name = if p.name == DEFAULT_NAME { "Padrão" } else { p.name.as_str() };
    match &p.email {
        Some(e) => format!("{name} — {e}"),
        None => name.to_string(),
    }
}

/// IDs: `open|<ferramenta>|<perfil>` e `default|<ferramenta>|<perfil>`.
fn item_id(action: &str, tool: Tool, name: &str) -> String {
    format!("{action}|{}|{name}", tool.id())
}

fn parse_id(id: &str) -> Option<(&str, Tool, &str)> {
    let mut it = id.splitn(3, '|');
    let action = it.next()?;
    let tool = Tool::from_id(it.next()?)?;
    Some((action, tool, it.next()?))
}

fn build_menu(app: &AppHandle, s: &AppState) -> tauri::Result<Menu<Wry>> {
    let menu = Menu::new(app)?;
    let mut any = false;
    for t in s.tools.iter().filter(|t| t.installed) {
        any = true;
        let sub = Submenu::with_id(app, format!("tool|{}", t.tool.id()), &t.label, true)?;
        let open = Submenu::with_id(app, format!("opens|{}", t.tool.id()), "Abrir", true)?;
        for p in &t.profiles {
            open.append(&MenuItem::with_id(app, item_id("open", t.tool, &p.name), label(p), true, None::<&str>)?)?;
        }
        sub.append(&open)?;
        if t.supports_default {
            let def = Submenu::with_id(app, format!("defaults|{}", t.tool.id()), "Usar como padrão", true)?;
            for p in &t.profiles {
                def.append(&CheckMenuItem::with_id(
                    app,
                    item_id("default", t.tool, &p.name),
                    label(p),
                    !p.is_selected,
                    p.is_selected,
                    None::<&str>,
                )?)?;
            }
            sub.append(&def)?;
        }
        menu.append(&sub)?;
    }
    if !any {
        menu.append(&MenuItem::with_id(app, "none", "Nenhuma ferramenta de IA instalada", false, None::<&str>)?)?;
    }
    let tail: [&dyn IsMenuItem<Wry>; 4] = [
        &PredefinedMenuItem::separator(app)?,
        &MenuItem::with_id(app, "show", "Abrir janela", true, None::<&str>)?,
        &MenuItem::with_id(app, "update", "Procurar atualizações", true, None::<&str>)?,
        &MenuItem::with_id(app, "quit", "Sair", true, None::<&str>)?,
    ];
    menu.append_items(&tail)?;
    Ok(menu)
}

pub fn show_window(app: &AppHandle) {
    if let Some(w) = app.get_webview_window("main") {
        let _ = w.unminimize();
        let _ = w.show();
        let _ = w.set_focus();
    }
}

pub fn create(app: &AppHandle) -> tauri::Result<()> {
    let menu = build_menu(app, &crate::state())?;
    TrayIconBuilder::with_id(TRAY_ID)
        .icon(app.default_window_icon().cloned().expect("ícone do app"))
        .tooltip("AI Session Manager")
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_menu_event(|app, ev| {
            let id = ev.id().as_ref();
            let result = match parse_id(id) {
                Some(("open", tool, name)) => crate::do_open(tool, name, None),
                Some(("default", tool, name)) => crate::do_set_default(app, tool, name).map(|_| ()),
                _ => match id {
                    "update" => {
                        let app = app.clone();
                        tauri::async_runtime::spawn(async move {
                            let body = match crate::updates::check(&app, true).await {
                                Ok(None) => format!("Você já está na versão mais recente ({}).", app.package_info().version),
                                Ok(Some(v)) => format!("Atualizando para a versão {v}…"),
                                Err(e) => format!("Não foi possível verificar atualizações: {e}"),
                            };
                            let _ = app.notification().builder().title("AI Session Manager").body(body).show();
                        });
                        Ok(())
                    }
                    "show" => {
                        show_window(app);
                        Ok(())
                    }
                    "quit" => {
                        app.exit(0);
                        Ok(())
                    }
                    _ => Ok(()),
                },
            };
            if let Err(e) = result {
                crate::show_error(&e);
            }
        })
        .on_tray_icon_event(|tray, ev| {
            if let TrayIconEvent::Click { button: MouseButton::Left, button_state: MouseButtonState::Up, .. } = ev {
                show_window(tray.app_handle());
            }
        })
        .build(app)?;
    Ok(())
}

/// Reconstrói o menu com a lista atual e avisa a janela para recarregar.
pub fn refresh(app: &AppHandle, s: &AppState) {
    if let Some(tray) = app.tray_by_id(TRAY_ID) {
        if let Ok(menu) = build_menu(app, s) {
            let _ = tray.set_menu(Some(menu));
        }
    }
    let _ = app.emit("state-changed", ());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ids_roundtrip_with_spaces_and_pipes_in_name() {
        let id = item_id("open", Tool::Codex, "meu perfil");
        assert_eq!(parse_id(&id), Some(("open", Tool::Codex, "meu perfil")));
        assert_eq!(parse_id("show"), None);
    }
}

//! Ícone na bandeja do Windows: troca rápida de perfil sem abrir a janela.

use crate::profiles::{ProfileInfo, State, DEFAULT_NAME};
use tauri::menu::{CheckMenuItem, Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::{AppHandle, Emitter, Manager, Wry};

const TRAY_ID: &str = "main";
const DEFAULT_PREFIX: &str = "default:";
const OPEN_PREFIX: &str = "open:";

fn label(p: &ProfileInfo) -> String {
    let name = if p.name == DEFAULT_NAME { "Padrão" } else { p.name.as_str() };
    match &p.email {
        Some(e) => format!("{name} — {e}"),
        None => name.to_string(),
    }
}

fn build_menu(app: &AppHandle, s: &State) -> tauri::Result<Menu<Wry>> {
    let current = s
        .profiles
        .iter()
        .find(|p| p.is_selected)
        .map(label)
        .unwrap_or_else(|| "pasta externa".into());
    let header = MenuItem::with_id(app, "header", format!("Padrão: {current}"), false, None::<&str>)?;

    let defaults = Submenu::with_id(app, "defaults", "Usar como padrão", true)?;
    let opens = Submenu::with_id(app, "opens", "Abrir Claude", true)?;
    for p in &s.profiles {
        defaults.append(&CheckMenuItem::with_id(
            app,
            format!("{DEFAULT_PREFIX}{}", p.name),
            label(p),
            !p.is_selected,
            p.is_selected,
            None::<&str>,
        )?)?;
        opens.append(&MenuItem::with_id(app, format!("{OPEN_PREFIX}{}", p.name), label(p), true, None::<&str>)?)?;
    }

    Menu::with_items(
        app,
        &[
            &header,
            &PredefinedMenuItem::separator(app)?,
            &defaults,
            &opens,
            &PredefinedMenuItem::separator(app)?,
            &MenuItem::with_id(app, "show", "Abrir janela", true, None::<&str>)?,
            &MenuItem::with_id(app, "quit", "Sair", true, None::<&str>)?,
        ],
    )
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
        .tooltip("Claude Profile Manager")
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_menu_event(|app, ev| {
            let id = ev.id().as_ref();
            let result = if let Some(name) = id.strip_prefix(DEFAULT_PREFIX) {
                crate::do_set_default(app, name).map(|_| ())
            } else if let Some(name) = id.strip_prefix(OPEN_PREFIX) {
                crate::do_open_claude(name)
            } else if id == "show" {
                show_window(app);
                Ok(())
            } else if id == "quit" {
                app.exit(0);
                Ok(())
            } else {
                Ok(())
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
pub fn refresh(app: &AppHandle, s: &State) {
    if let Some(tray) = app.tray_by_id(TRAY_ID) {
        if let Ok(menu) = build_menu(app, s) {
            let _ = tray.set_menu(Some(menu));
        }
    }
    let _ = app.emit("state-changed", ());
}

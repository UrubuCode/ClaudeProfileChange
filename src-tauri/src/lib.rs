mod env;
mod explorer;
mod profiles;
mod tray;

use profiles::{State, Store};
use std::path::{Path, PathBuf};
use std::process::Command;
use tauri::AppHandle;

fn state() -> State {
    Store::from_env().state(env::get())
}

/// Mantém o menu do Explorer e a bandeja em dia com a lista de perfis.
fn sync_menu(app: &AppHandle) -> Result<State, String> {
    let s = state();
    explorer::enable(&s.profiles)?;
    tray::refresh(app, &s);
    Ok(s)
}

pub(crate) fn do_set_default(app: &AppHandle, name: &str) -> Result<State, String> {
    let v = Store::from_env().env_for(name)?;
    env::set(v.as_deref())?;
    sync_menu(app)
}

pub(crate) fn do_open_claude(name: &str) -> Result<(), String> {
    open_claude_in(&Store::from_env(), name, None)
}

#[tauri::command]
fn get_state() -> State {
    state()
}

/// Define o perfil usado por terminais/apps abertos a partir de agora.
#[tauri::command]
fn set_default(app: AppHandle, name: String) -> Result<State, String> {
    do_set_default(&app, &name)
}

#[derive(serde::Serialize)]
struct Created {
    name: String,
    warnings: Vec<String>,
    state: State,
}

#[tauri::command]
fn create_profile(app: AppHandle, name: String) -> Result<Created, String> {
    let s = Store::from_env();
    let (name, warnings) = s.create(&name)?;
    open_claude_in(&s, &name, None)?;
    Ok(Created { name, warnings, state: sync_menu(&app)? })
}

#[tauri::command]
fn rename_profile(app: AppHandle, old: String, new: String) -> Result<State, String> {
    let s = Store::from_env();
    let was_selected = s.state(env::get()).profiles.iter().any(|p| p.name == old && p.is_selected);
    let n = s.rename(&old, &new)?;
    if was_selected {
        env::set(s.env_for(&n)?.as_deref())?;
    }
    sync_menu(&app)
}

#[tauri::command]
fn delete_profile(app: AppHandle, name: String) -> Result<State, String> {
    let s = Store::from_env();
    let was_selected = s.state(env::get()).profiles.iter().any(|p| p.name == name && p.is_selected);
    s.delete(&name)?;
    if was_selected {
        env::set(None)?;
    }
    sync_menu(&app)
}

/// Abre um terminal novo rodando `claude` com o perfil, na pasta `cwd` (ou home).
fn open_claude_in(s: &Store, name: &str, cwd: Option<&Path>) -> Result<(), String> {
    s.dir_of(name)?; // valida
    s.ensure_shared_links(name); // perfis antigos ganham links novos (ex.: sessions)
    let folder = cwd.map(Path::to_path_buf).or_else(dirs::home_dir).unwrap_or_else(|| PathBuf::from("."));
    let title = match folder.file_name() {
        Some(f) => format!("Claude [{name}] - {}", f.to_string_lossy()),
        None => format!("Claude [{name}] - {}", folder.display()),
    };
    let mut cmd = Command::new("cmd");
    // `start` abre uma janela nova; ambiente e pasta são herdados.
    cmd.args(["/c", "start", &title, "powershell", "-NoExit", "-Command", "claude"]);
    // Não herdar marcadores de uma sessão do Claude Code que tenha aberto o app
    // (ex.: CLAUDE_CODE_CHILD_SESSION desliga o salvamento do histórico).
    for k in [
        "CLAUDECODE",
        "CLAUDE_PID",
        "CLAUDE_CODE_ENTRYPOINT",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_CODE_CHILD_SESSION",
        "CLAUDE_CODE_BRIDGE_SESSION_ID",
        "CLAUDE_CODE_MESSAGING_SOCKET",
        "CLAUDE_CODE_MESSAGING_TOKEN",
        "CLAUDE_CODE_SESSION_ATTENDED",
    ] {
        cmd.env_remove(k);
    }
    match s.env_for(name)? {
        Some(v) => cmd.env(env::VAR, v),
        None => cmd.env_remove(env::VAR),
    };
    cmd.current_dir(&folder);
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        cmd.creation_flags(0x0800_0000); // CREATE_NO_WINDOW para o cmd intermediário
    }
    cmd.spawn().map(|_| ()).map_err(|e| format!("Não foi possível abrir o terminal: {e}"))
}

#[tauri::command]
fn open_claude(name: String) -> Result<(), String> {
    do_open_claude(&name)
}

#[tauri::command]
fn open_folder(name: String) -> Result<(), String> {
    let dir = Store::from_env().dir_of(&name)?;
    reveal(&dir)
}

fn reveal(p: &Path) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    let cmd = "explorer";
    #[cfg(target_os = "macos")]
    let cmd = "open";
    #[cfg(all(unix, not(target_os = "macos")))]
    let cmd = "xdg-open";
    Command::new(cmd).arg(p).spawn().map(|_| ()).map_err(|e| e.to_string())
}

/// Modo linha de comando usado pelo menu do Explorer:
/// `claude-profile-manager --open <perfil> <pasta>`. Retorna `true` se tratou.
pub fn handle_cli() -> bool {
    let args: Vec<String> = std::env::args().collect();
    // `--menu on|off`: instala/remove o menu do Explorer (usado também pelo desinstalador).
    if args.get(1).map(String::as_str) == Some("--menu") {
        let r = match args.get(2).map(String::as_str) {
            Some("off") => explorer::disable(),
            _ => explorer::enable(&state().profiles),
        };
        if let Err(e) = r {
            show_error(&e);
            std::process::exit(1);
        }
        return true;
    }
    if args.get(1).map(String::as_str) != Some(explorer::CLI_FLAG) {
        return false;
    }
    let name = args.get(2).cloned().unwrap_or_default();
    let dir = args.get(3).map(|d| PathBuf::from(explorer::fix_dir_arg(d)));
    if let Err(e) = open_claude_in(&Store::from_env(), &name, dir.as_deref()) {
        show_error(&e);
    }
    true
}

#[cfg(windows)]
pub(crate) fn show_error(msg: &str) {
    use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONERROR, MB_OK};
    let w = |s: &str| s.encode_utf16().chain(Some(0)).collect::<Vec<u16>>();
    let (m, t) = (w(msg), w("Claude Profile Manager"));
    unsafe { MessageBoxW(std::ptr::null_mut(), m.as_ptr(), t.as_ptr(), MB_OK | MB_ICONERROR) };
}
#[cfg(not(windows))]
pub(crate) fn show_error(msg: &str) {
    eprintln!("{msg}");
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Menu do Explorer sempre ligado: regrava a cada abertura com o caminho atual
    // do executável (reinstalação/atualização nunca deixa o menu quebrado).
    let _ = explorer::enable(&state().profiles);

    tauri::Builder::default()
        // Precisa ser o primeiro plugin: uma segunda abertura só traz a janela existente.
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            tray::show_window(app);
        }))
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .setup(|app| {
            tray::create(app.handle())?;
            Ok(())
        })
        // Fechar a janela só esconde: o app continua na bandeja ("Sair" encerra).
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                let _ = window.hide();
            }
        })
        .invoke_handler(tauri::generate_handler![
            get_state,
            set_default,
            create_profile,
            rename_profile,
            delete_profile,
            open_claude,
            open_folder
        ])
        .run(tauri::generate_context!())
        .expect("erro ao iniciar o aplicativo");
}

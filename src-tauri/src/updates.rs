//! Atualização automática em segundo plano.
//!
//! - Verifica ao abrir e a cada 6 horas (roda no Rust, funciona com a janela
//!   escondida na bandeja).
//! - Janela escondida: baixa, instala e o app reinicia sozinho.
//! - Janela visível: avisa a interface, que mostra a faixa "Atualizar agora".
//! - Depois de atualizar, mostra uma notificação "Atualizado para a versão X".

use std::path::PathBuf;
use std::time::Duration;
use tauri::{AppHandle, Emitter, Manager};
use tauri_plugin_notification::NotificationExt;
use tauri_plugin_updater::UpdaterExt;

const INTERVAL: Duration = Duration::from_secs(6 * 60 * 60);
const FIRST_DELAY: Duration = Duration::from_secs(30);

/// Arquivo que marca "acabei de instalar a versão X" para notificar após reiniciar.
fn marker() -> Option<PathBuf> {
    dirs::data_local_dir().map(|d| d.join("ClaudeProfileManager").join("updated-to"))
}

fn window_visible(app: &AppHandle) -> bool {
    app.get_webview_window("main")
        .and_then(|w| w.is_visible().ok())
        .unwrap_or(false)
}

fn notify(app: &AppHandle, body: &str) {
    let _ = app
        .notification()
        .builder()
        .title("Claude Profile Manager")
        .body(body)
        .show();
}

/// Verifica e, se `install_now`, instala direto; senão avisa a interface.
/// Retorna a versão encontrada (se houver).
pub async fn check(app: &AppHandle, install_now: bool) -> Result<Option<String>, String> {
    let updater = app.updater().map_err(|e| e.to_string())?;
    let Some(update) = updater.check().await.map_err(|e| e.to_string())? else {
        return Ok(None);
    };
    let version = update.version.clone();
    if !install_now {
        let _ = app.emit("update-available", &version);
        return Ok(Some(version));
    }
    if let Some(m) = marker() {
        let _ = std::fs::create_dir_all(m.parent().unwrap());
        let _ = std::fs::write(&m, &version);
    }
    update
        .download_and_install(|_, _| {}, || {})
        .await
        .map_err(|e| e.to_string())?;
    // No Windows o instalador já encerra e reabre o app; isto cobre o resto.
    app.restart();
}

/// Inicia o laço de verificação e mostra a notificação pós-atualização.
pub fn start(app: &AppHandle) {
    if let Some(m) = marker() {
        if let Ok(v) = std::fs::read_to_string(&m) {
            let _ = std::fs::remove_file(&m);
            if v.trim() == app.package_info().version.to_string() {
                notify(app, &format!("Atualizado para a versão {}.", v.trim()));
            }
        }
    }
    let app = app.clone();
    tauri::async_runtime::spawn(async move {
        tokio_sleep(FIRST_DELAY).await;
        loop {
            // Escondido na bandeja: instala sozinho. Visível: só avisa.
            let _ = check(&app, !window_visible(&app)).await;
            tokio_sleep(INTERVAL).await;
        }
    });
}

async fn tokio_sleep(d: Duration) {
    // Evita depender do tokio diretamente: dorme numa thread de bloqueio.
    let _ = tauri::async_runtime::spawn_blocking(move || std::thread::sleep(d)).await;
}

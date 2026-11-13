// Evita abrir uma janela de console no Windows em release.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    // Chamado pelo menu do Explorer: abre o terminal e sai sem mostrar a janela.
    if ai_session_manager_lib::handle_cli() {
        return;
    }
    ai_session_manager_lib::run()
}

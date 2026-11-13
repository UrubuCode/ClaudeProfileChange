# AI Session Manager

Gerencia várias contas de ferramentas de IA no Windows: **Claude Code**, **Codex** e
**Antigravity** (`agy`). Feito em Rust + Tauri 2 com frontend em React; o instalador tem cerca de 2 MB.

> Antes se chamava **Claude Profile Manager**. Quem tem a versão antiga instalada
> recebe esta pelo auto-update; o instalador remove a versão antiga sozinho.

## Como funciona

Cada conta fica numa pasta própria e a ferramenta é apontada para ela. Nada é
copiado entre contas: cada ferramenta renova o próprio login dentro da pasta da
conta, então trocar de perfil nunca derruba a sessão.

| Ferramenta | Pasta dos perfis | Como o perfil é aplicado |
|---|---|---|
| Claude Code | `~/.claude-profiles/<nome>` | `CLAUDE_CONFIG_DIR` |
| Codex | `~/.codex-profiles/<nome>` | `CODEX_HOME` |
| Antigravity | `~/.agy-profiles/<nome>` | home própria (`USERPROFILE`) + login em arquivo |

O perfil **padrão** de cada ferramenta é a instalação original (`~/.claude`, `~/.codex`, login normal do `agy`).

- **Usar como padrão** (Claude e Codex): grava a variável nas variáveis do usuário;
  vale para terminais e editores abertos depois.
- **Abrir**: abre um terminal (Windows Terminal, se houver) com o perfil só naquela
  janela — dá para usar várias contas ao mesmo tempo.
- **Botão direito numa pasta → "Mostrar mais opções" → "Abrir IA aqui"**.
- **Bandeja**: fechar a janela mantém o app na bandeja, com atalhos por ferramenta.
- **Auto-update** em segundo plano.
- Skills, plugins, agentes e regras de cada ferramenta são compartilhados com a
  instalação original por junction.

## Desenvolvimento

Requisitos: Rust (stable), Node.js 18+ e o WebView2, que já vem no Windows 11.

```powershell
npm install
npx tauri dev                    # modo desenvolvimento
npx tauri build                  # instaladores em src-tauri/target/release/bundle/
cd src-tauri; cargo test         # testes do backend
```

### Publicar uma versão

Suba a versão em `package.json`, `src-tauri/tauri.conf.json` e `src-tauri/Cargo.toml`,
faça commit e envie uma tag `vX.Y.Z`. O GitHub Actions compila, assina (secret
`TAURI_SIGNING_PRIVATE_KEY`) e publica a release com o `latest.json` do auto-update.

Linha de comando do executável:

| Comando | Efeito |
|---|---|
| `ai-session-manager --menu on\|off` | instala ou remove o menu do Explorer |
| `ai-session-manager --open <claude\|codex\|agy> <perfil> <pasta>` | abre a ferramenta na pasta com o perfil |

## Estrutura

```
src/                  frontend React (App.tsx, api.ts)
src-tauri/src/
  tools.rs            ferramentas suportadas e como cada uma isola um perfil
  profiles.rs         perfis por ferramenta (criar, listar, excluir, conta)
  terminal.rs         abre o terminal com o perfil aplicado
  env.rs              leitura e gravação da variável no HKCU\Environment
  explorer.rs         menu de contexto do Explorer
  lib.rs              comandos Tauri e modo linha de comando
```

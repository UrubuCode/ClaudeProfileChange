# Claude Profile Manager

Gerencia várias contas do [Claude Code](https://claude.com/claude-code) no Windows.
Feito em Rust + Tauri 2 com frontend em React. O instalador tem cerca de 1 MB.

## Como funciona

Cada conta fica numa pasta própria em `~/.claude-profiles/<nome>/`, e o Claude é
apontado para ela pela variável `CLAUDE_CONFIG_DIR`. A pasta `~/.claude` original
é o perfil **padrão**.

Nada é copiado entre contas: o Claude renova o token dentro da pasta de cada conta,
então trocar de perfil nunca desconecta a sessão.

- **Usar como padrão**: grava `CLAUDE_CONFIG_DIR` nas variáveis do usuário. Vale
  para terminais e apps abertos depois da troca.
- **Abrir Claude**: abre um terminal com o perfil só naquela janela, o que permite
  usar várias contas ao mesmo tempo.
- **Menu no Explorer**: com o botão direito numa pasta, "Abrir Claude aqui ▸ perfil"
  (no Windows 11, fica em "Mostrar mais opções").
- `skills`, `plugins`, `agents` e `commands` são compartilhados com o `~/.claude`
  por junction. `settings.json` e `CLAUDE.md` são copiados quando o perfil é criado.

### Nova conta

1. Clique em **+ Nova** e dê um nome. Um terminal do Claude abre já no perfil novo.
2. Digite `/login` e entre com a outra conta. Use uma janela anônima se o navegador
   já estiver logado em outra conta.

## Desenvolvimento

Requisitos: Rust (stable), Node.js 18+ e o WebView2, que já vem no Windows 11.

```powershell
npm install
npx tauri dev                    # modo desenvolvimento
npx tauri build                  # instaladores em src-tauri/target/release/bundle/
cd src-tauri; cargo test         # testes do backend
```

Linha de comando do executável:

| Comando | Efeito |
|---|---|
| `claude-profile-manager --menu on\|off` | instala ou remove o menu do Explorer |
| `claude-profile-manager --open <perfil> <pasta>` | abre o Claude na pasta com o perfil |

## Estrutura

```
src/                  frontend React (App.tsx, api.ts)
src-tauri/src/
  profiles.rs         perfis = pastas com CLAUDE_CONFIG_DIR
  env.rs              leitura e gravação da variável no HKCU\Environment
  explorer.rs         menu de contexto do Explorer
  lib.rs              comandos Tauri e modo linha de comando
```

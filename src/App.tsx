import { useCallback, useEffect, useRef, useState } from "react";
import { api, formatDate, formatLeft, sessionStatus, type ProfileInfo, type State } from "./api";
import { Dialog, type DialogRequest } from "./Dialog";
import { Updater } from "./Updater";

type Menu = "arquivo" | "perfil" | null;
interface Ctx { x: number; y: number; name: string }

export default function App() {
  const [state, setState] = useState<State | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [status, setStatus] = useState<{ text: string; error?: boolean }>({ text: "Pronto" });
  const [dialog, setDialog] = useState<DialogRequest | null>(null);
  const [menu, setMenu] = useState<Menu>(null);
  const [ctx, setCtx] = useState<Ctx | null>(null);
  const busy = useRef(false);

  const ask = (r: Omit<DialogRequest, "resolve">) =>
    new Promise<string | null>((resolve) => setDialog({ ...r, resolve }));
  const fail = (e: unknown) => setStatus({ text: String(e), error: true });

  const run = useCallback(async <T,>(action: () => Promise<T>, ok?: string): Promise<T | undefined> => {
    if (busy.current) return;
    busy.current = true;
    try {
      const r = await action();
      if (ok) setStatus({ text: ok });
      return r;
    } catch (e) {
      fail(e);
    } finally {
      busy.current = false;
    }
  }, []);

  const load = useCallback(async (ok?: string) => {
    const s = await run(api.getState, ok);
    if (s) setState(s);
  }, [run]);

  useEffect(() => {
    load();
    const onFocus = () => load();
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [load]);

  useEffect(() => {
    if (!state) return;
    if (selected && state.profiles.some((p) => p.name === selected)) return;
    setSelected(state.profiles.find((p) => p.isSelected)?.name ?? state.profiles[0]?.name ?? null);
  }, [state, selected]);

  const profile = state?.profiles.find((p) => p.name === selected);

  // ---- ações ----
  const setDefault = async (name = selected) => {
    if (!name) return;
    const s = await run(() => api.setDefault(name),
      `"${name}" agora é o padrão — vale para terminais e apps abertos daqui em diante`);
    if (s) setState(s);
  };

  const openClaude = (name = selected) => name && run(() => api.openClaude(name), `Abrindo Claude com "${name}"…`);
  const openFolder = (name = selected) => name && api.openFolder(name).catch(fail);

  const create = async () => {
    const name = await ask({
      message: "Nome da nova conta. Vou abrir um terminal do Claude nela — digite /login e entre com a conta.",
      input: "", okLabel: "Criar e abrir",
    });
    if (!name) return;
    const c = await run(() => api.createProfile(name));
    if (!c) return;
    setState(c.state);
    setSelected(c.name);
    setStatus(c.warnings.length
      ? { text: `Perfil "${c.name}" criado, com avisos: ${c.warnings.join("; ")}`, error: true }
      : { text: `Perfil "${c.name}" criado — faça /login no terminal que abriu` });
  };

  const rename = async (name = selected) => {
    if (!name || isDefault(name)) return;
    const n = await ask({ message: `Novo nome para "${name}":`, input: name, okLabel: "Renomear" });
    if (!n || n === name) return;
    const s = await run(() => api.renameProfile(name, n), `"${name}" renomeado para "${n}"`);
    if (s) { setState(s); setSelected(n); }
  };

  const remove = async (name = selected) => {
    if (!name || isDefault(name)) return;
    const ok = await ask({
      message: `Excluir o perfil "${name}"? A pasta dele (login e histórico dessa conta) será apagada. Skills e plugins compartilhados não são afetados.`,
      okLabel: "Excluir", danger: true,
    });
    if (ok === null) return;
    const s = await run(() => api.deleteProfile(name), `Perfil "${name}" excluído`);
    if (s) setState(s);
  };

  const toggleExplorer = async () => {
    const on = !state?.explorerMenu;
    const s = await run(() => api.setExplorerMenu(on), on
      ? 'Menu instalado: clique direito numa pasta → "Mostrar mais opções" → "Abrir Claude aqui"'
      : "Menu removido do Explorer");
    if (s) setState(s);
  };

  const isDefault = (name: string) => state?.profiles.find((p) => p.name === name)?.isDefaultProfile ?? false;

  // ---- atalhos ----
  const keys = useRef<(e: KeyboardEvent) => void>();
  keys.current = (e) => {
    if (dialog || e.target instanceof HTMLInputElement) return;
    const list = state?.profiles.map((p) => p.name) ?? [];
    const k = e.key, ctrl = e.ctrlKey, lk = k.toLowerCase();
    if (ctrl && lk === "n") create();
    else if (ctrl && lk === "o") openFolder();
    else if (ctrl && lk === "t") openClaude();
    else if (k === "F5" || (ctrl && lk === "r")) load("Atualizado");
    else if (k === "Enter") setDefault();
    else if (k === "F2") rename();
    else if (k === "Delete") remove();
    else if (k === "Escape") { setMenu(null); setCtx(null); return; }
    else if (k === "ArrowDown" || k === "ArrowUp") {
      if (!list.length) return;
      const i = selected ? list.indexOf(selected) : -1;
      setSelected(list[k === "ArrowDown" ? Math.min(list.length - 1, i + 1) : Math.max(0, i - 1)]);
    } else return;
    e.preventDefault();
  };
  useEffect(() => {
    const h = (e: KeyboardEvent) => keys.current?.(e);
    const close = () => { setMenu(null); setCtx(null); };
    window.addEventListener("keydown", h);
    window.addEventListener("click", close);
    window.addEventListener("blur", close);
    return () => {
      window.removeEventListener("keydown", h);
      window.removeEventListener("click", close);
      window.removeEventListener("blur", close);
    };
  }, []);

  const total = state?.profiles.length ?? 0;
  const current = state?.profiles.find((p) => p.isSelected);

  return (
    <div className="app" onContextMenu={(e) => e.preventDefault()}>
      <nav className="menubar" onClick={(e) => e.stopPropagation()}>
        <MenuButton id="arquivo" label="Arquivo" open={menu} setOpen={setMenu}>
          <Item label="Nova conta…" hint="Ctrl+N" onClick={create} />
          <Item label={(state?.explorerMenu ? "✓ " : "") + "Menu \"Abrir Claude aqui\" no Explorer"} onClick={toggleExplorer} />
          <Item label="Atualizar" hint="F5" onClick={() => load("Atualizado")} />
        </MenuButton>
        <MenuButton id="perfil" label="Perfil" open={menu} setOpen={setMenu}>
          <Item label="Usar como padrão" hint="Enter" onClick={() => setDefault()} disabled={!profile || profile.isSelected} />
          <Item label="Abrir Claude neste perfil" hint="Ctrl+T" onClick={() => openClaude()} disabled={!profile} />
          <Item label="Abrir pasta" hint="Ctrl+O" onClick={() => openFolder()} disabled={!profile} />
          <Item label="Renomear…" hint="F2" onClick={() => rename()} disabled={!profile || profile.isDefaultProfile} />
          <Item label="Excluir…" hint="Del" onClick={() => remove()} disabled={!profile || profile.isDefaultProfile} danger />
        </MenuButton>
        <div className="counters">
          <span>{total} {total === 1 ? "perfil" : "perfis"}</span>
          <span>Padrão: <b>{current ? label(current) : "pasta externa"}</b></span>
        </div>
      </nav>

      <Updater />

      {state?.envUnknown && (
        <div className="banner">
          CLAUDE_CONFIG_DIR aponta para <code>{state.envValue}</code>, que não é um perfil deste app.
        </div>
      )}

      <div className="main">
        <aside className="sidebar">
          <div className="sidebar-head">
            <span>Contas</span>
            <button className="small" onClick={create} title="Nova conta (Ctrl+N)">+ Nova</button>
          </div>
          <ul>
            {state?.profiles.map((p) => (
              <ProfileRow key={p.name} p={p} selected={selected === p.name}
                onSelect={() => setSelected(p.name)}
                onOpen={() => setDefault(p.name)}
                onContext={(x, y) => { setSelected(p.name); setMenu(null); setCtx({ x, y, name: p.name }); }} />
            ))}
          </ul>
        </aside>

        <section className="detail">
          {profile ? (
            <Detail p={profile} onDefault={() => setDefault()} onOpen={() => openClaude()} onFolder={() => openFolder()}
              onRename={() => rename()} onDelete={() => remove()} />
          ) : <div className="placeholder">Selecione um perfil</div>}
        </section>
      </div>

      <footer className={"statusbar" + (status.error ? " error" : "")}>
        <span className="status-text" title={status.text}>{status.text}</span>
        <label className="toggle" title="Clique direito numa pasta → Abrir Claude aqui → perfil">
          <input type="checkbox" checked={!!state?.explorerMenu} onChange={toggleExplorer} />
          Menu no Explorer
        </label>
      </footer>

      {ctx && (() => {
        const p = state?.profiles.find((x) => x.name === ctx.name);
        const close = (f: () => void) => () => { setCtx(null); f(); };
        return (
          <div className="menu context" style={{ left: ctx.x, top: ctx.y }} onClick={(e) => e.stopPropagation()}>
            <Item label="Usar como padrão" hint="Enter" onClick={close(() => setDefault(ctx.name))} disabled={p?.isSelected} />
            <Item label="Abrir Claude" hint="Ctrl+T" onClick={close(() => openClaude(ctx.name))} />
            <Item label="Abrir pasta" hint="Ctrl+O" onClick={close(() => openFolder(ctx.name))} />
            <Item label="Renomear…" hint="F2" onClick={close(() => rename(ctx.name))} disabled={p?.isDefaultProfile} />
            <Item label="Excluir…" hint="Del" onClick={close(() => remove(ctx.name))} disabled={p?.isDefaultProfile} danger />
          </div>
        );
      })()}

      {dialog && <Dialog req={dialog} onClose={() => setDialog(null)} />}
    </div>
  );
}

const label = (p: ProfileInfo) => (p.isDefaultProfile ? "padrão (~/.claude)" : p.name);

function MenuButton(props: { id: Exclude<Menu, null>; label: string; open: Menu; setOpen: (m: Menu) => void; children: React.ReactNode }) {
  const isOpen = props.open === props.id;
  return (
    <div className="menu-root">
      <button className={"menu-btn" + (isOpen ? " open" : "")}
        onClick={() => props.setOpen(isOpen ? null : props.id)}
        onMouseEnter={() => props.open && props.setOpen(props.id)}>
        {props.label}
      </button>
      {isOpen && <div className="menu" onClick={() => props.setOpen(null)}>{props.children}</div>}
    </div>
  );
}

function Item(p: { label: string; hint?: string; onClick: () => void; disabled?: boolean; danger?: boolean }) {
  return (
    <button className={"menu-item" + (p.danger ? " danger-text" : "")} disabled={p.disabled} onClick={p.onClick}>
      <span>{p.label}</span>
      {p.hint && <kbd>{p.hint}</kbd>}
    </button>
  );
}

function ProfileRow(props: { p: ProfileInfo; selected: boolean; onSelect: () => void; onOpen: () => void; onContext: (x: number, y: number) => void }) {
  const { p } = props;
  return (
    <li className={"row" + (props.selected ? " selected" : "")}
      onClick={(e) => { e.stopPropagation(); props.onSelect(); }}
      onDoubleClick={props.onOpen}
      onContextMenu={(e) => { e.preventDefault(); e.stopPropagation(); props.onContext(e.clientX, e.clientY); }}
      title="Duplo-clique para usar como padrão">
      <span className={"dot " + sessionStatus(p).tone} />
      <span className="row-text">
        <span className="row-name">{label(p)}</span>
        <span className="row-sub">{p.email ?? (p.loggedIn ? "conta sem e-mail" : "sem login")}</span>
      </span>
      {p.isSelected && <span className="badge">padrão</span>}
    </li>
  );
}

function Detail(props: { p: ProfileInfo; onDefault: () => void; onOpen: () => void; onFolder: () => void; onRename: () => void; onDelete: () => void }) {
  const { p } = props;
  const st = sessionStatus(p);
  return (
    <div className="detail-inner">
      <div className="detail-head">
        <div>
          <h2>{label(p)}</h2>
          <div className="sub">{p.email ?? "Sem conta logada"}{p.organization ? ` · ${p.organization}` : ""}</div>
        </div>
        <div className="detail-actions">
          <button onClick={props.onDefault} disabled={p.isSelected}>{p.isSelected ? "É o padrão" : "Usar como padrão"}</button>
          <button className="ghost" onClick={props.onOpen}>{p.loggedIn ? "Abrir Claude" : "Abrir e fazer login"}</button>
        </div>
      </div>

      <div className="cards">
        <Card title="Sessão"><span className={"tone " + st.tone}>{st.text}</span></Card>
        <Card title="Plano">{p.plan ?? cap(p.subscriptionType) ?? "—"}</Card>
        <Card title="Access token">
          {p.loggedIn ? (p.expiresAt > Date.now() ? formatLeft(p.expiresAt) : "Renova sozinho ao usar") : "—"}
          <small>{formatDate(p.expiresAt)}</small>
        </Card>
        <Card title="Login válido até">
          {p.refreshExpiresAt ? formatLeft(p.refreshExpiresAt) : "—"}
          <small>{formatDate(p.refreshExpiresAt)}</small>
        </Card>
        <Card title="Rate limit tier"><code>{p.rateLimitTier ?? "—"}</code></Card>
        <Card title="Escopos" wide>
          {p.scopes.length ? <div className="chips">{p.scopes.map((s) => <span key={s} className="chip">{s}</span>)}</div> : "—"}
        </Card>
        <Card title="Pasta" wide>
          <code className="selectable">{p.path}</code>
        </Card>
      </div>

      <div className="detail-footer">
        <button className="ghost" onClick={props.onFolder}>Abrir pasta</button>
        {!p.isDefaultProfile && <>
          <button className="ghost" onClick={props.onRename}>Renomear</button>
          <button className="danger" onClick={props.onDelete}>Excluir</button>
        </>}
      </div>

      <p className="hint">
        "Usar como padrão" grava <code>CLAUDE_CONFIG_DIR</code> nas variáveis do seu usuário. Terminais e o VS Code
        já abertos continuam na conta anterior até serem reabertos. "Abrir Claude" usa o perfil só naquela janela.
      </p>
    </div>
  );
}

function Card(p: { title: string; wide?: boolean; children: React.ReactNode }) {
  return (
    <div className={"card" + (p.wide ? " wide" : "")}>
      <div className="card-title">{p.title}</div>
      <div className="card-body">{p.children}</div>
    </div>
  );
}

const cap = (s: string | null) => (s ? s[0].toUpperCase() + s.slice(1) : null);

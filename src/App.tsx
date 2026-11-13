import { useCallback, useEffect, useRef, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import {
  api, formatDate, formatLeft, sessionStatus,
  type AppState, type ProfileInfo, type ToolId, type ToolState,
} from "./api";
import { Dialog, type DialogRequest } from "./Dialog";
import { Updater } from "./Updater";

type Menu = "arquivo" | "perfil" | null;
interface Ctx { x: number; y: number; name: string }

const TOOL_KEY = "selectedTool";
const readTool = (): ToolId => {
  try { return (localStorage.getItem(TOOL_KEY) as ToolId) || "claude"; } catch { return "claude"; }
};

export default function App() {
  const [state, setState] = useState<AppState | null>(null);
  const [toolId, setToolId] = useState<ToolId>(readTool);
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
    const unlisten = listen("state-changed", () => load());
    return () => {
      window.removeEventListener("focus", onFocus);
      unlisten.then((f) => f());
    };
  }, [load]);

  const tool: ToolState | undefined = state?.tools.find((t) => t.tool === toolId) ?? state?.tools[0];
  const profiles = tool?.profiles ?? [];

  const chooseTool = (id: ToolId) => {
    setToolId(id);
    setSelected(null);
    try { localStorage.setItem(TOOL_KEY, id); } catch { /* sem storage */ }
  };

  useEffect(() => {
    if (!tool) return;
    if (selected && tool.profiles.some((p) => p.name === selected)) return;
    setSelected(tool.profiles.find((p) => p.isSelected)?.name ?? tool.profiles[0]?.name ?? null);
  }, [tool, selected]);

  const profile = profiles.find((p) => p.name === selected);
  const label = (p: ProfileInfo) => (p.isDefaultProfile ? "padrão" : p.name);

  // ---- ações (sempre na ferramenta da aba atual) ----
  const t = tool?.tool ?? "claude";
  const tLabel = tool?.label ?? "";

  const setDefault = async (name = selected) => {
    if (!name || !tool?.supportsDefault) return;
    const s = await run(() => api.setDefault(t, name),
      `${tLabel}: "${name}" agora é o padrão — vale para terminais e apps abertos daqui em diante`);
    if (s) setState(s);
  };

  const openTool = (name = selected) =>
    name && run(() => api.openTool(t, name), `Abrindo ${tLabel} com "${name}"…`);
  const openFolder = (name = selected) => name && api.openFolder(t, name).catch(fail);

  const create = async () => {
    if (!tool) return;
    const name = await ask({
      message: tool.installed
        ? `Nome do novo perfil de ${tLabel}. Vou abrir o ${tool.command} nele — faça o login com a conta desejada.`
        : `Nome do novo perfil de ${tLabel}. (O comando "${tool.command}" não foi encontrado; instale-o para usar o perfil.)`,
      input: "", okLabel: tool.installed ? "Criar e abrir" : "Criar",
    });
    if (!name) return;
    const c = await run(() => api.createProfile(t, name));
    if (!c) return;
    setState(c.state);
    setSelected(c.name);
    setStatus(c.warnings.length
      ? { text: `Perfil "${c.name}" criado, com avisos: ${c.warnings.join("; ")}`, error: true }
      : { text: `Perfil "${c.name}" de ${tLabel} criado${tool.installed ? " — faça o login no terminal que abriu" : ""}` });
  };

  const rename = async (name = selected) => {
    const p = profiles.find((x) => x.name === name);
    if (!name || !p || p.isDefaultProfile) return;
    const n = await ask({ message: `Novo nome para "${name}":`, input: name, okLabel: "Renomear" });
    if (!n || n === name) return;
    const s = await run(() => api.renameProfile(t, name, n), `"${name}" renomeado para "${n}"`);
    if (s) { setState(s); setSelected(n); }
  };

  const remove = async (name = selected) => {
    const p = profiles.find((x) => x.name === name);
    if (!name || !p || p.isDefaultProfile) return;
    const ok = await ask({
      message: `Excluir o perfil "${name}" de ${tLabel}? A pasta dele (login, histórico e conversas dessa conta) será apagada. Itens compartilhados não são afetados.`,
      okLabel: "Excluir", danger: true,
    });
    if (ok === null) return;
    const s = await run(() => api.deleteProfile(t, name), `Perfil "${name}" excluído`);
    if (s) setState(s);
  };

  // ---- atalhos ----
  const keys = useRef<(e: KeyboardEvent) => void>();
  keys.current = (e) => {
    if (dialog || e.target instanceof HTMLInputElement) return;
    const list = profiles.map((p) => p.name);
    const k = e.key, ctrl = e.ctrlKey, lk = k.toLowerCase();
    const n = Number(k);
    if (ctrl && n >= 1 && n <= (state?.tools.length ?? 0)) chooseTool(state!.tools[n - 1].tool);
    else if (ctrl && lk === "n") create();
    else if (ctrl && lk === "o") openFolder();
    else if (ctrl && lk === "t") openTool();
    else if (k === "F5" || (ctrl && lk === "r")) load("Atualizado");
    else if (k === "Enter") (tool?.supportsDefault ? setDefault() : openTool());
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

  const totalProfiles = state?.tools.reduce((a, x) => a + x.profiles.length, 0) ?? 0;
  const current = profiles.find((p) => p.isSelected);

  return (
    <div className="app" onContextMenu={(e) => e.preventDefault()}>
      <nav className="menubar" onClick={(e) => e.stopPropagation()}>
        <MenuButton id="arquivo" label="Arquivo" open={menu} setOpen={setMenu}>
          <Item label={`Novo perfil de ${tLabel}…`} hint="Ctrl+N" onClick={create} />
          <Item label="Atualizar" hint="F5" onClick={() => load("Atualizado")} />
        </MenuButton>
        <MenuButton id="perfil" label="Perfil" open={menu} setOpen={setMenu}>
          {tool?.supportsDefault && (
            <Item label="Usar como padrão" hint="Enter" onClick={() => setDefault()} disabled={!profile || profile.isSelected} />
          )}
          <Item label={`Abrir ${tLabel}`} hint="Ctrl+T" onClick={() => openTool()} disabled={!profile || !tool?.installed} />
          <Item label="Abrir pasta" hint="Ctrl+O" onClick={() => openFolder()} disabled={!profile} />
          <Item label="Renomear…" hint="F2" onClick={() => rename()} disabled={!profile || profile.isDefaultProfile} />
          <Item label="Excluir…" hint="Del" onClick={() => remove()} disabled={!profile || profile.isDefaultProfile} danger />
        </MenuButton>
        <div className="counters">
          <span>{totalProfiles} perfis</span>
          {tool?.supportsDefault && <span>{tLabel}: <b>{current ? label(current) : "pasta externa"}</b></span>}
        </div>
      </nav>

      <Updater />

      <div className="tabs" role="tablist">
        {state?.tools.map((x, i) => (
          <button key={x.tool} role="tab" aria-selected={x.tool === t}
            className={"tab" + (x.tool === t ? " active" : "") + (x.installed ? "" : " missing")}
            title={(x.installed ? "" : `"${x.command}" não encontrado no PATH · `) + `Ctrl+${i + 1}`}
            onClick={() => chooseTool(x.tool)}>
            <ToolMark tool={x.tool} />
            <span>{x.label}</span>
            <span className="count">{x.profiles.length}</span>
          </button>
        ))}
      </div>

      {tool && !tool.installed && (
        <div className="banner">
          O comando <code>{tool.command}</code> não foi encontrado. Você pode criar perfis, mas para usá-los instale o {tLabel} e reabra o app.
        </div>
      )}
      {tool?.envUnknown && (
        <div className="banner">
          <code>{tool.envVar}</code> aponta para <code>{tool.envValue}</code>, que não é um perfil deste app.
        </div>
      )}

      <div className="main">
        <aside className="sidebar">
          <div className="sidebar-head">
            <span>Perfis · {tLabel}</span>
            <button className="small" onClick={create} title="Novo perfil (Ctrl+N)">+ Novo</button>
          </div>
          <ul>
            {profiles.map((p) => (
              <ProfileRow key={p.name} p={p} label={label(p)} selected={selected === p.name}
                badge={tool?.supportsDefault && p.isSelected ? "padrão" : null}
                onSelect={() => setSelected(p.name)}
                onOpen={() => (tool?.supportsDefault ? setDefault(p.name) : openTool(p.name))}
                onContext={(x, y) => { setSelected(p.name); setMenu(null); setCtx({ x, y, name: p.name }); }} />
            ))}
          </ul>
        </aside>

        <section className="detail">
          {profile && tool ? (
            <Detail p={profile} tool={tool} title={label(profile)}
              onDefault={() => setDefault()} onOpen={() => openTool()} onFolder={() => openFolder()}
              onRename={() => rename()} onDelete={() => remove()} />
          ) : <div className="placeholder">Selecione um perfil</div>}
        </section>
      </div>

      <footer className={"statusbar" + (status.error ? " error" : "")}>
        <span className="status-text" title={status.text}>{status.text}</span>
        <span className="path" title={tool?.profilesRoot}>{tool?.profilesRoot}</span>
      </footer>

      {ctx && (() => {
        const p = profiles.find((x) => x.name === ctx.name);
        const close = (f: () => void) => () => { setCtx(null); f(); };
        return (
          <div className="menu context" style={{ left: ctx.x, top: ctx.y }} onClick={(e) => e.stopPropagation()}>
            {tool?.supportsDefault && (
              <Item label="Usar como padrão" hint="Enter" onClick={close(() => setDefault(ctx.name))} disabled={p?.isSelected} />
            )}
            <Item label={`Abrir ${tLabel}`} hint="Ctrl+T" onClick={close(() => openTool(ctx.name))} disabled={!tool?.installed} />
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

function ToolMark({ tool }: { tool: ToolId }) {
  return <span className={"mark mark-" + tool} aria-hidden="true">{tool === "claude" ? "C" : tool === "codex" ? "X" : "A"}</span>;
}

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

function ProfileRow(props: {
  p: ProfileInfo; label: string; selected: boolean; badge: string | null;
  onSelect: () => void; onOpen: () => void; onContext: (x: number, y: number) => void;
}) {
  const { p } = props;
  return (
    <li className={"row" + (props.selected ? " selected" : "")}
      onClick={(e) => { e.stopPropagation(); props.onSelect(); }}
      onDoubleClick={props.onOpen}
      onContextMenu={(e) => { e.preventDefault(); e.stopPropagation(); props.onContext(e.clientX, e.clientY); }}>
      <span className={"dot " + sessionStatus(p).tone} />
      <span className="row-text">
        <span className="row-name">{props.label}</span>
        <span className="row-sub">{p.email ?? (p.loggedIn ? "conta sem e-mail" : "sem login")}</span>
      </span>
      {props.badge && <span className="badge">{props.badge}</span>}
    </li>
  );
}

function Detail(props: {
  p: ProfileInfo; tool: ToolState; title: string;
  onDefault: () => void; onOpen: () => void; onFolder: () => void; onRename: () => void; onDelete: () => void;
}) {
  const { p, tool } = props;
  const st = sessionStatus(p);
  return (
    <div className="detail-inner">
      <div className="detail-head">
        <div>
          <h2>{props.title}</h2>
          <div className="sub">{p.email ?? "Sem conta logada"}{p.organization ? ` · ${p.organization}` : ""}</div>
        </div>
        <div className="detail-actions">
          {tool.supportsDefault && (
            <button onClick={props.onDefault} disabled={p.isSelected}>{p.isSelected ? "É o padrão" : "Usar como padrão"}</button>
          )}
          <button className={tool.supportsDefault ? "ghost" : ""} onClick={props.onOpen} disabled={!tool.installed}>
            {p.loggedIn ? `Abrir ${tool.label}` : "Abrir e fazer login"}
          </button>
        </div>
      </div>

      <div className="cards">
        <Card title="Sessão"><span className={"tone " + st.tone}>{st.text}</span></Card>
        <Card title="Plano">{p.plan ?? "—"}</Card>
        {p.expiresAt != null && p.loggedIn && (
          <Card title="Access token">
            {p.expiresAt > Date.now() ? formatLeft(p.expiresAt) : "Renova sozinho ao usar"}
            <small>{formatDate(p.expiresAt)}</small>
          </Card>
        )}
        {p.refreshExpiresAt != null && (
          <Card title="Login válido até">
            {formatLeft(p.refreshExpiresAt)}
            <small>{formatDate(p.refreshExpiresAt)}</small>
          </Card>
        )}
        {p.details.map((d) => <Card key={d.label} title={d.label}>{d.value}</Card>)}
        {p.scopes.length > 0 && (
          <Card title="Escopos" wide>
            <div className="chips">{p.scopes.map((s) => <span key={s} className="chip">{s}</span>)}</div>
          </Card>
        )}
        <Card title="Pasta" wide><code className="selectable">{p.path}</code></Card>
      </div>

      <div className="detail-footer">
        <button className="ghost" onClick={props.onFolder}>Abrir pasta</button>
        {!p.isDefaultProfile && <>
          <button className="ghost" onClick={props.onRename}>Renomear</button>
          <button className="danger" onClick={props.onDelete}>Excluir</button>
        </>}
      </div>

      <p className="hint">
        {tool.supportsDefault ? (
          <>"Usar como padrão" grava <code>{tool.envVar}</code> nas variáveis do seu usuário. Terminais e editores já
            abertos continuam na conta anterior até serem reabertos. "Abrir {tool.label}" usa o perfil só naquela janela.</>
        ) : (
          <>O {tool.label} não tem uma variável de sistema para trocar de conta: o padrão é sempre o login normal.
            Use "Abrir {tool.label}" ou o botão direito no Explorer para usar outro perfil.</>
        )}
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

import { useEffect, useState } from "react";
import { check, type Update } from "@tauri-apps/plugin-updater";
import { relaunch } from "@tauri-apps/plugin-process";
import { listen } from "@tauri-apps/api/event";

type Phase =
  | { kind: "idle" }
  | { kind: "available"; update: Update }
  | { kind: "downloading"; pct: number | null }
  | { kind: "error"; msg: string };

/** Verifica atualizações ao abrir o app e oferece instalar. */
export function Updater() {
  const [phase, setPhase] = useState<Phase>({ kind: "idle" });

  useEffect(() => {
    // Em `tauri dev` não há release correspondente; ignore falhas silenciosamente.
    const lookup = () =>
      check()
        .then((u) => u && setPhase((p) => (p.kind === "idle" ? { kind: "available", update: u } : p)))
        .catch(() => {});
    lookup();
    // A verificação periódica roda no Rust; com a janela visível ela avisa aqui.
    const unlisten = listen("update-available", lookup);
    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  if (phase.kind === "idle") return null;

  const install = async (update: Update) => {
    let total = 0, got = 0;
    setPhase({ kind: "downloading", pct: null });
    try {
      await update.downloadAndInstall((ev) => {
        if (ev.event === "Started") total = ev.data.contentLength ?? 0;
        if (ev.event === "Progress") {
          got += ev.data.chunkLength;
          setPhase({ kind: "downloading", pct: total ? Math.round((got / total) * 100) : null });
        }
      });
      await relaunch(); // no Windows o instalador já fecha o app; isso cobre os demais casos
    } catch (e) {
      setPhase({ kind: "error", msg: String(e) });
    }
  };

  return (
    <div className="banner update">
      {phase.kind === "available" && (
        <>
          <span>Nova versão <b>{phase.update.version}</b> disponível.</span>
          <button className="small" onClick={() => install(phase.update)}>Atualizar agora</button>
          <button className="small ghost" onClick={() => setPhase({ kind: "idle" })}>Depois</button>
        </>
      )}
      {phase.kind === "downloading" && (
        <span>Baixando atualização{phase.pct !== null ? ` — ${phase.pct}%` : "…"} O app vai reiniciar sozinho.</span>
      )}
      {phase.kind === "error" && (
        <>
          <span className="bad">Falha ao atualizar: {phase.msg}</span>
          <button className="small ghost" onClick={() => setPhase({ kind: "idle" })}>Fechar</button>
        </>
      )}
    </div>
  );
}

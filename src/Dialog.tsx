import { useEffect, useRef, useState } from "react";

export interface DialogRequest {
  message: string;
  okLabel: string;
  danger?: boolean;
  /** Se definido, mostra um campo de texto com esse valor inicial. */
  input?: string;
  resolve: (value: string | null) => void;
}

export function Dialog({ req, onClose }: { req: DialogRequest; onClose: () => void }) {
  const [value, setValue] = useState(req.input ?? "");
  const inputRef = useRef<HTMLInputElement>(null);
  const okRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (req.input !== undefined) inputRef.current?.select();
    else okRef.current?.focus();
  }, [req]);

  const finish = (v: string | null) => {
    req.resolve(v);
    onClose();
  };

  return (
    <div className="backdrop" onMouseDown={() => finish(null)}>
      <form
        className="dialog"
        onMouseDown={(e) => e.stopPropagation()}
        onKeyDown={(e) => e.key === "Escape" && finish(null)}
        onSubmit={(e) => {
          e.preventDefault();
          finish(req.input !== undefined ? value.trim() : "");
        }}
      >
        <p>{req.message}</p>
        {req.input !== undefined && (
          <input ref={inputRef} value={value} onChange={(e) => setValue(e.target.value)} />
        )}
        <div className="dialog-btns">
          <button type="button" className="ghost" onClick={() => finish(null)}>
            Cancelar
          </button>
          <button ref={okRef} type="submit" className={req.danger ? "danger solid" : ""}>
            {req.okLabel}
          </button>
        </div>
      </form>
    </div>
  );
}

import threading
import queue
import tkinter as tk
from tkinter import ttk
import os

# --- fila para mensagens thread->UI ---
q = queue.Queue()


def make_ui():
    root = tk.Tk()
    root.title("PDF -> Audiobook")

    frm = ttk.Frame(root, padding=12)
    frm.grid(sticky="nsew")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    lbl = ttk.Label(frm, text="Pronto para iniciar.")
    lbl.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

    pbar = ttk.Progressbar(frm, length=360, mode="determinate", maximum=100)
    pbar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))

    start_btn = ttk.Button(frm, text="Iniciar")
    start_btn.grid(row=2, column=0, sticky="w")

    stop_lbl = ttk.Label(frm, text="")
    stop_lbl.grid(row=2, column=1, sticky="e")

    # --- função que processa mensagens da fila e atualiza UI ---
    def poll_queue():
        try:
            while True:
                msg = q.get_nowait()
                kind = msg["kind"]
                if kind == "progress":
                    done = msg["done"]
                    total = msg["total"]
                    pct = int(done * 100 / total) if total else 0
                    lbl.config(text=f"Gerando bloco {done}/{total} …")
                    pbar["value"] = pct
                elif kind == "status":
                    lbl.config(text=msg["text"])
                elif kind == "done":
                    lbl.config(text=f"Concluído: {msg['path']}")
                    pbar["value"] = 100
                    start_btn.config(state="normal")
                    stop_lbl.config(text="✅")
        except queue.Empty:
            pass
        root.after(100, poll_queue)

    # --- callback de progresso chamado pela classe ---
    def on_progress(done: int, total: int, filename: str):
        q.put({"kind": "progress", "done": done, "total": total})

    # --- trabalho pesado num thread separado ---
    def worker():
        try:
            q.put({"kind": "status", "text": "A extrair texto do PDF…"})
            maker = PDF2Audiobook(
                pdf_path="Homo Deus_bg.pdf",  # <- ajusta aqui
                voice=PDF2Audiobook.VOICE_BG_F,
                output_dir="output",
                max_chars=4000,
                rate="-11%",
                on_progress=on_progress,
            )
            out = maker.run()
            q.put({"kind": "done", "path": out or "(sem ficheiro)"})
        except Exception as e:
            q.put({"kind": "status", "text": f"Erro: {e}"})
            start_btn.config(state="normal")

    def on_start():
        start_btn.config(state="disabled")
        stop_lbl.config(text="")
        pbar["value"] = 0
        lbl.config(text="A preparar…")
        threading.Thread(target=worker, daemon=True).start()

    start_btn.config(command=on_start)
    poll_queue()
    root.mainloop()


if __name__ == "__main__":
    make_ui()

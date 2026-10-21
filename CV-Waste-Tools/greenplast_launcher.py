# -*- coding: utf-8 -*-
"""Cross-platform GreenPlast launcher for dataset splitting and annotation audit."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from greenplast_environment import APP_DIR, EnvironmentManager, probe_env, MANAGED_NAME, MANAGED_DISPLAY_NAME

class Launcher:
    def __init__(self, prepared=None):
        self.root = tk.Tk()
        self.root.title("GreenPlast · Model Tools")
        self.root.geometry("790x545")
        self.root.minsize(680, 490)
        self.msgs = queue.Queue()
        self.conda = None
        self.env = None
        self.busy = False
        self.build_ui()
        self.root.after(100, self.process_messages)
        if prepared:
            conda, prefix, details = prepared
            self.process_ready(conda, prefix, details)
        else:
            self.refresh()

    def process_ready(self, conda, prefix, details):
        """Use a checked environment prepared by the Linux shell bootstrap."""
        self.conda = conda
        self.env = prefix
        self.busy = False
        self.retry.configure(state="normal")
        self.train_button.configure(state="normal")
        self.audit_button.configure(state="normal")
        self.progress.configure(mode="determinate", maximum=100, value=100)
        self.status.set("Ready — choose a tool")
        self.env_text.set(
            f"{MANAGED_DISPLAY_NAME if self.env.name.lower() == MANAGED_NAME else self.env.name} "
            f"({self.env})  |  PyTorch {details.get('torch', '?')}  |  "
            f"CUDA: {'available' if details.get('cuda') else 'not available'}"
            + (f"  |  {details['gpu']}" if details.get('gpu') else "")
        )
        self.append_log("Using verified Conda environment: " + str(self.env))

    def build_ui(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        outer = ttk.Frame(self.root, padding=22)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(6, weight=1)
        ttk.Label(outer, text="GreenPlast  /  Model Tools",
                  font=("Segoe UI", 20, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(outer, text="Train and split datasets, or inspect YOLO annotations.",
                  foreground="#555555").grid(row=1, column=0, sticky="w", pady=(4, 18))

        buttons = ttk.Frame(outer)
        buttons.grid(row=2, column=0, sticky="ew")
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        self.train_button = ttk.Button(buttons, text="Open  ·  Split & Train",
                                       command=lambda: self.launch("train"), state="disabled")
        self.train_button.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=16)
        self.audit_button = ttk.Button(buttons, text="Open  ·  Annotation Audit",
                                       command=lambda: self.launch("audit"), state="disabled")
        self.audit_button.grid(row=0, column=1, sticky="ew", padx=(8, 0), ipady=16)
        ttk.Label(buttons, text="Combine folders, make train/val/test lists, optionally train YOLO.",
                  wraplength=320, foreground="#555555").grid(row=1, column=0,
                                                           sticky="w", padx=(2, 14), pady=(8, 0))
        ttk.Label(buttons, text="Find class disagreements and suspicious boxes; export review CSV.",
                  wraplength=320, foreground="#555555").grid(row=1, column=1,
                                                           sticky="w", padx=(16, 0), pady=(8, 0))
        ttk.Separator(outer, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=20)
        info = ttk.Frame(outer)
        info.grid(row=4, column=0, sticky="ew")
        info.columnconfigure(0, weight=1)
        self.status = tk.StringVar(value="Looking for Conda environments ...")
        self.env_text = tk.StringVar(value="Environment: checking")
        ttk.Label(info, textvariable=self.status, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w")
        ttk.Label(info, textvariable=self.env_text, foreground="#555555",
                  wraplength=660).grid(row=1, column=0, sticky="w", pady=(6, 8))
        self.progress = ttk.Progressbar(info, mode="indeterminate")
        self.progress.grid(row=2, column=0, sticky="ew")
        ttk.Label(outer, text="Setup and activity log", font=("Segoe UI", 10, "bold")).grid(
            row=5, column=0, sticky="w", pady=(16, 5))
        logframe = ttk.Frame(outer)
        logframe.grid(row=6, column=0, sticky="nsew")
        logframe.rowconfigure(0, weight=1)
        logframe.columnconfigure(0, weight=1)
        self.log_widget = tk.Text(logframe, height=6, wrap="word", state="disabled",
                                  font=("Consolas", 9), background="#f5f6f8")
        self.log_widget.grid(row=0, column=0, sticky="nsew")
        scr = ttk.Scrollbar(logframe, command=self.log_widget.yview)
        scr.grid(row=0, column=1, sticky="ns")
        self.log_widget.configure(yscrollcommand=scr.set)
        footer = ttk.Frame(outer)
        footer.grid(row=7, column=0, sticky="ew", pady=(12, 0))
        self.retry = ttk.Button(footer, text="Recheck / repair environment",
                                command=self.refresh)
        self.retry.pack(side="left")
        ttk.Button(footer, text="Close", command=self.root.destroy).pack(side="right")

    def report(self, kind, value):
        self.msgs.put((kind, value))

    def refresh(self):
        if self.busy:
            return
        self.busy = True
        self.train_button.configure(state="disabled")
        self.audit_button.configure(state="disabled")
        self.retry.configure(state="disabled")
        self.status.set("Checking Conda environments ...")
        self.env_text.set("Environment: checking")
        self.progress.configure(mode="indeterminate", value=0)
        self.progress.start(16)

        def worker():
            try:
                settings = EnvironmentManager(self.report).setup()
                self.report("ready", settings)
            except Exception as exc:
                self.report("error", str(exc))

        threading.Thread(target=worker, daemon=True, name="CondaEnvironmentSetup").start()

    def append_log(self, line):
        self.log_widget.configure(state="normal")
        self.log_widget.insert("end", line + "\n")
        # Don't retain thousands of pip-installation lines in the widget.
        if int(self.log_widget.index("end-1c").split(".")[0]) > 250:
            self.log_widget.delete("1.0", "75.0")
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")

    def process_messages(self):
        try:
            while True:
                kind, value = self.msgs.get_nowait()
                if kind == "log":
                    self.append_log("• " + str(value))
                elif kind == "detail":
                    # Display recent pip/conda command output in a scrolling log.
                    self.append_log(str(value))
                elif kind == "status":
                    self.status.set(str(value))
                elif kind == "ready":
                    self.conda, self.env, details = value
                    self.busy = False
                    self.progress.stop()
                    self.progress.configure(mode="determinate", maximum=100, value=100)
                    self.retry.configure(state="normal")
                    self.train_button.configure(state="normal")
                    self.audit_button.configure(state="normal")
                    self.status.set("Ready — choose a tool")
                    self.env_text.set(f"{MANAGED_DISPLAY_NAME if self.env.name.lower() == MANAGED_NAME else self.env.name} "
            f"({self.env})  |  PyTorch {details.get('torch', '?')}  |  "
                                      f"CUDA: {'available' if details.get('cuda') else 'not available'}"
                                      + (f"  |  {details['gpu']}" if details.get('gpu') else ""))
                elif kind == "error":
                    self.busy = False
                    self.progress.stop()
                    self.progress.configure(mode="determinate", maximum=100, value=0)
                    self.retry.configure(state="normal")
                    self.status.set("Environment setup failed")
                    self.env_text.set("Check the log and select Recheck / repair after resolving the problem.")
                    self.append_log("ERROR: " + str(value))
                    messagebox.showerror("GreenPlast setup failed", str(value), parent=self.root)
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self.process_messages)

    def launch(self, name):
        if not self.conda or not self.env:
            messagebox.showerror("Environment not ready", "Please wait for environment setup.")
            return
        command = [self.conda, "run", "--no-capture-output", "-p", str(self.env),
                   "python", "-u", str(APP_DIR / "run_tool.py"), name]
        flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
        try:
            proc = subprocess.Popen(command, cwd=str(APP_DIR), creationflags=flags)
        except OSError as exc:
            messagebox.showerror("Launch failed", str(exc), parent=self.root)
            return
        log_location = ("a separate console" if os.name == "nt" else "the launching terminal")
        self.append_log(f"Started {name} (PID {proc.pid}). Output appears in {log_location}.")

    def run(self):
        self.root.mainloop()


def main(argv=None):
    parser = argparse.ArgumentParser(description="GreenPlast tool launcher")
    parser.add_argument("--env-prefix", default=None, help="Previously verified Conda env")
    parser.add_argument("--conda-exe", default=None, help="Conda executable path")
    args = parser.parse_args(argv)
    prepared = None
    if args.env_prefix or args.conda_exe:
        if not args.env_prefix or not args.conda_exe:
            parser.error("--env-prefix and --conda-exe must both be specified")
        env = Path(args.env_prefix).resolve()
        details = probe_env(args.conda_exe, env, needs_cuda=False)
        if not details.get("ok"):
            parser.error("Prepared environment is not usable: " + str(details.get("error", details)))
        prepared = (args.conda_exe, env, details)
    Launcher(prepared=prepared).run()


if __name__ == "__main__":
    main()

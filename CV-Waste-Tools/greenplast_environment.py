# -*- coding: utf-8 -*-
"""Conda environment detection, reuse and CUDA-aware setup for GreenPlast.

All functions here use Python's standard library. The Linux bootstrap calls
these functions *before* a GUI Python environment is available.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

APP_DIR = Path(__file__).resolve().parent
MANAGED_NAME = "cv-waste-tools"
MANAGED_DISPLAY_NAME = "CV Waste Tools"
MIN_PYTHON = (3, 10)
MAX_PYTHON = (3, 14)

# This tests real imports and detects CUDA availability. A successful pip
# installation alone does not establish that a Conda env is usable.
PROBE = r'''
import json, sys
out = {'python': list(sys.version_info[:3]), 'ok': False}
try:
    import tkinter
    import numpy
    import yaml
    import cv2
    import torch
    import torchvision
    import ultralytics
    from ultralytics.data.split import autosplit
    out.update(ok=True, torch=str(torch.__version__),
               ultralytics=str(ultralytics.__version__),
               cuda=bool(torch.cuda.is_available()),
               gpu=(torch.cuda.get_device_name(0) if torch.cuda.is_available() else ''))
    if out['cuda']:
        # Confirm that this wheel can actually run a kernel on the GPU,
        # not merely see a CUDA-capable driver or device.
        x = torch.ones(2, device='cuda')
        torch.cuda.synchronize()
        assert float(x.sum().item()) == 2.0, 'GPU compute probe failed' 
except Exception as exc:
    out['ok'] = False
    out['cuda'] = False
    out['error'] = type(exc).__name__ + ': ' + str(exc)
print('GREENPLAST_PROBE=' + json.dumps(out), flush=True)
'''


def find_conda() -> str:
    """Find a real Conda executable, including on Linux without shell init."""
    is_win = os.name == "nt"
    exe = "conda.exe" if is_win else "conda"
    candidates = [os.environ.get("CONDA_EXE"), shutil.which(exe)]
    if not is_win:
        # On Linux `conda` is often a shell function, so look for its binary.
        candidates.append(shutil.which("conda"))
    roots = [
        Path(sys.prefix), Path.home() / "miniconda3",
        Path.home() / "anaconda3", Path.home() / "miniforge3",
        Path.home() / "mambaforge", Path("/opt/conda"),
        Path("/opt/miniconda3"), Path("/opt/miniforge3"),
    ]
    if is_win:
        local = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
        roots.extend([local / "miniconda3", local / "anaconda3"])
    for root in roots:
        candidates.append(str(root / ("Scripts" if is_win else "bin") / exe))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise RuntimeError(
        "Conda was not found. Install Miniconda, Miniforge, or Anaconda "
        "and rerun START_GREENPLAST.bat (Windows) or START_GREENPLAST.sh (Linux)."
    )


def list_envs(conda: str) -> list[Path]:
    result = subprocess.run([conda, "env", "list", "--json"], capture_output=True,
                            text=True, errors="replace", timeout=90, check=False)
    if result.returncode:
        raise RuntimeError("Could not list Conda environments:\n" +
                           (result.stderr or result.stdout)[-1800:])
    data = json.loads(result.stdout)
    return [Path(p) for p in data.get("envs", [])]


def detect_nvidia() -> tuple[str, tuple[int, int] | None] | None:
    candidates = [shutil.which("nvidia-smi")]
    if os.name == "nt":
        candidates += [r"C:\Windows\System32\nvidia-smi.exe",
                       r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"]
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            result = subprocess.run([candidate], capture_output=True, text=True,
                                    errors="replace", timeout=12, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode != 0 or "NVIDIA-SMI" not in result.stdout:
            continue
        match = re.search(r"CUDA Version:\s*(\d+)\.(\d+)", result.stdout)
        cuda = (int(match[1]), int(match[2])) if match else None
        return ("NVIDIA GPU", cuda)
    return None


def torch_index(cuda: tuple[int, int] | None) -> str | None:
    """Pick a prebuilt CUDA PyTorch wheel compatible with the NVIDIA driver.

    Driver CUDA version (nvidia-smi) is a *maximum*, not a toolkit requirement.
    Pip wheels bring their own CUDA user-space runtime libraries.
    """
    if cuda is None:
        return None
    for required, wheel in (
        ((13, 2), "cu132"), ((13, 0), "cu130"),
        ((12, 8), "cu128"), ((12, 6), "cu126"),
        ((11, 8), "cu118"),
    ):
        if cuda >= required:
            return wheel
    return None


def probe_env(conda: str, prefix: Path, needs_cuda: bool) -> dict:
    try:
        result = subprocess.run(
            [conda, "run", "-p", str(prefix), "python", "-c", PROBE],
            capture_output=True, text=True, errors="replace", timeout=100,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}
    lines = [line.split("GREENPLAST_PROBE=", 1)[1].strip()
             for line in result.stdout.splitlines() if "GREENPLAST_PROBE=" in line]
    if not lines:
        return {"ok": False, "error": (result.stderr or result.stdout or
                                          "No Python response")[-400:]}
    try:
        data = json.loads(lines[-1])
    except json.JSONDecodeError:
        return {"ok": False, "error": "Could not decode environment check"}
    py = tuple(data.get("python", [])[:2])
    data["ok"] = bool(data.get("ok") and MIN_PYTHON <= py < MAX_PYTHON and
                      (data.get("cuda") or not needs_cuda))
    if needs_cuda and not data["ok"] and not data.get("cuda") and not data.get("error"):
        data["error"] = "PyTorch cannot access the NVIDIA GPU"
    return data


class EnvironmentManager:
    def __init__(self, report):
        self.report = report

    def run_checked(self, command: list[str], title: str):
        self.report("log", title)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, errors="replace", bufsize=1)
        tail = []
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                tail.append(line)
                if len(tail) > 30:
                    tail.pop(0)
                self.report("detail", line)
        result = proc.wait()
        if result:
            raise RuntimeError(f"{title} failed (exit code {result}).\n" +
                               "\n".join(tail[-12:]))

    def setup(self) -> tuple[str, Path, dict]:
        conda = find_conda()
        self.report("log", "Conda detected: " + conda)
        nvidia = detect_nvidia()
        gpu_wheel = torch_index(nvidia[1]) if nvidia else None
        needs_cuda = bool(nvidia and gpu_wheel)
        if nvidia:
            self.report("log", "NVIDIA GPU detected. Driver CUDA capability: " +
                        (".".join(map(str, nvidia[1])) if nvidia[1] else "unknown"))
            if not needs_cuda:
                self.report("log", "Driver CUDA version unsupported/unknown: GPU setup is unavailable; using CPU-compatible setup.")
        else:
            self.report("log", "No NVIDIA driver detected: CPU-compatible setup.")
        envs = list_envs(conda)
        preferred = sorted(envs, key=lambda p: (p.name.lower() != MANAGED_NAME,
                                               p.name.lower(), str(p)))
        self.report("log", f"Checking {len(preferred)} existing Conda environments ...")
        for prefix in preferred:
            self.report("status", "Checking " + prefix.name + " ...")
            check = probe_env(conda, prefix, needs_cuda)
            if check.get("ok"):
                self.report("log", f"Reusing environment: {prefix}")
                return conda, prefix, check
            # Avoid excessive logs when a machine has many other projects.
            if prefix.name.lower() == MANAGED_NAME:
                self.report("log", "Dedicated environment requires setup: " +
                            str(check.get("error", "missing dependencies")))
        # Never install into an unrelated existing environment.
        managed = next((env for env in envs if env.name.lower() == MANAGED_NAME), None)
        if managed is None:
            self.report("status", "Creating Conda environment (first run) ...")
            self.run_checked([conda, "create", "-y", "-n", MANAGED_NAME,
                              "python=3.11", "pip", "tk"],
                             f"Creating persistent Conda environment: {MANAGED_DISPLAY_NAME} ({MANAGED_NAME})")
            envs = list_envs(conda)
            managed = next((env for env in envs if env.name.lower() == MANAGED_NAME), None)
            if managed is None:
                raise RuntimeError("Conda reported successful creation, but the new environment "
                                   "cannot be located.")
        else:
            self.report("log", f"Repairing existing {MANAGED_DISPLAY_NAME} environment only.")
        base_cmd = [conda, "run", "--no-capture-output", "-p", str(managed),
                    "python", "-m", "pip"]
        self.report("status", "Installing PyTorch (first setup can be large) ...")
        index = (f"https://download.pytorch.org/whl/{gpu_wheel}" if needs_cuda else
                 "https://download.pytorch.org/whl/cpu")
        self.run_checked(base_cmd + ["install", "--upgrade", "torch", "torchvision",
                                     "--index-url", index],
                         f"Installing PyTorch ({gpu_wheel or 'CPU'})")
        self.report("status", "Installing Ultralytics and GUI dependencies ...")
        self.run_checked(base_cmd + ["install", "-r", str(APP_DIR / "requirements.txt")],
                         "Installing application dependencies")
        self.report("status", "Validating environment ...")
        check = probe_env(conda, managed, needs_cuda)
        if not check.get("ok"):
            raise RuntimeError("New environment failed its dependency/CUDA check: " +
                               str(check.get("error", check)))
        self.report("log", "Environment ready. Future launches will reuse it without reinstalling.")
        return conda, managed, check



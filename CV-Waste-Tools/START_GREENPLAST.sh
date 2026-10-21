#!/usr/bin/env bash
# GreenPlast Tools for Linux: run this from a terminal or desktop launcher.
set -Eeuo pipefail
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$APP_DIR"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "ERROR: START_GREENPLAST.sh currently targets Linux desktop systems." >&2
  exit 1
fi

CONDA_BIN=""
if [[ -n "${CONDA_EXE:-}" && -x "${CONDA_EXE}" ]]; then
  CONDA_BIN="${CONDA_EXE}"
elif command -v conda >/dev/null 2>&1; then
  # May be a shell function, but `type -P` returns the real executable.
  CONDA_BIN="$(type -P conda || true)"
fi
if [[ -z "$CONDA_BIN" ]]; then
  for root in "$HOME/miniforge3" "$HOME/miniconda3" "$HOME/anaconda3" \
              "$HOME/mambaforge" /opt/conda /opt/miniconda3 /opt/miniforge3; do
    if [[ -x "$root/bin/conda" ]]; then
      CONDA_BIN="$root/bin/conda"
      break
    fi
  done
fi
if [[ -z "$CONDA_BIN" ]]; then
  echo "ERROR: Conda not found. Install Miniforge, Miniconda, or Anaconda." >&2
  echo "Then reopen the shell, or set CONDA_EXE=/path/to/conda." >&2
  exit 1
fi

export CONDA_EXE="$CONDA_BIN"
echo "[GreenPlast] Conda: $CONDA_BIN"
echo "[GreenPlast] Detecting a suitable environment (CUDA PyTorch if available) ..."
# The bootstrap uses only Python's standard library, so the Conda base env
# does not need Tkinter, NumPy, Ultralytics or PyTorch installed.
"$CONDA_BIN" run --no-capture-output -n base python -u "$APP_DIR/greenplast_bootstrap.py"

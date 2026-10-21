GREENPLAST TOOLS - WINDOWS + LINUX
=================================

Two applications in one launcher:
  (1) Split & Train: make no-copy YOLO train/val/test manifests and train models.
  (2) Annotation Audit: check labeled images using a YOLO model and export a
      CSV for the CV Waste Web REVIEW task. It does not edit annotation files.

QUICK START - WINDOWS 10/11
---------------------------
1. Extract the entire archive (keep all files in the same folder).
2. Install Miniforge, Miniconda or Anaconda if Conda is not installed.
3. Double-click START_GREENPLAST.bat.
4. Wait for dependency checks / initial installation; choose a tool in the GUI.

QUICK START - LINUX (DESKTOP / X11 OR XWAYLAND)
----------------------------------------------
1. Extract the entire archive to a writable directory.
2. Install Miniforge, Miniconda or Anaconda if Conda is not installed.
3. In a terminal, change to the extracted directory and run:

      chmod +x START_GREENPLAST.sh
      ./START_GREENPLAST.sh

   Or: bash START_GREENPLAST.sh

4. After dependency checks, choose Split & Train or Annotation Audit.

The Linux shell script works even if the Conda base environment does not
have tkinter, torch, numpy, or ultralytics. The script locates Conda and
runs greenplast_bootstrap.py using Python from the Conda base environment;
the bootstrap then starts the GUI in the verified environment.

CONDA ENVIRONMENT NAME
----------------------
The new managed environment is named cv-waste-tools in Conda and
is displayed as "CV Waste Tools" in the application. Conda does not
permit spaces in environment names. Existing suitable environments,
including an older greenplast-tools installation, can still be reused.
The launcher does not rename or delete an existing environment.

GPU SUPPORT (WINDOWS AND LINUX)
-------------------------------
Ultralytics does not have a separate "GPU module". It uses PyTorch for GPU
training and inference. The launcher installs Ultralytics and, when possible,
a prebuilt CUDA-enabled torch + torchvision rather than CPU-only PyTorch.

- The launcher checks nvidia-smi to detect an NVIDIA driver and reported
  maximum CUDA capability. It selects a compatible PyTorch wheel index:
  CUDA 13.2 -> cu132; 13.0 -> cu130; 12.8 -> cu128; 12.6 -> cu126;
  11.8 -> cu118 (depending on driver capability).
- The PyTorch wheel includes CUDA runtime libraries. Normally you do NOT
  need to separately install the full CUDA Toolkit; you DO need a working
  NVIDIA GPU driver on the host. Conda does not install/update GPU drivers.
- The environment check imports Ultralytics, PyTorch, torchvision, NumPy,
  OpenCV, PyYAML, tkinter and checks torch.cuda.is_available(). If CUDA is
  accessible, it also performs an actual tensor computation on the GPU.
- If it finds an existing suitable Conda environment, it reuses that
  environment without changing it. Otherwise it creates or repairs a
  persistent environment named cv-waste-tools (display name: CV Waste Tools)
  and installs dependencies.
- The package does not automatically configure AMD ROCm GPU support.
- If the NVIDIA driver is incompatible or CUDA installation fails, the
  launcher reports an error or CPU-only environment; it does NOT silently
  claim GPU support.

TO TRAIN ON THE GPU
-------------------
Open "Split & Train", switch to "2. Model & training", and explicitly
select "GPU 0 (CUDA)" under Training device. "Auto" in this training GUI
currently defaults to CPU; installing CUDA PyTorch does not change that.
The launcher displays "CUDA: available" (and the GPU name) once the setup
has been verified. The first installation needs internet access and may
download multiple gigabytes.

WORKFLOW / FILES
----------------
- START_GREENPLAST.bat: Windows one-click start.
- START_GREENPLAST.sh: Linux shell start.
- greenplast_launcher.py: common GUI with buttons for both applications.
- greenplast_bootstrap.py: standard-library environment bootstrap for Linux,
  also used by Windows when Conda base lacks tkinter.
- greenplast_environment.py: shared Conda discovery, validation and installer.
- train_and_split_tool_GUI.py: no-copy dataset splitting and YOLO training.
- audit_dataset_review_gui.py: non-recursive annotation audit; reads YOLO
  detection BBOX labels with 5 fields or saved-confidence labels with 6
  fields. Unannotated/background images are skipped by default.
- run_tool.py: starts the selected tool in the chosen environment.
- requirements.txt: Ultralytics and other Python dependencies.

Original images and annotations are not moved or copied by splitting;
annotation audit never writes to YOLO label files. Train and audit outputs
are written to paths selected inside the respective tools.

TROUBLESHOOTING
---------------
- Conda not found on Linux: set CONDA_EXE=/absolute/path/to/bin/conda
  before launching, or install Conda in a standard location.
- No GUI on Linux: start from an X11/XWayland graphical desktop, with DISPLAY
  and appropriate display permissions configured. Headless servers need a
  desktop, remote X forwarding or an appropriate virtual display.
- GPU absent: check "nvidia-smi" on the host. If it fails, repair/install
  the NVIDIA driver, not just the CUDA Python packages.
- Training runs on CPU: select "GPU 0 (CUDA)" in the training GUI; check
  that launcher status reports "CUDA: available" first.
- Environment repair: use the launcher "Recheck / repair environment" button.
- Background images: intentionally missing .txt files are skipped during
  annotation audit, but the selected label directory must still be correct.

This package was syntax-tested, shell-checked and tested with simulated Conda
and CUDA environments. No actual download/installation or NVIDIA GPU test
was run on your hardware. GPU compatibility ultimately depends on the host
GPU, driver, platform and available PyTorch wheels.

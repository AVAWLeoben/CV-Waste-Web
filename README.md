# AVAW CVAT BBOX – Browser YOLO Annotation Tool with LiteRT

A standalone browser-based bounding-box annotation tool for YOLO datasets.

The application is implemented as a single HTML file and supports:

- loading image datasets directly in the browser,
- reading and writing YOLO bounding-box annotation files,
- creating, moving, resizing, copying, pasting, and deleting boxes,
- editing class names and display colors,
- navigating through datasets,
- optional autosave on navigation,
- running Ultralytics YOLO models directly in the browser,
- loading `.tflite` / LiteRT models,
- WebGPU acceleration with CPU/WASM fallback,
- using YOLO predictions as annotations,
- exporting annotated images,
- and working without a Python inference server.

The browser application itself does **not** require Python after the model has been exported.

---

## Repository contents

Typical repository layout:

```text
.
├── AVAW_CVAT_BBOX_LiteRT.html
├── export_to_liteRT.py
├── README.md
└── models/
    └── example_model.tflite
```

The HTML application can also be distributed as a single file.

---

# 1. Application overview

`AVAW_CVAT_BBOX_LiteRT.html` is a browser-based annotation interface inspired by a desktop YOLO/CVAT-style workflow.

It combines two functions:

1. **Manual bounding-box annotation**
2. **YOLO-assisted annotation using LiteRT models**

All image editing and inference are performed locally in the browser.

No images are uploaded to a server by the application.

---

# 2. Supported annotation format

Annotations use the standard YOLO text format.

For every image:

```text
image001.jpg
```

the corresponding annotation file is:

```text
image001.txt
```

Each line contains:

```text
class_id x_center y_center width height
```

with normalized coordinates between `0` and `1`.

Example:

```text
0 0.512500 0.462500 0.175000 0.225000
2 0.231250 0.610000 0.087500 0.140000
```

Internally, the browser converts these normalized values to pixel coordinates for editing and converts them back to YOLO format when saving.

---

# 3. Starting the application

## Option A – Open the HTML file directly

In many modern browsers, simply double-click:

```text
AVAW_CVAT_BBOX_LiteRT.html
```

The page will open through a `file://` URL.

This is convenient for annotation and may also work for model inference depending on browser security settings.

## Option B – Run through localhost

If browser modules, LiteRT, WebGPU, WASM, or security restrictions cause problems, serve the folder locally.

From a terminal:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/AVAW_CVAT_BBOX_LiteRT.html
```

`localhost` is generally the more reliable option for WebGPU/WASM execution.

---

# 4. Browser recommendation

A recent Chromium-based browser is recommended, for example:

- Google Chrome
- Microsoft Edge

The application can use WebGPU, WebAssembly, and the File System Access API. Browser support for direct folder writing varies.

---

# 5. Loading a dataset

The top toolbar provides two different workflows.

## Open Working Folder

**Open Working Folder** is the simplest workflow.

It:

1. opens one directory,
2. loads supported images from that directory,
3. loads matching YOLO `.txt` annotation files,
4. uses the same directory as the annotation output directory.

Example:

```text
dataset/
├── image001.jpg
├── image001.txt
├── image002.jpg
├── image002.txt
├── image003.jpg
└── image003.txt
```

When annotations are saved, the matching `.txt` files are written back into that same folder.

## Import Images / Annotations

**Import Images / Annotations** loads images and annotation files without automatically defining where future annotation files should be written.

Use this when:

- the source data should remain untouched,
- images are being loaded from another location,
- annotations should be stored in a separate folder.

After importing, use **Choose Annotation Save Folder** to select the output directory.

The selected folder is reused for all subsequent manual saves and autosaves during the current browser session.

---

# 6. Annotation output folder

The toolbar displays the current annotation output location.

Example:

```text
Annotation output: labels
```

When using **Open Working Folder**, that directory automatically becomes the annotation output folder.

When using **Import Images / Annotations**, select an output directory once using:

```text
Choose Annotation Save Folder
```

The browser normally asks for folder authorization once per page session.

After that, annotation saves can be performed without repeatedly selecting a directory.

Browser security may require folder authorization again after closing or reloading the page.

---

# 7. Creating and editing bounding boxes

The application supports standard bounding-box editing operations.

## Create a box

Activate the add-box tool and draw a rectangle on the image.

The new box is assigned the currently selected class.

## Select a box

Click inside a bounding box.

The selected box becomes available for:

- moving,
- resizing,
- deleting,
- copying,
- class reassignment.

## Move a box

Drag the selected box.

## Resize a box

Drag one of its resize handles.

## Multi-selection

Multiple boxes can be selected for group operations.

The application also supports selection by dragging a selection region.

## Delete boxes

Select one or more boxes and use:

```text
Delete
```

or:

```text
Backspace
```

The Delete shortcut works even if a button, range slider, checkbox, file selector, or dropdown currently has focus.

Text-entry fields are protected so normal text editing still works.

## Delete all boxes

Use the **Delete All** control to remove all annotations from the current image.

## Remove duplicate boxes

The duplicate-removal function can be used to clean repeated annotations.

---

# 8. Copy and paste

Selected annotations can be copied and pasted.

Typical shortcuts:

```text
Ctrl+C
Ctrl+V
```

This is useful when consecutive images contain objects at similar locations.

---

# 9. Undo

The application maintains a short undo history for annotation operations.

Use the **Undo** button or the corresponding keyboard shortcut where available.

---

# 10. Classes and colors

The class configuration dialog allows class names to be edited.

Example:

```text
PET
PE
PP
PS
PVC
```

Each class is assigned a display color for visualization.

When a compatible Ultralytics model is loaded, class names embedded in the model metadata can also be imported automatically.

---

# 11. Image navigation

The application includes:

- previous image,
- next image,
- image list,
- image counter,
- dataset progress indicator,
- direct image selection.

The current image's annotations are kept separately from those of other images.

---

# 12. Autosave on navigation

The option:

```text
Auto save on navigation
```

controls what happens when leaving an edited image.

## Autosave enabled

When enabled:

1. the current annotation is written to the selected annotation output folder,
2. navigation continues only after the save succeeds.

This prevents navigation from silently discarding changes.

## Autosave disabled

When disabled:

- unsaved annotation edits are discarded when leaving the image,
- the image returns to its last loaded or manually saved annotation state.

This prevents in-memory edits from appearing to have been saved when they were not written to disk.

---

# 13. Manual annotation save

Use:

```text
Save Annotation
```

to write the current YOLO `.txt` annotation file.

Example:

```text
frame_0042.jpg
```

produces:

```text
frame_0042.txt
```

The save location is the currently selected annotation output directory.

---

# 14. Image transformations

The application contains basic augmentation/editing operations such as:

- horizontal flip,
- vertical flip.

The bounding boxes are transformed together with the image.

These operations can be useful for teaching data augmentation concepts.

---

# 15. Exporting annotated images

The application can export an image with the current bounding boxes drawn on top.

This is useful for documentation, teaching material, dataset review, and debugging annotation quality.

A viewport/screenshot-style export is also available.

---

# 16. YOLO inference in the browser

The application supports direct YOLO inference using Ultralytics LiteRT `.tflite` models.

The inference pipeline is:

```text
.tflite model
      ↓
@ultralytics/yolo
      ↓
LiteRT.js
      ↓
WebGPU
      ↓
CPU/WASM fallback when required
      ↓
YOLO detections
      ↓
browser annotations
```

No Python backend is required while using the HTML application.

---

# 17. Loading a model

Use the model file selector and choose one:

```text
*.tflite
```

Only one model is active at a time.

The application shows explicit model states:

```text
SELECTED
LOADING
READY
LOAD FAILED
```

If model loading fails, the error is displayed in the application.

A **Load / retry model** button is available to retry loading the same file.

---

# 18. Model metadata

Ultralytics LiteRT exports contain model metadata.

The browser can read information such as:

- task,
- class names,
- image size,
- stride.

The application therefore does not need a separate runtime image-size selector.

The exported model itself defines its fixed input size.

For example:

```text
yolo11n_160.tflite
```

may have been exported with:

```python
imgsz=160
```

while another model may use:

```python
imgsz=640
```

The HTML application loads the model as exported.

---

# 19. Running YOLO inference

After the model status shows:

```text
READY
```

load an image and press:

```text
Run YOLO inference
```

The model predictions are converted into editable bounding-box annotations.

The application also displays inference information such as:

- backend,
- preprocessing time,
- inference time,
- postprocessing time.

---

# 20. Confidence and IoU

The model panel provides controls for:

- confidence threshold,
- IoU threshold.

These are passed to browser inference.

Increasing the confidence threshold reduces low-confidence detections.

The IoU value influences postprocessing/NMS behavior.

---

# 21. Single-click prediction

The application also supports object prediction at a selected image position.

This mode runs detection and chooses the highest-confidence detected object containing the clicked point.

It can be useful when manually annotating an image and only one particular object should be added.

---

# 22. WebGPU and fallback execution

The application prefers browser acceleration when available.

Typical execution is:

```text
WebGPU
```

If the selected LiteRT graph contains unsupported WebGPU operations, the runtime can fall back to CPU/WASM.

The application displays the backend actually selected by the model runtime.

A WebGPU-capable browser is recommended but not strictly required for every model.

---

# 23. Internet requirement

The current HTML version loads its browser inference libraries from a CDN.

The import map includes packages such as:

```text
@ultralytics/yolo
@litertjs/core
@litertjs/wasm-utils
```

Therefore an internet connection is required when those dependencies are first loaded.

A fully offline version could instead self-host the JavaScript and LiteRT WASM dependencies.

---

# 24. Exporting YOLO models to LiteRT

Ultralytics exports LiteRT models using:

```python
format="litert"
```

The resulting file uses the `.tflite` extension.

Example:

```python
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

model.export(
    format="litert",
    imgsz=640,
    nms=None,
)
```

This creates a LiteRT/TFLite model suitable for use in the browser application.

---

# 25. Why `nms=None`?

For current Ultralytics browser LiteRT deployment, `nms=None` keeps the one-to-many detection path where appropriate and lets the browser package perform postprocessing.

This avoids certain WebGPU-incompatible NMS-free graph operations on some YOLO exports.

Example:

```python
model.export(
    format="litert",
    imgsz=640,
    nms=None,
)
```

---

# 26. Fixed inference resolution

The application intentionally does **not** dynamically change the model input resolution.

Instead, choose the desired size during export.

Examples:

```python
imgsz=160
```

```python
imgsz=320
```

```python
imgsz=640
```

Each exported model has its own fixed input size.

Example:

```python
from ultralytics import YOLO

YOLO("yolo11n.pt").export(
    format="litert",
    imgsz=160,
    nms=None,
)
```

The browser reads the model metadata and runs the model at its exported size.

---

# 27. Example export script

A simple `export_to_liteRT.py` can contain:

```python
from ultralytics import YOLO

MODEL = "yolo11n.pt"
IMGSZ = 640

model = YOLO(MODEL)

model.export(
    format="litert",
    imgsz=IMGSZ,
    nms=None,
)
```

For a custom trained model:

```python
from ultralytics import YOLO

model = YOLO("best.pt")

model.export(
    format="litert",
    imgsz=640,
    nms=None,
)
```

---

# 28. Exporting several models

Example:

```python
from ultralytics import YOLO

MODELS = [
    "yolov8n.pt",
    "yolo11n.pt",
    "yolo26n.pt",
]

IMGSZ = 640

for model_path in MODELS:
    model = YOLO(model_path)

    model.export(
        format="litert",
        imgsz=IMGSZ,
        nms=None,
    )
```

---

# 29. LiteRT export on Windows

Ultralytics currently documents LiteRT export support for:

- Linux x86_64
- macOS

For Windows systems, a practical solution is:

```text
Windows
   ↓
WSL2
   ↓
Ubuntu
   ↓
Ultralytics Python environment
   ↓
LiteRT export
```

The resulting `.tflite` file can then be used normally from Windows and loaded into the browser application.

---

# 30. Installing WSL2 Ubuntu

Open PowerShell as Administrator and install WSL if necessary:

```powershell
wsl --install
```

Restart Windows if requested.

Ubuntu can then be launched from the Start menu or with:

```powershell
wsl
```

---

# 31. Windows paths inside WSL

Windows drives are mounted below:

```text
/mnt
```

Examples:

Windows:

```text
C:\Users\User\Documents\WSL
```

WSL:

```text
/mnt/c/Users/User/Documents/WSL
```

Windows:

```text
D:\YOLO
```

WSL:

```text
/mnt/d/YOLO
```

To see mounted drives:

```bash
ls /mnt
```

To check the current directory:

```bash
pwd
```

---

# 32. Recommended export folder

For example, create a folder in Windows:

```text
C:\Users\User\Documents\WSL
```

Place inside it:

```text
export_to_liteRT.py
yolo11n.pt
```

Then, from Ubuntu/WSL:

```bash
cd /mnt/c/Users/User/Documents/WSL
```

Check the files:

```bash
ls
```

---

# 33. Create the Python environment in WSL

Install Python virtual-environment support if necessary:

```bash
sudo apt update
sudo apt install python3-venv
```

Create a virtual environment:

```bash
python3 -m venv ~/yolo_export
```

Activate it:

```bash
source ~/yolo_export/bin/activate
```

The shell prompt should now begin with something similar to:

```text
(yolo_export)
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install Ultralytics:

```bash
pip install -U ultralytics
```

---

# 34. Run the exporter

Navigate to the Windows folder from WSL:

```bash
cd /mnt/c/Users/User/Documents/WSL
```

Activate the environment if it is not already active:

```bash
source ~/yolo_export/bin/activate
```

Run:

```bash
python export_to_liteRT.py
```

The exported `.tflite` file will appear in a Windows-accessible location.

It can then be selected directly from the HTML application.

---

# 35. Reusing the WSL environment

The environment only needs to be created once.

For later export sessions:

```bash
source ~/yolo_export/bin/activate
cd /mnt/c/Users/User/Documents/WSL
python export_to_liteRT.py
```

---

# 36. CUDA is not required for export

A CUDA-enabled WSL installation is not required merely to convert a YOLO `.pt` model to LiteRT.

The export can be performed using the CPU.

A GPU may improve other training/inference workflows, but it is not necessary for this conversion step.

---

# 37. Typical complete workflow

A practical workflow is:

```text
1. Train or obtain a YOLO .pt model
                ↓
2. Start Ubuntu through WSL2
                ↓
3. Activate the yolo_export Python environment
                ↓
4. Export .pt → LiteRT .tflite
                ↓
5. Open AVAW_CVAT_BBOX_LiteRT.html
                ↓
6. Open a working image folder
                ↓
7. Load the .tflite model
                ↓
8. Run YOLO inference
                ↓
9. Correct/add/delete bounding boxes manually
                ↓
10. Save YOLO .txt annotations
```

---

# 38. Suggested dataset structure

A simple dataset layout is:

```text
dataset/
├── images/
│   ├── image001.jpg
│   ├── image002.jpg
│   └── image003.jpg
└── labels/
    ├── image001.txt
    ├── image002.txt
    └── image003.txt
```

If images and labels are stored separately, use:

```text
Import Images / Annotations
```

followed by:

```text
Choose Annotation Save Folder
```

If images and labels share one directory, use:

```text
Open Working Folder
```

---

# 39. Troubleshooting

## Model file can be selected, but status never becomes READY

The application should progress through:

```text
SELECTED
LOADING
READY
```

or display:

```text
LOAD FAILED
```

If loading fails:

- verify that the file is a valid Ultralytics LiteRT `.tflite`,
- use a recent Ultralytics version for export,
- try running the page through `localhost`,
- check the browser developer console,
- try Chrome or Edge,
- verify internet access for the CDN dependencies.

## WebGPU is unavailable

Inference may still run through a CPU/WASM fallback.

For WebGPU:

- use a current Chrome or Edge release,
- update GPU drivers,
- prefer `https://` or `http://localhost`,
- verify WebGPU is enabled in the browser.

## Inference is slow

Possible causes:

- CPU/WASM fallback,
- large input resolution,
- large YOLO model,
- unsupported WebGPU operations in the graph,
- first-run runtime/WASM initialization.

For teaching exercises, small models and small fixed resolutions such as `160` or `320` can significantly reduce inference time.

## Save folder is requested repeatedly

Use:

```text
Open Working Folder
```

when annotations should be saved alongside the dataset.

Alternatively:

1. use **Import Images / Annotations**,
2. click **Choose Annotation Save Folder** once.

The chosen output folder is reused for the rest of that page session.

A browser may require authorization again after the page is closed or reloaded.

## Autosave behavior

With autosave disabled, unsaved edits are discarded when leaving the image.

With autosave enabled, the `.txt` file is written before navigation.

## Delete key does nothing

First select a bounding box.

Both:

```text
Delete
```

and:

```text
Backspace
```

remove the selected annotation.

## USB drive not visible in WSL

Windows fixed drives are normally available below `/mnt`, but removable drives may not be mounted automatically.

It is usually simpler to perform the LiteRT export from a normal Windows folder such as:

```text
C:\Users\User\Documents\WSL
```

and copy the resulting `.tflite` file to the USB drive afterward.

---

# 40. Technology used

The application uses:

- HTML
- CSS
- JavaScript ES modules
- Canvas 2D
- File System Access API
- WebAssembly
- WebGPU
- LiteRT.js
- `@ultralytics/yolo`

Model conversion uses:

- Python
- Ultralytics
- WSL2/Ubuntu on Windows when required

---

# 41. Relevant upstream projects

Ultralytics:

https://github.com/ultralytics/ultralytics

Ultralytics browser inference:

https://github.com/ultralytics/inference

Ultralytics browser package documentation:

https://github.com/ultralytics/inference/blob/main/web/README.md

LiteRT:

https://developers.google.com/edge/litert

---

# 42. Notes on LiteRT compatibility

For browser use, export the model with a recent version of Ultralytics.

Current Ultralytics browser inference supports `.tflite` LiteRT models directly and obtains the model metadata from the exported file.

The browser package automatically selects the LiteRT.js backend for `.tflite` files.

The exact backend used for inference depends on browser capabilities and model operations.

---

# 43. Privacy

Image data and annotations remain on the user's computer.

Inference runs locally in the browser.

The current HTML contacts external CDNs to download the JavaScript/WASM inference runtime unless those dependencies are self-hosted.

The images themselves are not intentionally uploaded by this application.

---

# 44. Intended use

This project is primarily intended for:

- education,
- YOLO exercises,
- computer-vision demonstrations,
- dataset annotation,
- browser inference experiments,
- comparing manual and model-assisted annotation workflows.

It is designed to make the complete process visible:

```text
image
→ annotation
→ YOLO model
→ LiteRT export
→ browser inference
→ annotation correction
```

---

# License

Add the license appropriate for your repository, for example `MIT`, if desired.

---

# Acknowledgements

This project uses the Ultralytics YOLO ecosystem and Google's LiteRT browser runtime.

Ultralytics YOLO licensing and dependencies remain subject to their respective upstream licenses.

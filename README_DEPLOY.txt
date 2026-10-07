AVAW Annotator combined Detection + Segmentation build

For GitHub Pages:
1. Put index.html and .nojekyll in the repository root.
2. Repository -> Settings -> Pages.
3. Deploy from branch: main, folder: /(root).

Detection/BBOX remains the master implementation for:
image loading, canvas display, zoom/pan, navigation, save/autosave,
class handling, selection, model loading, and LiteRT runtime.

Segmentation adds YOLO polygon I/O, manual polygon editing, vertex editing,
simplification, merging, contained-polygon cleanup, and LiteRT segmentation.

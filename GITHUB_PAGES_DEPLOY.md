# GitHub Pages deployment

This repository can be hosted directly with GitHub Pages because the annotation application is a static web app.

## Files to place in the repository root

```text
index.html
.nojekyll
README.md
```

`index.html` is the browser annotation application.

## Enable GitHub Pages

1. Open the repository on GitHub.
2. Open **Settings**.
3. Select **Pages** in the left sidebar.
4. Under **Build and deployment**, choose:
   - **Source:** Deploy from a branch
   - **Branch:** `main`
   - **Folder:** `/ (root)`
5. Click **Save**.
6. Wait for the Pages deployment to finish.

GitHub will show the public URL on the Pages settings screen. It normally has the form:

```text
https://USERNAME.github.io/REPOSITORY/
```

Open that URL and the annotation app should start as `index.html`.

## What remains local

Hosting the site does not automatically upload user datasets.

The application still works with:

- local image folders,
- local YOLO `.txt` annotations,
- locally selected `.tflite` models,
- browser-side LiteRT/WebGPU inference.

Users must explicitly grant folder/file access through the browser.

## Browser recommendation

Use a recent version of Chrome or Edge.

GitHub Pages uses HTTPS, which is preferable for WebGPU and browser file-system APIs.

## Current external dependencies

The current `index.html` imports these packages from `esm.sh`:

- `@ultralytics/yolo`
- `@litertjs/core`
- `@litertjs/wasm-utils`

Therefore the hosted app still requires internet access to load the inference runtime.

A later version can self-host these dependencies if fully controlled/offline deployment is required.

## Custom domain later

After the GitHub Pages version works, a custom domain can be configured in:

**Repository → Settings → Pages → Custom domain**

For example:

```text
annotation.example.com
```

Configure the DNS records requested by GitHub before enabling the custom domain.

## Updating the site

Commit and push a new `index.html` to `main`.

GitHub Pages redeploys automatically.

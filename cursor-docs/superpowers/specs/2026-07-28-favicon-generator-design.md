# Favicon Generator — Design

**Date:** 2026-07-28  
**Status:** Approved for planning  
**Scope:** Modernize the existing Pillow CLI into a complete modern favicon set, with SVG input support, packaging, and docs/UX polish. Tests are out of scope for this pass.

## Goal

Turn `favicon_generator.py` into a simple, installable Python tool that generates **all currently useful favicon / app-icon assets at the correct sizes**, drops obsolete formats, supports SVG and raster sources, and ships clear docs and packaging.

## Non-goals

- Unit/integration test suite (deferred)
- Legacy Apple size matrix or Windows `mstile` / `msapplication-*` output
- A `--legacy` preset
- GUI or web UI

## Output set

| File | Spec |
|------|------|
| `favicon.svg` | Copied when source is SVG; omitted for raster-only sources |
| `favicon.ico` | Multi-size ICO: 16×16, 32×32, 48×48 |
| `favicon-16x16.png` | Browser tab |
| `favicon-32x32.png` | Retina tab |
| `apple-touch-icon.png` | 180×180 |
| `icon-192.png` | PWA / Android |
| `icon-512.png` | PWA |
| `icon-maskable-512.png` | 512×512 with extra safe-zone padding |
| `site.webmanifest` | References 192, 512 (any), and maskable 512 |
| HTML snippet | Modern `<link>` / `<meta>` only (default filename `favicon-links.html`) |

### Removed (relative to current code)

- Legacy Apple sizes: 57, 60, 72, 76, 114, 120, 144, 152
- `apple-touch-icon-precomposed` markup
- `favicon-96x96.png`, `favicon-128.png`, `favicon-196x196.png`
- All `mstile-*` files and `msapplication-*` meta tags
- ICO sizes 24×24 and 64×64

## Architecture

Single-module CLI remains the implementation unit:

- `favicon_generator.py` — argument parsing, load, render, write
- `pyproject.toml` — project metadata + console script entry point (e.g. `favicon-generator`)
- `requirements.txt` — aligned with project deps for simple `pip install -r`
- `.gitignore` — `favicons/`, `__pycache__/`, venvs, build artefacts
- `README.md` — install, usage, output list, SVG notes

### Pipeline

1. Parse and validate CLI args  
2. Load source: SVG via cairosvg → high-res RGBA; else Pillow (`exif_transpose`, RGBA)  
3. Render each PNG `IconSpec` via shared `render_icon()`  
4. Optionally write `favicon.ico`  
5. If source was SVG, copy to `favicon.svg`  
6. Optionally write `site.webmanifest` and HTML snippet  
7. Print a clear summary of generated paths  

### Render behaviour

- Fit modes unchanged: `contain` (default), `cover`, `stretch`
- Shared padding (`--padding`, 0.0–0.45) for normal icons
- Maskable 512: same fit, with additional inner padding (~20% total safe zone) so Android masks do not clip the logo
- Apple touch: docs recommend a non-transparent `--background`; transparent background still emits RGBA (iOS may composite on white)

### Error handling

- Exit `1` on user/input errors; messages on stderr
- Refuse to overwrite existing outputs unless `--overwrite`
- Explicit errors for missing source, invalid colours, SVG render failure, missing cairosvg when `.svg` is supplied

## CLI

### Kept

- `source` (positional)
- `-o` / `--output-dir` (default `./favicons`)
- `--fit` (`contain` | `cover` | `stretch`)
- `--background` (`transparent`, CSS name, or hex)
- `--padding`
- `--prefix` (URL prefix in HTML/manifest paths)
- `--html-file`
- `--no-html`
- `--no-ico`
- `--overwrite`

### Changed / added

| Flag | Role |
|------|------|
| `--theme-colour` | Manifest `theme_color` + HTML `theme-color` (default `#FFFFFF`). Replaces `--tile-colour`. |
| `--background-colour` | Manifest `background_color` (default: same value as `--theme-colour`) |
| `--name` | Manifest / app `name` (default: derived from source stem or `"App"`) |
| `--short-name` | Manifest `short_name` (default: same as `--name`) |
| `--no-manifest` | Skip `site.webmanifest` |

### Removed

- `--tile-colour`
- `--application-name` (replaced by `--name` / `--short-name`)

## HTML and manifest

### HTML (when not `--no-html`)

Emit, in order:

1. `<link rel="icon" href="…/favicon.svg" type="image/svg+xml">` — only if SVG was produced  
2. `<link rel="icon" href="…/favicon.ico" sizes="48x48">` — omitted if `--no-ico`  
3. `<link rel="icon" type="image/png" sizes="32x32" href="…/favicon-32x32.png">`  
4. `<link rel="icon" type="image/png" sizes="16x16" href="…/favicon-16x16.png">`  
5. `<link rel="apple-touch-icon" sizes="180x180" href="…/apple-touch-icon.png">`  
6. `<link rel="manifest" href="…/site.webmanifest">` — omitted if `--no-manifest`  
7. `<meta name="theme-color" content="{theme-colour}">`  

All `href`s honour `--prefix`.

### Manifest (when not `--no-manifest`)

```json
{
  "name": "<name>",
  "short_name": "<short-name>",
  "theme_color": "<theme-colour>",
  "background_color": "<background-colour>",
  "icons": [
    { "src": "<prefix>icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "<prefix>icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "<prefix>icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

## SVG support

- Dependency: `cairosvg` (in addition to `Pillow`)
- Raster path unchanged (PNG/JPEG/WebP/etc. via Pillow)
- SVG path: render to a large RGBA bitmap (e.g. 1024×1024 viewport) for downstream icon rendering; also copy the original file to `favicon.svg`
- Docs state SVG and common raster formats are supported for input
- `cairosvg` is a **required** package dependency so install always supports SVG; if SVG rendering fails, surface the underlying error clearly

## Packaging and docs

- `pyproject.toml` with console script `favicon-generator = …:main` (or equivalent)
- Dependencies: `Pillow` (existing range), `cairosvg`
- README covers: install, basic and advanced examples, full output table, SVG notes, Apple background recommendation
- CLI success output lists each generated filename

## Compatibility notes

- Existing callers using legacy filenames or `--tile-colour` / `--application-name` will break; this is intentional (playground tool, no released API guarantee)
- Document the new flag names in the README migration-style “what changed” blurb briefly

## Success criteria

1. Running the tool on a square PNG or SVG produces the Section “Output set” files (SVG copy only for SVG sources)  
2. HTML and manifest reference only modern assets and correct sizes  
3. Obsolete Apple/Windows assets are gone from code and docs  
4. Installable via project packaging; `favicon-generator --help` works after install  
5. README accurately describes inputs, outputs, and flags  

# Favicon Generator

Generate a modern favicon set from one source image (PNG, JPEG, WebP, or SVG):

- `favicon-16x16.png`, `favicon-32x32.png`
- `favicon.ico` (16, 32, 48)
- `apple-touch-icon.png` (180×180)
- `icon-192.png`, `icon-512.png`, `icon-maskable-512.png`
- `site.webmanifest`
- `favicon-links.html` (optional HTML snippet)
- `favicon.svg` when the source is SVG

## Install

```bash
python -m pip install -e .
# or
python -m pip install -r requirements.txt
```

## Use

```bash
favicon-generator logo.png
# or
python favicon_generator.py logo.png
```

Default output directory: `./favicons`.

```bash
favicon-generator logo.svg \
  --output-dir site/assets/favicons \
  --prefix /assets/favicons/ \
  --name "My App" \
  --short-name "App" \
  --theme-colour "#0A0A0A" \
  --background-colour "#0A0A0A" \
  --background "#0A0A0A" \
  --padding 0.05
```

For Apple touch icons, prefer a non-transparent `--background` so iOS does not composite onto an unexpected fill.

### Useful flags

| Flag | Purpose |
|------|---------|
| `--fit contain\|cover\|stretch` | How the source fills each canvas |
| `--no-ico` / `--no-html` / `--no-manifest` | Skip optional outputs |
| `--overwrite` | Replace existing files |

### What changed from the earlier playground script

- Dropped legacy multi-size Apple icons and Windows `mstile` assets
- Replaced `--tile-colour` / `--application-name` with `--theme-colour`, `--background-colour`, `--name`, `--short-name`
- Added SVG input (cairosvg) and PWA manifest + maskable icon

Use `--help` for the full option list.

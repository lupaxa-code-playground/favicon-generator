# Reference

Run `favicon-generator --help` for the authoritative list from your installed
version.

## CLI options

| Option | Default | Description |
|--------|---------|-------------|
| `source` | *(required)* | Source image: PNG, JPEG, WebP, or SVG |
| `-o` / `--output-dir` | `favicons` | Output directory |
| `--fit` | `contain` | `contain`, `cover`, or `stretch` |
| `--background` | `transparent` | Canvas background |
| `--padding` | `0` | Fractional padding `0.0`–`0.45` |
| `--theme-colour` | `#FFFFFF` | `theme-color` / manifest `theme_color` |
| `--background-colour` | same as `--theme-colour` | Manifest `background_color` |
| `--name` | source stem or `App` | Manifest name |
| `--short-name` | same as `--name` | Manifest `short_name` |
| `--prefix` | *(empty)* | URL prefix for HTML and manifest |
| `--html-file` | `favicon-links.html` | HTML snippet filename |
| `--no-manifest` | off | Skip `site.webmanifest` |
| `--no-html` | off | Skip HTML snippet |
| `--no-ico` | off | Skip `favicon.ico` |
| `--overwrite` | off | Replace existing files |

## Generated files

| File | Notes |
|------|--------|
| `favicon-16x16.png` | 16×16 |
| `favicon-32x32.png` | 32×32 |
| `favicon.ico` | 16, 32, 48 (unless `--no-ico`) |
| `apple-touch-icon.png` | 180×180 |
| `icon-192.png` | PWA |
| `icon-512.png` | PWA |
| `icon-maskable-512.png` | Maskable PWA |
| `site.webmanifest` | Unless `--no-manifest` |
| `favicon-links.html` | Unless `--no-html` (name overridable) |
| `favicon.svg` | Only when source is SVG |

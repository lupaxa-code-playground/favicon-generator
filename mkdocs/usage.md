# Usage

## Basic generation

```bash
favicon-generator logo.png
```

Default output directory: `./favicons`.

## SVG sources

SVG input is rasterised with cairosvg and also copied to `favicon.svg` in the
output directory.

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

## Fit, background, and padding

| Flag | Notes |
|------|--------|
| `--fit contain\|cover\|stretch` | How the source fills each canvas (`contain` default) |
| `--background` | Canvas fill: `transparent`, CSS name, or hex |
| `--padding` | Fractional padding `0.0`–`0.45` |

For Apple touch icons, prefer a non-transparent `--background` so iOS does not
composite onto an unexpected fill.

Maskable icons use an opaque white fill when `--background` is transparent.

## URL prefix and app metadata

Use `--prefix` so HTML and `site.webmanifest` point at the correct public path
(for example `assets/favicons/` or `/favicons/`).

`--name` / `--short-name` feed the web manifest. Theme and background colours
default as documented in [Reference](reference.md).

## Skipping optional outputs

| Flag | Effect |
|------|--------|
| `--no-ico` | Skip `favicon.ico` |
| `--no-html` | Skip the HTML snippet |
| `--no-manifest` | Skip `site.webmanifest` |
| `--overwrite` | Replace existing generated files |

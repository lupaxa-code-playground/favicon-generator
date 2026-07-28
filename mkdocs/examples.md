# Examples

## Minimal PNG

```bash
favicon-generator logo.png
```

## SVG with site paths

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

## Overwrite an existing output directory

```bash
favicon-generator logo.png --output-dir favicons --overwrite
```

## Skip ICO and HTML

```bash
favicon-generator logo.png --no-ico --no-html
```

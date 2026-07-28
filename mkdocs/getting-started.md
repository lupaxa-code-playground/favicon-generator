# Getting started

## Requirements

- Python 3.10+
- For SVG sources: system Cairo (`brew install cairo` on macOS, or
  `apt install libcairo2` on Debian/Ubuntu)

## Install

```bash
python -m pip install lupaxa-favicon-generator
```

Editable / development install:

```bash
python -m pip install -e ".[dev]"
```

## First run

```bash
favicon-generator --help
favicon-generator logo.png
```

By default, files are written to `./favicons`. Use `--overwrite` if that
directory already contains generated files you want replaced.

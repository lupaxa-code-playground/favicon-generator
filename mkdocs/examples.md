# Examples

Template showcase of Material / Python-Markdown features. Keep or delete this
page after you start real project docs.

## Admonitions

!!! note "Note"
    Useful for tip-style callouts.

!!! warning "Warning"
    Call out risk or irreversible actions.

!!! failure "Failure"
    Describe error cases and recovery.

!!! tip "Tip"
    Optional shortcuts or recommended defaults.

## Tabs

=== "macOS"

    ```bash
    brew install your-project
    ```

=== "Linux"

    ```bash
    sudo apt install your-project
    ```

=== "Python"

    ```bash
    pip install your-project
    ```

## Code

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"


print(greet("Your Project"))
```

Inline code and keys: press ++ctrl+c++ to cancel, or run `your-project --help`.

## Tables

| Field | Type | Required |
| --- | --- | --- |
| `name` | string | yes |
| `enabled` | boolean | no |
| `retries` | integer | no |

## Task lists

- [x] Clone the template
- [x] Install requirements and run `mkdocs serve`
- [ ] Replace placeholders in `mkdocs.yml`
- [ ] Rewrite sample pages for your project

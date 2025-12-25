# CodeOptiX Documentation

This directory contains the MkDocs documentation for CodeOptiX.

## Building the Documentation

### Install Dependencies

```bash
pip install -e ".[docs]"
# Or with uv:
uv sync --extra docs
```

### Build Documentation

```bash
mkdocs build
```

### Serve Locally

```bash
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

## Documentation Structure

- `index.md` - Homepage
- `getting-started/` - Beginner guides
- `concepts/` - Core concepts
- `guides/` - How-to guides
- `advanced/` - Advanced topics
- `examples/` - Code examples
- `api-reference.md` - API documentation

## Custom Styling

Custom CSS files in `stylesheets/`:
- `extra.css` - Base styles and dark/light mode
- `gradients.css` - Gradient text for headings
- `syntax.css` - Syntax highlighting colors

## Contributing

When adding new documentation:
1. Create markdown files in appropriate directories
2. Update `mkdocs.yml` navigation
3. Test locally with `mkdocs serve`
4. Ensure beginner-friendly language


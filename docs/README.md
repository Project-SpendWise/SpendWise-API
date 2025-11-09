# Documentation

This directory contains the source files for the SpendWise API documentation, built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## Building the Documentation

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install MkDocs and all required dependencies.

### Serve Locally (Development)

To preview the documentation locally with auto-reload:

```bash
mkdocs serve
```

The documentation will be available at `http://127.0.0.1:8000`

### Build Static Site

To build the documentation as a static site:

```bash
mkdocs build
```

The built site will be in the `site/` directory (which is gitignored).

### Deploy

To deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

## Documentation Structure

- `index.md` - Homepage
- `getting-started/` - Installation and setup guides
- `api/` - API reference documentation
- `models/` - Database model documentation
- `development/` - Development guides
- `utilities/` - Utility function documentation

## Editing Documentation

1. Edit the Markdown files in this directory
2. Run `mkdocs serve` to preview changes
3. Commit changes to version control

## Configuration

Documentation configuration is in `mkdocs.yml` at the project root.


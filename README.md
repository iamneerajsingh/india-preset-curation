# India Preset Curation

A Markdown-first curation workspace for India, with a Mona Mayhem-inspired GitHub Pages interface.

## Content structure

```text
modules/
  MS-4019/
    README.md
    industry/
      README.md
      Digital Native/README.md
      FSI/README.md
      Gov/README.md
      Healthcare/README.md
      IT-ITeS/README.md
      Manufacturing-Mobility/README.md
      Retail/README.md
      Telco/README.md
  MS-4019-persona/
    README.md
    industry/
      ...same eight verticals, with persona-led starter use cases
templates/
  use-case.md
scripts/
  build.py
site/
  assets/
```

## Update a page

Edit any secondary `README.md` under `modules/` directly in GitHub and commit to `main`. GitHub Actions rebuilds and publishes the site. Each Markdown file becomes a page, and the navigation, search, and page counts update automatically.

Add a module by creating `modules/YOUR-MODULE/README.md`. Add a vertical or use case by creating another folder or Markdown file inside a module. Copy `templates/use-case.md` as a starting point. Use a single `# Heading` for the page title and a short first paragraph for its card description. Relative Markdown links, including paths with spaces, are supported.

The initial use cases are **draft curation scaffolds**, not official Microsoft course content, validated presets, or regulatory guidance. Review and replace them before delivery. Only use synthetic or explicitly approved, non-sensitive demo data.

## Run locally

Requires Python 3.12 or newer.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python scripts/build.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. For the project Pages URL, the workflow builds with `--base-path /india-preset-curation`. The generated `dist/` folder is not committed.

## Publishing

`.github/workflows/pages.yml` builds on pushes to `main` and manual dispatch, then deploys through GitHub Pages. Repository **Settings > Pages > Source** must be **GitHub Actions**. The intended URL is `https://iamneerajsingh.github.io/india-preset-curation/`.

The UI uses local CSS and JavaScript, system fonts, a dark grid, cyan-to-purple accents, responsive navigation, content search, module filtering, and a light/dark toggle. No runtime API, tracking, or external font service is required. Change the design in `site/assets/`; content authors only need Markdown.

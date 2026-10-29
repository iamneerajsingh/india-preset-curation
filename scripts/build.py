"""Build a static, searchable site from the module Markdown tree."""

import argparse
import html
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/iamneerajsingh/india-preset-curation"


def page_path(source):
    return source.with_suffix(".html")


def href(path, base):
    return base + "/" + quote(path.as_posix())


def title_and_summary(text, fallback):
    heading = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = heading.group(1).strip() if heading else fallback
    paragraphs = re.split(r"\n\s*\n", text.strip())
    summary = next(
        (p.strip().replace("\n", " ") for p in paragraphs if p and not p.startswith(("#", "|", "```", "-", ">"))),
        "Open this collection to explore its curation notes and use cases.",
    )
    return title, summary


class LocalLinks(Treeprocessor):
    def run(self, root):
        for element in root.iter("a"):
            target = element.get("href", "")
            parts = urlsplit(target)
            if not parts.scheme and not parts.netloc and parts.path.lower().endswith(".md"):
                local_path = unquote(parts.path)
                resolved = posixpath.normpath((self.source.parent / local_path).as_posix()) if self.source else None
                if resolved and not resolved.startswith("modules/"):
                    element.set("href", REPO + "/blob/main/" + quote(resolved) + ("#" + parts.fragment if parts.fragment else ""))
                else:
                    element.set("href", urlunsplit(parts._replace(path=quote(local_path[:-3] + ".html"))))


class MarkdownLinks(Extension):
    def __init__(self, source=None):
        self.source = source
        super().__init__()

    def extendMarkdown(self, md):
        processor = LocalLinks(md)
        processor.source = self.source
        md.treeprocessors.register(processor, "local-links", 5)


def render_markdown(text, source=None):
    return markdown.markdown(text, extensions=["tables", "fenced_code", "toc", MarkdownLinks(source)])


def cards(pages, base):
    result = []
    for page in pages:
        title = html.escape(page["title"])
        summary = html.escape(page["summary"])
        module = html.escape(page["module"])
        search = html.escape((page["title"] + " " + page["text"]).lower(), quote=True)
        result.append(f"""<a class="content-card" href="{href(page_path(page['path']), base)}"
            data-module="{module}" data-search="{search}">
            <span class="card-eyebrow">{module} <span aria-hidden="true">↗</span></span>
            <h3>{title}</h3><p>{summary}</p>
            <span class="card-bottom">Explore collection <span aria-hidden="true">→</span></span></a>""")
    return "\n".join(result)


def layout(title, body, pages, base, current=None):
    def directory_tree(directory, label):
        # Include intermediate folders even when they do not have a README.
        children = sorted({
            directory / p["path"].relative_to(directory).parts[0]
            for p in pages if p["path"].is_relative_to(directory)
            and len(p["path"].relative_to(directory).parts) > 1
        })
        links = "".join(
            f'<a href="{href(page_path(p["path"]), base)}"'
            + (' aria-current="page"' if p["path"] == current else "")
            + f'>{html.escape(p["path"].name if p["path"].name == "README.md" else p["title"])}</a>'
            for p in pages if p["path"].parent == directory
        )
        nested = "".join(directory_tree(child, child.name) for child in children)
        return f"<details open><summary>{html.escape(label)}/</summary>{links}{nested}</details>"

    nav = [
        directory_tree(Path("modules") / module, module)
        for module in sorted({p["module"] for p in pages})
    ]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A Markdown-first workspace for India preset curation, modules, personas and industry use cases.">
<meta name="color-scheme" content="dark light"><title>{html.escape(title)} · India Presets</title>
<link rel="icon" href="{base}/assets/mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}/assets/style.css">
<script src="{base}/assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="topbar"><a class="brand" href="{base}/"><img src="{base}/assets/mark.svg" alt="" width="34" height="34">
<span>india<span class="brand-muted"> / presets</span></span></a>
<nav aria-label="Main"><a href="{base}/#collections">Collections</a><a href="{REPO}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
<button id="theme" type="button" aria-label="Switch to light theme">☀ <span>Light</span></button></nav></header>
{body}
<footer><span>Built for India. Curated together.</span><a href="{REPO}/blob/main/README.md">Markdown in. Possibilities out. ↗</a></footer>
<dialog id="browse-dialog"><div class="dialog-heading"><h2>All collections</h2><button id="close-browse" type="button" autofocus>Close ✕</button></div>
<nav class="tree" aria-label="Content navigation">{''.join(nav)}</nav></dialog>
</body></html>"""


def build(root=ROOT, base=""):
    base = "/" + base.strip("/") if base.strip("/") else ""
    output = root / "dist"
    output.mkdir(exist_ok=True)
    shutil.copytree(root / "site/assets", output / "assets", dirs_exist_ok=True)
    pages = []
    for source in sorted((root / "modules").rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        path = source.relative_to(root)
        title, summary = title_and_summary(text, source.stem)
        pages.append(dict(path=path, title=title, summary=summary, text=text, module=path.parts[1]))
    if not pages:
        raise ValueError("No module Markdown found")
    modules = [p for p in pages if len(p["path"].parts) == 3 and p["path"].name == "README.md"]
    verticals = {p["path"].parts[3] for p in pages if len(p["path"].parts) >= 5 and p["path"].parts[2] == "industry"}
    filters = "".join(f'<button type="button" class="filter" data-filter="{html.escape(m)}" aria-pressed="false">{html.escape(m)}</button>'
                      for m in sorted({p["module"] for p in pages}))
    home = f"""<main id="main">
<section class="hero"><div class="eyebrow"><span class="status-dot"></span> THE INDIA CURATION WORKSPACE</div>
<h1>Local context.<br><span class="gradient">Limitless possibilities.</span></h1>
<p class="hero-copy">Your launchpad for India-ready presets. Explore modules, discover personas,<br class="desktop-break">
and turn industry scenarios into meaningful Copilot experiences.</p>
<div class="hero-panel"><div><span class="label">CHOOSE YOUR STARTING POINT</span>
<p>One workspace. Two perspectives. Start with the module,<br class="desktop-break"> or put your audience at the centre.</p></div>
<div class="chips"><span>Module-led</span><span>Persona-first</span><span>India-focused</span></div></div>
<div class="hero-actions"><a class="button primary" href="#collections">Explore collections <span aria-hidden="true">→</span></a>
<a class="button secondary" href="{REPO}/tree/main/modules">Open content folders ↗</a></div>
<p class="hero-note">Made to evolve. Edit a README. Publish a new possibility.</p>
<div class="stats"><div><strong>{len(modules):02}</strong><span>Module tracks</span></div><div><strong>{len(verticals):02}</strong><span>India verticals</span></div>
<div><strong>MD</strong><span>Powered by Markdown</span></div></div></section>
<section class="collection-section" id="collections"><div class="section-top"><div><span class="label">FIND YOUR NEXT USE CASE</span>
<h2>The curation library<span class="accent">.</span></h2></div><button class="button secondary" id="browse" type="button">Browse folder tree ↗</button></div>
<div class="toolbar"><div class="filters" role="group" aria-label="Filter by module"><button class="filter active" type="button" data-filter="all" aria-pressed="true">All collections</button>{filters}</div>
<label class="search"><span class="sr-only">Search collections</span><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="Search verticals, personas, use cases…"></label></div>
<p id="result-count" class="result-count" aria-live="polite">{len(pages)} collections to explore</p>
<div class="card-grid">{cards(pages, base)}</div><p id="empty" hidden>No matches. Try another keyword or module.</p>
<div class="contribute"><div><span class="label">A LIVING LIBRARY</span><h2>Your next idea belongs here.</h2><p>Add a folder. Update a README. Keep the India story growing.</p></div>
<a class="button secondary" href="{REPO}/blob/main/templates/use-case.md">Get the use-case template ↗</a></div>
<p class="draft-note">Starter content is draft scaffolding, not official Microsoft training or a validated preset. Review before use.</p></section></main>"""
    (output / "index.html").write_text(layout("Home", home, pages, base), encoding="utf-8")
    for page in pages:
        path = page["path"]
        edit = REPO + "/edit/main/" + quote(path.as_posix())
        children = [p for p in pages if p["path"] != path and p["path"].is_relative_to(path.parent)] if path.name == "README.md" else []
        body = f"""<main id="main" class="reading-layout"><aside class="reading-sidebar"><a href="{base}/#collections">← All collections</a>
<button id="browse" type="button" class="button secondary">Browse folder tree</button><span class="label">{html.escape(page['module'])}</span>
<p class="source-path">{html.escape(path.as_posix())}</p><a href="{edit}">Edit this Markdown ↗</a></aside>
<div class="reading-content"><div class="page-meta"><span class="eyebrow">INDIA PRESET CURATION</span><span class="draft-badge">DRAFT COLLECTION</span></div>
<article class="markdown">{render_markdown(page['text'], path)}</article>
{('<section class="related"><h2>In this collection</h2><div class="card-grid">' + cards(children, base) + '</div></section>') if children else ''}
<div class="edit-note">This page is generated from a Markdown file. <a href="{edit}">Improve this collection on GitHub ↗</a></div></div></main>"""
        target = output / page_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(layout(page["title"], body, pages, base, path), encoding="utf-8")
    (output / ".nojekyll").touch()
    (output / "404.html").write_text(layout("Page not found", f'<main id="main" class="not-found"><h1>Off the map.</h1><p>This collection could not be found.</p><a class="button primary" href="{base}/">Back to the library</a></main>', pages, base), encoding="utf-8")
    print(f"Built {len(pages)} content pages and home in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-path", default="")
    build(base=parser.parse_args().base_path)

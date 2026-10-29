import importlib.util
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from shutil import copytree
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "scripts/build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.urls.append(value)


class BuildTests(unittest.TestCase):
    def test_titles_and_relative_markdown_links(self):
        title, summary = builder.title_and_summary("# A title\n\nA useful summary.\n\n## Next", "fallback")
        self.assertEqual((title, summary), ("A title", "A useful summary."))
        rendered = builder.render_markdown("[Digital](<Digital Native/README.md#overview>)")
        self.assertIn('href="Digital%20Native/README.html#overview"', rendered)
        self.assertIn('href="https://example.com/a.md"', builder.render_markdown("[Remote](https://example.com/a.md)"))
        rendered = builder.render_markdown(
            "[Template](../../templates/use-case.md)", Path("modules/MS-4019/README.md")
        )
        self.assertIn(builder.REPO + "/blob/main/templates/use-case.md", rendered)

    def test_build_discovers_new_content_and_all_local_links_resolve(self):
        for base in ("", "/india-preset-curation"):
            with self.subTest(base=base), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                copytree(ROOT / "modules", root / "modules")
                copytree(ROOT / "templates", root / "templates")
                copytree(ROOT / "site", root / "site")
                # Templates are repository-only links, not generated content pages.
                new_page = root / "modules/MS-4019/industry/IT-ITeS/More ideas.md"
                new_page.write_text("# More ideas\n\nAn automatically discovered use case.")
                builder.build(root, base)
                output = root / "dist"
                home = (output / "index.html").read_text()
                self.assertIn("More ideas", home)
                self.assertIn("21 collections to explore", home)
                self.assertIn("<strong>08</strong>", home)
                self.assertIn("<summary>Digital Native/</summary>", home)
                for page in output.rglob("*.html"):
                    parser = References()
                    parser.feed(page.read_text())
                    for target in parser.urls:
                        parts = urlsplit(target)
                        if parts.scheme or parts.netloc or not parts.path:
                            continue
                        path = unquote(parts.path)
                        if path.startswith("/"):
                            self.assertTrue(path.startswith(base + "/"), target)
                            resolved = output / path[len(base):].lstrip("/")
                        else:
                            resolved = page.parent / path
                        self.assertTrue(resolved.exists(), f"{page.relative_to(output)} -> {target}")


if __name__ == "__main__":
    unittest.main()

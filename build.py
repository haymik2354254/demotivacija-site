# build.py - FINAL WORKING VERSION
import os
import json
from datetime import datetime
from xml.etree import ElementTree as ET
from jinja2 import Environment, FileSystemLoader

BASE_URL = "https://demotivacija.si"


env = Environment(loader=FileSystemLoader('templates'))
index_template = env.get_template('index-template.html')


def build_sitemap(visible_posts):
    """Generate sitemap.xml with the homepage, static pages and published blog posts."""
    urlset = ET.Element(
        "urlset",
        {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    )

    def add_url(path, lastmod=None):
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"{BASE_URL}{path}"
        if lastmod:
            ET.SubElement(url, "lastmod").text = lastmod

    # Canonical homepage only — do not add /index.html.
    add_url("/")

    # Add static indexable pages only if they exist in the project.
    for filename in ("zakaj.html", "privacy.html"):
        if os.path.exists(filename):
            add_url(f"/{filename}")

    # Add only posts that are already published/visible.
    for post in visible_posts:
        relative_url = (post.get("url") or "").strip().lstrip("/")
        if not relative_url:
            continue

        post_date = post.get("date")
        lastmod = post_date.strftime("%Y-%m-%d") if isinstance(post_date, datetime) else None
        add_url(f"/{relative_url}", lastmod=lastmod)

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write("sitemap.xml", encoding="utf-8", xml_declaration=True)


def main():
    print("🏗️  Building index.html...")

    with open("data/posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    # Prepare posts for template
    for post in posts:
        date_str = post.get("date")
        if isinstance(date_str, str):
            try:
                post["date"] = datetime.strptime(date_str, "%Y-%m-%d")
            except (TypeError, ValueError):
                post["date"] = today
        post["date_str"] = date_str or today_str

    # Filter and sort
    visible_posts = [p for p in posts if p.get("date") and p["date"] <= today]
    visible_posts.sort(key=lambda x: x["date"], reverse=True)

    rendered = index_template.render(
        posts=visible_posts,
        today=today_str
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(rendered)

    build_sitemap(visible_posts)

    print(f"✅ index.html built with {len(visible_posts)} visible posts.")
    print(f"✅ sitemap.xml built with {len(visible_posts)} published posts.")


if __name__ == "__main__":
    main()

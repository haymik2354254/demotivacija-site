# build.py - FINAL WORKING VERSION
import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
index_template = env.get_template('index-template.html')

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
            except:
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

    print(f"✅ index.html built with {len(visible_posts)} visible posts.")

if __name__ == "__main__":
    main()
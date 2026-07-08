import feedparser


def fetch_posts(account):
    feed = feedparser.parse(account["rss_url"])

    posts = []

    for entry in feed.entries:
        post_id = entry.get("id") or entry.get("link")

        posts.append({
            "account_name": account["name"],
            "id": post_id,
            "title": entry.get("title", "タイトルなし"),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", "")
        })

    return posts
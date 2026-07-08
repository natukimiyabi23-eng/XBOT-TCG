import feedparser
import re
import html


def clean_text(text):
    text = re.sub("<.*?>", "", text)
    text = html.unescape(text)
    text = text.strip()

    if len(text) > 180:
        text = text[:180] + "..."

    return text


def extract_image(entry):
    # RSS.appで画像が media_content に入る場合
    if "media_content" in entry:
        for media in entry.media_content:
            if "url" in media:
                return media["url"]

    # enclosure に画像が入る場合
    if "enclosures" in entry:
        for enclosure in entry.enclosures:
            if enclosure.get("type", "").startswith("image/"):
                return enclosure.get("href")

    # summary内のimgタグから拾う場合
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)

    if match:
        return html.unescape(match.group(1))

    return None


def fetch_posts(account):
    feed = feedparser.parse(account["rss_url"])

    posts = []

    for entry in feed.entries:
        post_id = entry.get("id") or entry.get("link")

        title = clean_text(entry.get("title", "タイトルなし"))
        summary = clean_text(entry.get("summary", ""))
        image_url = extract_image(entry)

        posts.append({
            "account_name": account["name"],
            "id": post_id,
            "title": title,
            "summary": summary,
            "link": entry.get("link", ""),
            "image_url": image_url,
            "published": entry.get("published", "")
        })

    return posts
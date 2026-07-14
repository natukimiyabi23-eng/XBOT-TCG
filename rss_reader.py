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
    """
    RSS内から最初の画像URLを探して返す。
    RSSサービスによって画像の保存場所が違うため、
    複数の形式を順番に確認する。
    """

    # 1. media:content
    media_content = entry.get("media_content", [])

    for media in media_content:
        url = media.get("url")

        if url:
            return html.unescape(url)

    # 2. media:thumbnail
    media_thumbnail = entry.get("media_thumbnail", [])

    for thumbnail in media_thumbnail:
        url = thumbnail.get("url")

        if url:
            return html.unescape(url)

    # 3. enclosure
    enclosures = entry.get("enclosures", [])

    for enclosure in enclosures:
        enclosure_type = enclosure.get("type", "")
        url = enclosure.get("href") or enclosure.get("url")

        if url and enclosure_type.startswith("image/"):
            return html.unescape(url)

    # 4. summary / description内のimgタグ
    html_sources = [
        entry.get("summary", ""),
        entry.get("description", "")
    ]

    # 5. content内のHTMLも確認
    for content in entry.get("content", []):
        if isinstance(content, dict):
            html_sources.append(content.get("value", ""))

    for source in html_sources:
        if not source:
            continue

        # src="..." と src='...' の両方に対応
        match = re.search(
            r"""<img[^>]+src=["']([^"']+)["']""",
            source,
            re.IGNORECASE
        )

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
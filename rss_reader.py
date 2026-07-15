from datetime import datetime
import feedparser
import re
import html


MAX_DESCRIPTION_LENGTH = 100


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<.*?>", "", text, flags=re.DOTALL)
    text = html.unescape(text)
    text = re.sub(r"https?://\S+", "", text)
    text = " ".join(text.split())
    text = re.sub(r"(?:\s*#[^\s#]+)+\s*$", "", text)

    return text.strip()


def shorten_text(text, max_length):
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


def normalize_for_comparison(text):
    if not text:
        return ""

    return re.sub(r"\s+", "", text)


def remove_title_from_summary(title, summary):
    if not title or not summary:
        return summary

    normalized_title = normalize_for_comparison(title)
    normalized_summary = normalize_for_comparison(summary)

    if normalized_summary == normalized_title:
        return ""

    if (
        normalized_title
        and normalized_summary.startswith(normalized_title)
    ):
        target_character_count = len(normalized_title)
        counted_characters = 0
        cut_position = 0

        for index, character in enumerate(summary):
            if not character.isspace():
                counted_characters += 1

            if counted_characters >= target_character_count:
                cut_position = index + 1
                break

        return summary[cut_position:].strip()

    return summary


def extract_image(entry):
    for media in entry.get("media_content", []):
        url = media.get("url")

        if url:
            return html.unescape(url)

    for thumbnail in entry.get("media_thumbnail", []):
        url = thumbnail.get("url")

        if url:
            return html.unescape(url)

    for enclosure in entry.get("enclosures", []):
        enclosure_type = enclosure.get("type", "")
        url = enclosure.get("href") or enclosure.get("url")

        if url and enclosure_type.startswith("image/"):
            return html.unescape(url)

    html_sources = [
        entry.get("summary", ""),
        entry.get("description", "")
    ]

    for content in entry.get("content", []):
        if isinstance(content, dict):
            html_sources.append(content.get("value", ""))

    for source in html_sources:
        if not source:
            continue

        match = re.search(
            r"""<img[^>]+src=["']([^"']+)["']""",
            source,
            re.IGNORECASE
        )

        if match:
            return html.unescape(match.group(1))

    return None


def fetch_posts(account):
    """
    RSSを取得して、取得先・時刻・HTTP状態・件数をログへ表示する。
    """

    account_name = account.get("name", "不明なアカウント")
    rss_url = account.get("rss_url", "")

    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"[{started_at}] RSS取得開始: "
        f"{account_name} -> {rss_url}",
        flush=True
    )

    feed = feedparser.parse(rss_url)

    status = getattr(feed, "status", "不明")
    entry_count = len(feed.entries)
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"[{finished_at}] RSS取得完了: "
        f"{account_name} / status={status} / entries={entry_count}",
        flush=True
    )

    if getattr(feed, "bozo", False):
        error = getattr(
            feed,
            "bozo_exception",
            "不明なRSS解析エラー"
        )

        print(
            f"[{finished_at}] RSS解析警告: "
            f"{account_name} / "
            f"{type(error).__name__}: {error}",
            flush=True
        )

    posts = []

    for entry in feed.entries:
        post_id = entry.get("id") or entry.get("link")

        full_title = clean_text(
            entry.get("title", "タイトルなし")
        )

        full_summary = clean_text(
            entry.get("summary", "")
        )

        full_summary = remove_title_from_summary(
            full_title,
            full_summary
        )

        title = shorten_text(
            full_title,
            MAX_DESCRIPTION_LENGTH
        )

        summary = shorten_text(
            full_summary,
            MAX_DESCRIPTION_LENGTH
        )

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
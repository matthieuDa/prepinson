"""Build a local, first-party Instagram snapshot when a private token is present."""

from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import json
import os
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"
FIELDS = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{media_type,media_url,thumbnail_url}"


def token():
    value = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "").strip()
    if value:
        return value
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("INSTAGRAM_ACCESS_TOKEN="):
                value = line.split("=", 1)[1].strip()
                if time.time() - path.stat().st_mtime < 7 * 86400:
                    return value
                refresh_url = "https://graph.instagram.com/refresh_access_token?" + urlencode({"grant_type": "ig_refresh_token", "access_token": value})
                try:
                    with urlopen(Request(refresh_url), timeout=20) as response:
                        refreshed = json.load(response).get("access_token")
                    if refreshed:
                        temporary = path.with_name(".env.tmp")
                        temporary.write_text(f"INSTAGRAM_ACCESS_TOKEN={refreshed}\n", encoding="utf-8")
                        temporary.chmod(0o600)
                        temporary.replace(path)
                        return refreshed
                except Exception:
                    print("Instagram token renewal failed; trying the current token")
                return value
    return ""


def image_source(item):
    if item.get("media_type") == "VIDEO":
        return item.get("thumbnail_url") or item.get("media_url")
    if item.get("media_type") == "CAROUSEL_ALBUM":
        for child in item.get("children", {}).get("data", []):
            if child.get("media_type") == "IMAGE" and child.get("media_url"):
                return child["media_url"]
        return item.get("media_url") or item.get("thumbnail_url")
    return item.get("media_url") or item.get("thumbnail_url")


def trusted_image(url):
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return parsed.scheme == "https" and (host.endswith(".cdninstagram.com") or host.endswith(".fbcdn.net"))


def build():
    if os.environ.get("INSTAGRAM_SNAPSHOT_MODE") == "skip":
        shutil.rmtree(OUT / "assets" / "instagram", ignore_errors=True)
        (OUT / "instagram-feed.json").unlink(missing_ok=True)
        print("Instagram snapshot skipped: Netlify serves the refreshed feed from Blobs")
        return
    access_token = token()
    if not access_token:
        print("Instagram snapshot kept if present: no server-side token configured")
        return

    images = OUT / "assets" / "instagram"
    images.mkdir(parents=True, exist_ok=True)
    node = os.environ.get("NODE") or shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required to optimize Instagram images")
    try:
        url = "https://graph.instagram.com/v24.0/me/media?" + urlencode({"fields": FIELDS, "limit": 6})
        with urlopen(Request(url, headers={"Authorization": f"Bearer {access_token}"}), timeout=20) as response:
            media = json.load(response)["data"]
        if not isinstance(media, list):
            raise ValueError("Instagram returned an invalid media list")
        posts = []
        for item in media[:6]:
            source = image_source(item)
            permalink = item.get("permalink", "")
            media_id = str(item.get("id", ""))
            if not (8 <= len(media_id) <= 30 and media_id.isdigit() and source
                    and trusted_image(source) and permalink.startswith("https://www.instagram.com/")):
                raise ValueError("Instagram returned an unusable publication")
            filename = f"{media_id}.webp"
            target = images / filename
            if not target.is_file() or target.stat().st_size > 180_000:
                with urlopen(Request(source, headers={"User-Agent": "PrepinsonFeed/1.0"}), timeout=20) as response:
                    content_type = response.headers.get_content_type()
                    content = response.read(8_000_001)
                if len(content) > 8_000_000 or content_type not in {"image/jpeg", "image/webp", "image/png"}:
                    raise ValueError(f"Instagram image {media_id} is unusable")
                optimized = subprocess.run(
                    [node, str(ROOT / "netlify" / "lib" / "instagram-image.mjs")],
                    input=content, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
                ).stdout
                if len(optimized) > 180_000:
                    raise ValueError(f"Instagram image {media_id} exceeds the output limit")
                temporary = target.with_suffix(".webp.tmp")
                temporary.write_bytes(optimized)
                temporary.replace(target)
            posts.append({
                "id": media_id,
                "caption": item.get("caption", "")[:500],
                "permalink": permalink,
                "image": f"/assets/instagram/{filename}",
                "timestamp": item.get("timestamp", ""),
            })
        snapshot = OUT / "instagram-feed.json"
        temporary = snapshot.with_suffix(".json.tmp")
        temporary.write_text(json.dumps({"posts": posts, "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, ensure_ascii=False), encoding="utf-8")
        temporary.replace(snapshot)
        active = {f"{post['id']}.webp" for post in posts}
        now = time.time()
        for image in images.glob("*.webp"):
            if image.name in active:
                image.touch()
            elif now - image.stat().st_mtime >= 7 * 86400:
                image.unlink()
        print(f"Instagram snapshot: {len(posts)} posts, first-party images")
        if len(posts) < 6:
            print(f"Instagram warning: only {len(posts)} publications available")
    except Exception as error:
        print(f"Instagram sync failed; last complete snapshot retained: {error}")


if __name__ == "__main__":
    build()

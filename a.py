import os
import hashlib
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# ---------------- CONFIG ----------------
SITEMAPS = [
    "https://bollyflix.sarl/post-sitemap.xml",
    "https://bollyflix.sarl/post-sitemap2.xml",
    "https://bollyflix.sarl/post-sitemap3.xml",
    "https://bollyflix.sarl/post-sitemap4.xml",
    "https://bollyflix.sarl/post-sitemap5.xml",
    "https://bollyflix.sarl/post-sitemap6.xml",
    "https://bollyflix.sarl/post-sitemap7.xml",
    "https://bollyflix.sarl/post-sitemap8.xml",
    "https://bollyflix.sarl/post-sitemap9.xml",
    "https://bollyflix.sarl/post-sitemap10.xml",
    "https://bollyflix.sarl/post-sitemap11.xml",
    "https://bollyflix.sarl/post-sitemap12.xml",
    "https://bollyflix.sarl/post-sitemap13.xml",
    "https://bollyflix.sarl/post-sitemap14.xml",
    "https://bollyflix.sarl/post-sitemap15.xml",
    "https://bollyflix.sarl/post-sitemap16.xml",
]

SAVE_DIR = "posts"
WORKERS = 15   # increase to 20–30 if your internet is strong
# ---------------------------------------

os.makedirs(SAVE_DIR, exist_ok=True)

visited_urls = set()
content_hashes = set()

lock = Lock()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (FastSitemapDownloader/2.0)"
}


def html_hash(html):
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def get_post_urls(sitemap_url):
    print("📄 Reading sitemap:", sitemap_url)
    r = requests.get(sitemap_url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    urls = []
    for u in root.findall("ns:url", ns):
        loc = u.find("ns:loc", ns)
        if loc is not None:
            urls.append(loc.text.strip().rstrip("/"))

    return urls


def save_post(url, html):
    slug = urlparse(url).path.strip("/").replace("/", "_")
    filename = slug + ".html"

    path = os.path.join(SAVE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def download_post(url):
    with lock:
        if url in visited_urls:
            return
        visited_urls.add(url)

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return
    except:
        return

    html = r.text
    h = html_hash(html)

    with lock:
        if h in content_hashes:
            return
        content_hashes.add(h)

    save_post(url, html)
    print("✅ Saved:", url)


# ---------------- START ----------------
all_urls = []

for sm in SITEMAPS:
    try:
        all_urls.extend(get_post_urls(sm))
    except Exception as e:
        print("❌ Sitemap failed:", sm, e)

# Remove duplicate URLs early
all_urls = list(set(all_urls))

print("\n🚀 Total unique URLs:", len(all_urls))
print("⚡ Starting fast download...\n")

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = [executor.submit(download_post, url) for url in all_urls]
    for _ in as_completed(futures):
        pass

print("\n🎉 DONE")
print("📄 Pages saved:", len(content_hashes))

# a.py
import os
from bs4 import BeautifulSoup

# Paths
INPUT_FOLDER = "posts"      # Folder containing HTML files
OUTPUT_FOLDER = "output"   # Folder to save generated HTML

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to extract movie info from HTML content
def extract_movie_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Movie title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "No Title"

    # OG image
    og_image_tag = soup.find("meta", property="og:image")
    og_image = og_image_tag.get("content") if og_image_tag else ""

    # Movie details (from <ul>)
    details = {}
    ul_tag = soup.find("ul")
    if ul_tag:
        for li in ul_tag.find_all("li"):
            strong_tag = li.find("strong")
            if strong_tag and ":" in li.get_text():
                key = strong_tag.get_text(strip=True).rstrip(":")
                value = li.get_text(strip=True).replace(strong_tag.get_text(), "").lstrip(": ").strip()
                details[key] = value

    # Screenshots
    screenshots = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src:
            screenshots.append(src)

    # Download links (from <h5> and following <p>)
    downloads = []
    for h5 in soup.find_all("h5"):
        version = h5.get_text(strip=True)
        p_tag = h5.find_next_sibling("p")
        if p_tag:
            links = []
            for a in p_tag.find_all("a"):
                href = a.get("href")
                if href:
                    links.append((a.get_text(strip=True), href))
            if links:
                downloads.append({"version": version, "links": links})

    return {
        "title": title,
        "og_image": og_image,
        "details": details,
        "screenshots": screenshots,
        "downloads": downloads
    }

# Function to generate HTML for each movie
def generate_html(movie):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{movie['title']}</title>
</head>
<body>
<h1>{movie['title']}</h1>
<img src="{movie['og_image']}" alt="{movie['title']}" style="max-width:300px;"/>

<h2>Movie Details:</h2>
<ul>
"""
    for key, value in movie["details"].items():
        html += f"<li><strong>{key}:</strong> {value}</li>\n"
    html += "</ul>\n"

    if movie["screenshots"]:
        html += "<h2>Screenshots:</h2>\n"
        for src in movie["screenshots"]:
            html += f'<img src="{src}" alt="screenshot" style="max-width:200px; margin:5px;">\n'

    if movie["downloads"]:
        html += "<h2>Download Links:</h2>\n"
        for dl in movie["downloads"]:
            html += f"<h3>{dl['version']}</h3>\n<p>\n"
            for text, link in dl["links"]:
                html += f'<a href="{link}" target="_blank">{text}</a> | '
            html = html.rstrip(" | ")
            html += "</p>\n"

    html += "</body>\n</html>"
    return html

# Process all HTML files in INPUT_FOLDER
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".html"):
        filepath = os.path.join(INPUT_FOLDER, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        movie_info = extract_movie_info(content)
        out_file = os.path.join(OUTPUT_FOLDER, filename)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(generate_html(movie_info))
        print(f"Processed: {filename}")

print("All HTML files processed successfully!")

import os
from bs4 import BeautifulSoup

# Paths
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))  # folder where a.py is located
INPUT_FOLDER = os.path.join(BASE_FOLDER, "posts")          # original HTML files
OUTPUT_FOLDER = os.path.join(BASE_FOLDER, "output")       # prebuilt HTML files

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Process all HTML files
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".html"):
        input_path = os.path.join(INPUT_FOLDER, filename)

        # Read HTML content
        with open(input_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Basic movie info
        title = soup.find("title").text if soup.find("title") else "No Title"
        cover_img = soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else ""

        # Movie details from <ul>
        details = {}
        for li in soup.find_all("li"):
            if li.strong:
                key = li.strong.text.replace(":", "").strip()
                value = li.text.replace(li.strong.text, "").strip()
                details[key] = value

        # Screenshots
        screenshots = [img["src"] for img in soup.find_all("img")]

        # Versions and download links
        versions = []
        for h5 in soup.find_all("h5"):
            version_name = h5.get_text(strip=True)
            # The next <p> after <h5> contains links
            p_tag = h5.find_next("p")
            links = []
            if p_tag:
                for a in p_tag.find_all("a", class_="dl"):
                    links.append({
                        "text": a.text.strip(),
                        "href": a["href"]
                    })
            versions.append({
                "name": version_name,
                "links": links
            })

        # Build prebuilt HTML
        prebuilt_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    img {{ max-width: 300px; margin: 10px; }}
    .details li {{ margin-bottom: 5px; }}
    .download a {{ display: inline-block; padding: 10px; background: #13BF3C; color: white; text-decoration: none; margin: 5px; border-radius: 5px; }}
    .version {{ margin-bottom: 20px; }}
</style>
</head>
<body>
<h1>{details.get("Full Name", title)}</h1>
<img src="{cover_img}" alt="Cover Image" />

<h2>Movie Details:</h2>
<ul class="details">
"""
        for k, v in details.items():
            prebuilt_html += f"    <li><strong>{k}:</strong> {v}</li>\n"
        prebuilt_html += "</ul>\n"

        # Screenshots
        prebuilt_html += "<h2>Screenshots:</h2>\n"
        for shot in screenshots:
            prebuilt_html += f'<img src="{shot}" alt="Screenshot" />\n'

        # Versions and links
        prebuilt_html += "<h2>Download Versions:</h2>\n"
        for v in versions:
            prebuilt_html += f'<div class="version"><h3>{v["name"]}</h3>\n<div class="download">\n'
            for link in v["links"]:
                prebuilt_html += f'<a href="{link["href"]}" target="_blank">{link["text"]}</a>\n'
            prebuilt_html += "</div></div>\n"

        prebuilt_html += "</body>\n</html>"

        # Save output
        output_path = os.path.join(OUTPUT_FOLDER, f"prebuilt_{filename}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(prebuilt_html)

        print(f"Processed: {filename} -> {output_path}")

print("\nAll HTML files processed successfully!")

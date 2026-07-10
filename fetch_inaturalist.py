#!/usr/bin/env python3
import json
import urllib.request
import re
import sys

def fetch_observations(user_id="jahrik", limit=3):
    url = f"https://api.inaturalist.org/v1/observations?user_id={user_id}&per_page={limit}&order_by=created_at&order=desc"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get('results', [])
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return []

def generate_markdown(observations):
    if not observations:
        return "*No recent observations found.*"
    
    md = []
    md.append("<p align='center'>")
    for obs in observations:
        taxon = obs.get('taxon', {})
        name = taxon.get('preferred_common_name') or taxon.get('name') or "Unknown"
        obs_url = f"https://www.inaturalist.org/observations/{obs.get('id')}"
        photos = obs.get('photos', [])
        
        if photos:
            # Use medium image instead of square for better quality, if available
            img_url = photos[0].get('url', '').replace('square', 'medium')
            md.append(f"  <a href='{obs_url}' title='{name}'>")
            md.append(f"    <img src='{img_url}' width='250' alt='{name}' style='border-radius: 8px;' />")
            md.append(f"  </a>")
    
    md.append("</p>")
    return "\n".join(md)

def update_readme(new_content, readme_path="README.md"):
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to find the start and end markers and replace everything in between
        pattern = re.compile(r"(<!-- inat-start -->).*?(<!-- inat-end -->)", re.DOTALL)
        
        if not pattern.search(content):
            print(f"Markers not found in {readme_path}", file=sys.stderr)
            return False

        updated_content = pattern.sub(r"\g<1>\n" + new_content + r"\n\g<2>", content)

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("README.md updated successfully.")
        return True
    except Exception as e:
        print(f"Error updating README: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    print("Fetching observations...")
    obs = fetch_observations()
    md_content = generate_markdown(obs)
    update_readme(md_content)

import urllib.request
import urllib.parse
import re
import os
import yaml
from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value.endswith('.yaml'):
                    self.links.append(value)

base_url = 'https://auth.simia.pro/data/'
out_dir = 'simia_data_dump'
os.makedirs(out_dir, exist_ok=True)

print("Fetching directory index...")
req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

parser = LinkParser()
parser.feed(html)
links = parser.links
print(f"Found {len(links)} yaml files.")

for link in links:
    url = urllib.parse.urljoin(base_url, link)
    filename = os.path.basename(urllib.parse.urlparse(url).path)
    out_path = os.path.join(out_dir, filename)
    print(f"Downloading {filename}...")
    try:
        req_dl = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_dl) as response, open(out_path, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("Downloading web_rotations.yaml community links...")
try:
    with open(os.path.join(out_dir, 'web_rotations.yaml'), 'r', encoding='utf-8') as f:
        web_rotations = yaml.safe_load(f)
        for rot in web_rotations.get('rotations', []):
            url = rot.get('url')
            if url:
                # Some community URLs carry raw spaces in the path; urlopen rejects those.
                parsed = urllib.parse.urlsplit(url)
                url = urllib.parse.urlunsplit(parsed._replace(
                    path=urllib.parse.quote(parsed.path, safe='/%')))
                filename = "community_" + re.sub(r'[^a-zA-Z0-9_]', '_', rot.get('name', 'unnamed')) + ".yaml"
                out_path = os.path.join(out_dir, filename)
                print(f"Downloading {filename}...")
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(out_path, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    print(f"Failed to download {filename}: {e}")
except Exception as e:
    print(f"Could not process web_rotations.yaml: {e}")

print("Done downloading.")

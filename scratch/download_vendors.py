"""
Script for downloading frontend vendor libraries for offline support.
"""
import os
import urllib.request

VENDOR_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "presentation", "web", "assets", "vendor")
os.makedirs(VENDOR_DIR, exist_ok=True)

FILES_TO_DOWNLOAD = {
    "leaflet.js": "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
    "leaflet.css": "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
    "apexcharts.min.js": "https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js",
    "lucide.min.js": "https://unpkg.com/lucide@latest/dist/umd/lucide.min.js",
}

print(f"Downloading vendor libraries to {VENDOR_DIR}...")
for name, url in FILES_TO_DOWNLOAD.items():
    dest_path = os.path.join(VENDOR_DIR, name)
    print(f"Downloading {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully saved {name} ({os.path.getsize(dest_path)} bytes)")
    except Exception as e:
        print(f"Failed to download {name}: {e}")

print("Done downloading vendor assets.")

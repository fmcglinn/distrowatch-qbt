import requests
import feedparser
import qbittorrentapi
import os
import libtorrent as lt
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read qBittorrent credentials and settings from .env
QBIT_HOST = os.getenv("QBIT_HOST")
QBIT_USER = os.getenv("QBIT_USER")
QBIT_PASS = os.getenv("QBIT_PASS")
CATEGORY_NAME = os.getenv("CATEGORY_NAME", "permaseed")

# DistroWatch RSS feed
DISTROWATCH_RSS = "https://distrowatch.com/news/torrents.xml"

# Directory to store downloaded torrents
TORRENT_DIR = "torrents"
os.makedirs(TORRENT_DIR, exist_ok=True)

# Custom User-Agent string (Mimics Firefox on Linux)
HEADERS = {
    "User-Agent": "Wget",
    "Referer": "https://distrowatch.com/",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# Initialize qBittorrent connection
try:
    qb = qbittorrentapi.Client(host=QBIT_HOST, username=QBIT_USER, password=QBIT_PASS)
    qb.auth_log_in()
    print("[+] Connected to qBittorrent!")

    # Ensure category exists
    if CATEGORY_NAME not in qb.torrent_categories.categories.keys():
        qb.torrent_categories_add(name=CATEGORY_NAME)
        print(f"[+] Created qBittorrent category: {CATEGORY_NAME}")

except qbittorrentapi.exceptions.LoginFailed as e:
    print(f"[-] qBittorrent login failed: {e}")
    exit(1)

def fetch_latest_torrents():
    """Fetch the latest torrents from DistroWatch RSS feed."""
    feed = feedparser.parse(DISTROWATCH_RSS)
    torrents = []

    if not feed.entries:
        print("[-] No torrents found in the RSS feed.")
        return torrents

    for entry in feed.entries:
        title = entry.get("title", "Unknown Linux Distro")
        link = entry.get("link")  # This should be the direct torrent link

        if link and link.endswith(".torrent"):  # Ensure it's a valid torrent file
            torrents.append({"title": title, "link": link})
    
    return torrents

def get_torrent_name(torrent_file):
    """Extracts the torrent name from a .torrent file."""
    try:
        info = lt.torrent_info(torrent_file)  # Correct way to load the torrent file
        return info.name()

    except Exception as e:
        print(f"[-] Failed to extract name from {torrent_file}: {e}")
        return None

def is_torrent_added(torrent_name):
    """Check if a torrent with the same name already exists in qBittorrent."""
    try:
        torrents = qb.torrents_info()
        existing_names = {torrent.name.lower() for torrent in torrents}  # Normalize names

        # Strip '.torrent' from the input name
        torrent_name = torrent_name.replace(".torrent", "")

        if torrent_name.lower() in existing_names:
            print(f"[~] Torrent already exists in qBittorrent: {torrent_name}")
            return True

        return False

    except Exception as e:
        print(f"[-] Failed to check existing torrents: {e}")
        return False

def download_torrent(torrent):
    """Download the torrent file locally."""
    title = torrent["title"]
    link = torrent["link"]
    filename = os.path.join(TORRENT_DIR, title.replace(" ", "_"))

    if os.path.exists(filename):
        print(f"[~] Torrent file already downloaded: {filename}")
        return filename  # Return existing file

    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        
        response = session.get(link, timeout=10)
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"[+] Downloaded: {filename}")
        return filename

    except requests.RequestException as e:
        print(f"[-] Failed to download {title}: {e}")
        return None

def upload_torrent_to_qbittorrent(torrent_file):
    """Upload the torrent file to qBittorrent."""
    if not torrent_file or not os.path.exists(torrent_file):
        print(f"[-] Torrent file missing: {torrent_file}")
        return

    try:
        with open(torrent_file, "rb") as f:
            qb.torrents_add(torrent_files=f, category=CATEGORY_NAME)
            print(f"[+] Uploaded to qBittorrent: {torrent_file}")

    except Exception as e:
        print(f"[-] Failed to upload {torrent_file}: {e}")

# Fetch and process torrents
latest_torrents = fetch_latest_torrents()

if latest_torrents:
    for torrent in latest_torrents:
        torrent_file = download_torrent(torrent)

        if not torrent_file:
            continue
        
        # Extract real torrent name
        torrent_name = get_torrent_name(torrent_file)
        
        if not torrent_name:
            print(f"[-] Skipping, missing torrent name: {torrent_file}")
            continue
        
        if is_torrent_added(torrent_name):
            continue
        
        upload_torrent_to_qbittorrent(torrent_file)

else:
    print("[-] No new torrents to add.")

print("[+] Done checking for new Linux ISOs.")


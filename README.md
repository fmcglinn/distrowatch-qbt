# distrowatch-qbt


This script automatically fetches the latest Linux distribution torrents from DistroWatch's RSS feed, downloads them, and adds them to **qBittorrent** using its Web API.

## Features
 Fetches the latest Linux torrents from DistroWatch RSS.
 Downloads `.torrent` files and uploads them to **qBittorrent**.
 Uses **a virtual environment** for better package management.
 **Prevents duplicate torrents** by checking existing ones in qBittorrent.
 Can run automatically via **cron** or **systemd**.

---

## Installation & Setup

### 1. Clone the Repository
```bash
cd /opt/
git clone https://github.com/fmcglinn/distrowatch-qbt.git
cd distrowatch-qbt
```

### 2. Run init script
```bash
bash init.sh
```

### 3. Create a `.env` File
Copy example `.env` file in the project directory to store qBittorrent credentials, modify acordingly:
```bash
cp .env.example .env
```
### 4. Run the Script
```bash
bash run.sh
```

---

## Automating with Cron

```bash
cd /etc/cron.daily/
ln -s /opt/distrowatch-qbt/run.sh distrowatch-qbt
```


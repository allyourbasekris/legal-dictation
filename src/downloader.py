import requests
from pathlib import Path


def _download_progress(url, dest, callback=None):
    dest = Path(dest)
    if dest.exists():
        if callback:
            callback(1.0)
        return
    tmp = dest.with_suffix(".part")
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(tmp, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if callback and total:
                callback(downloaded / total)
    tmp.rename(dest)

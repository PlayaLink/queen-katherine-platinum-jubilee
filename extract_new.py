#!/usr/bin/env python3
"""
Extract specific new messages by subject and save photos + text.
"""

import base64
import os
import pickle
import re
import html as html_mod
from email.utils import parseaddr
from pathlib import Path

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DIR = Path(__file__).parent
TOKEN = DIR / "token.pickle"
PHOTOS_DIR = DIR / "photos"

IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif",
    "image/heic": ".heic", "image/heif": ".heif", "image/webp": ".webp",
    "image/tiff": ".tiff",
}

def get_gmail_service():
    with open(TOKEN, "rb") as f:
        creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN, "wb") as f:
                pickle.dump(creds, f)
    return build("gmail", "v1", credentials=creds)


def extract_body(payload):
    mime = payload.get("mimeType", "")
    if mime == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    parts = payload.get("parts", [])
    plain = ""
    html_body = ""
    for part in parts:
        part_mime = part.get("mimeType", "")
        if part_mime == "text/plain" and part.get("body", {}).get("data"):
            plain = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        elif part_mime == "text/html" and part.get("body", {}).get("data"):
            raw = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
            raw = re.sub(r"</(p|div|tr|li)>", "\n", raw, flags=re.IGNORECASE)
            raw = re.sub(r"<[^>]+>", "", raw)
            html_body = html_mod.unescape(raw).strip()
        elif part_mime.startswith("multipart/"):
            nested = extract_body(part)
            if nested:
                plain = plain or nested
    return plain if plain else html_body


def sanitize_filename(name):
    name = name.replace('"', "").replace("'", "").strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def download_photos(service, msg, safe_name):
    parts = msg["payload"].get("parts", [])
    all_parts = list(parts)
    for part in parts:
        if part.get("mimeType", "").startswith("multipart/"):
            all_parts.extend(part.get("parts", []))

    idx = 0
    for part in all_parts:
        mime = part.get("mimeType", "")
        filename = part.get("filename", "")
        att_id = part.get("body", {}).get("attachmentId")
        if not att_id:
            continue
        if mime in IMAGE_EXTENSIONS or (filename and any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS.values())):
            size = part.get("body", {}).get("size", 0)
            if size < 5000:
                continue
            ext = IMAGE_EXTENSIONS.get(mime, os.path.splitext(filename)[1] if filename else ".jpg")
            suffix = f"_{idx + 1}" if idx > 0 else ""
            photo_filename = f"{safe_name}{suffix}{ext}"
            photo_path = PHOTOS_DIR / photo_filename

            att = service.users().messages().attachments().get(
                userId="me", messageId=msg["id"], id=att_id
            ).execute()
            data = base64.urlsafe_b64decode(att["data"])
            with open(photo_path, "wb") as f:
                f.write(data)
            print(f"  📷 Saved: photos/{photo_filename} ({len(data) // 1024} KB)")
            idx += 1
    return idx


def main():
    PHOTOS_DIR.mkdir(exist_ok=True)
    service = get_gmail_service()

    # Search for the two new messages
    searches = [
        ('subject:"Qween Katherine" from:candace', "Candace Magoski"),
        ('subject:"Memories of Katherine" from:sandra', "Sandra F"),
    ]

    for query, expected_name in searches:
        print(f"\n{'=' * 50}")
        print(f"Searching: {query}")
        results = service.users().messages().list(userId="me", q=query, maxResults=5).execute()
        messages = results.get("messages", [])

        if not messages:
            print(f"  No messages found for {expected_name}")
            continue

        for m_ref in messages:
            msg = service.users().messages().get(userId="me", id=m_ref["id"], format="full").execute()
            headers = msg["payload"].get("headers", [])

            sender = ""
            for h in headers:
                if h["name"].lower() == "from":
                    name, addr = parseaddr(h["value"])
                    sender = name or addr
                    break

            print(f"\nFrom: {sender}")
            safe_name = sanitize_filename(sender)

            # Extract body
            body = extract_body(msg["payload"])
            print(f"\n--- MESSAGE TEXT ---")
            print(body[:1000] if body else "(no text body)")
            print(f"--- END ---\n")

            # Download photos
            count = download_photos(service, msg, safe_name)
            print(f"  Total photos: {count}")


if __name__ == "__main__":
    main()

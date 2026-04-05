#!/usr/bin/env python3
"""
Extract new submissions from the last 2 weeks for Katherine's 70th birthday site.
Downloads photos and prints full message text.
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

    # Target the specific new submission messages by their message IDs / subjects
    searches = [
        # Anna Hansen (forwarded by Brontë)
        ('subject:"Katherine\'s 70th Bday Photo/Memory Book" from:bronte after:2026/03/22 before:2026/03/23', "Anna_Hansen"),
        # Marilyn Shadaram (forwarded by Jordan Nelson)
        ('subject:"Katherine note/pic"', "Marilyn_Shadaram"),
        # Lynne Orr text (forwarded by Jordan Nelson)
        ('subject:"The three photos sent from me"', "Lynne_Orr"),
        # Lynne/John Orr photo (forwarded by Jordan Nelson)
        ('subject:"Katherine England\'s 70th bday"', "John_Orr"),
        # Rebecca England - baby photo
        ('subject:"Katherine\'s baby photo" from:rebecca', "Katherine_baby"),
        # Amelia England (forwarded by Brontë)
        ('subject:"Katherine\'s 70th Bday Photo/Memory Book" from:bronte after:2026/03/23 before:2026/03/24', "Amelia_England"),
        # Amelia photo (separate email from Brontë)
        ('subject:"Katherine\'s 70th Bday Photo/Memory Book" from:bronte "Photo for Amelia"', "Amelia_England_photo"),
        # Rebecca England - Katherine & Zombies
        ('subject:"Katherine & Zombies" from:rebecca', "Rebecca_England_zombies"),
        # Rebecca England - Jennifer's early memories
        ('subject:"Jennifer\'s early memories" from:rebecca', "Jennifer_England"),
    ]

    for query, label in searches:
        print(f"\n{'=' * 60}")
        print(f"🔍 {label}: {query}")
        results = service.users().messages().list(userId="me", q=query, maxResults=5).execute()
        messages = results.get("messages", [])

        if not messages:
            print(f"  ❌ No messages found")
            continue

        for m_ref in messages:
            msg = service.users().messages().get(userId="me", id=m_ref["id"], format="full").execute()
            headers = msg["payload"].get("headers", [])

            sender = ""
            subject = ""
            date = ""
            for h in headers:
                name = h["name"].lower()
                if name == "from":
                    n, addr = parseaddr(h["value"])
                    sender = n or addr
                elif name == "subject":
                    subject = h["value"]
                elif name == "date":
                    date = h["value"]

            print(f"\n  From: {sender}")
            print(f"  Date: {date}")
            print(f"  Subject: {subject}")

            # Extract and print body
            body = extract_body(msg["payload"])
            if body:
                print(f"\n  --- MESSAGE TEXT ---")
                print(body[:3000])
                print(f"  --- END ---")
            else:
                print(f"  (no text body)")

            # Download photos
            safe_name = sanitize_filename(label)
            count = download_photos(service, msg, safe_name)
            if count:
                print(f"  Total photos downloaded: {count}")
            else:
                print(f"  No photo attachments")

    print(f"\n{'=' * 60}")
    print("Done! Check the photos/ directory for new images.")


if __name__ == "__main__":
    main()

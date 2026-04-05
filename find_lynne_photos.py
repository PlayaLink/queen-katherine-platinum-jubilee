#!/usr/bin/env python3
"""Search for all emails from Lynne Orr that might contain photos."""

import base64
import os
import pickle
import re
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


def list_attachments(payload, depth=0):
    """Recursively list all attachments in a message."""
    parts = payload.get("parts", [])
    attachments = []
    for part in parts:
        mime = part.get("mimeType", "")
        filename = part.get("filename", "")
        att_id = part.get("body", {}).get("attachmentId")
        size = part.get("body", {}).get("size", 0)
        if att_id and filename:
            attachments.append({
                "filename": filename,
                "mime": mime,
                "size": size,
                "att_id": att_id,
            })
        if mime.startswith("multipart/"):
            attachments.extend(list_attachments(part, depth + 1))
    return attachments


def main():
    PHOTOS_DIR.mkdir(exist_ok=True)
    service = get_gmail_service()

    queries = [
        'from:lynne_orr',
        'from:lynne orr',
        'from:jorr@fullcoll.edu',
        'lynne orr has:attachment',
        'subject:"katherine" from:lynne',
        'subject:"orr" has:attachment',
    ]

    seen_ids = set()
    all_messages = []

    for q in queries:
        results = service.users().messages().list(userId="me", q=q, maxResults=50).execute()
        for m in results.get("messages", []):
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                all_messages.append(m["id"])

    print(f"Found {len(all_messages)} unique messages across all queries\n")

    for msg_id in all_messages:
        msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        headers = msg["payload"].get("headers", [])

        subject = ""
        from_header = ""
        date_header = ""
        for h in headers:
            if h["name"].lower() == "subject":
                subject = h["value"]
            elif h["name"].lower() == "from":
                from_header = h["value"]
            elif h["name"].lower() == "date":
                date_header = h["value"]

        attachments = list_attachments(msg["payload"])
        image_attachments = [a for a in attachments if a["mime"] in IMAGE_EXTENSIONS or
                            any(a["filename"].lower().endswith(ext) for ext in IMAGE_EXTENSIONS.values())]

        print(f"From: {from_header}")
        print(f"Date: {date_header}")
        print(f"Subject: {subject}")
        print(f"Attachments: {len(attachments)} total, {len(image_attachments)} images")
        for a in image_attachments:
            print(f"  📷 {a['filename']} ({a['mime']}, {a['size'] // 1024} KB)")
        print("-" * 60)

        # Download any image attachments
        for i, a in enumerate(image_attachments):
            if a["size"] < 5000:
                print(f"  Skipping {a['filename']} (too small, likely inline icon)")
                continue
            ext = IMAGE_EXTENSIONS.get(a["mime"], os.path.splitext(a["filename"])[1] if a["filename"] else ".jpg")
            suffix = f"_{i + 1}" if i > 0 else ""
            safe_name = f"Lynne_Orr{suffix}{ext}"
            photo_path = PHOTOS_DIR / safe_name

            if photo_path.exists():
                print(f"  Already exists: {safe_name}")
                continue

            att = service.users().messages().attachments().get(
                userId="me", messageId=msg_id, id=a["att_id"]
            ).execute()
            data = base64.urlsafe_b64decode(att["data"])
            with open(photo_path, "wb") as f:
                f.write(data)
            print(f"  ✅ Saved: photos/{safe_name} ({len(data) // 1024} KB)")


if __name__ == "__main__":
    main()

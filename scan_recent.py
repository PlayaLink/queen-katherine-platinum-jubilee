#!/usr/bin/env python3
"""
Broad scan of recent emails for any Katherine-related memories
that may have come in outside the original thread.
"""

import base64
import pickle
import re
from email.utils import parseaddr
from pathlib import Path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

DIR = Path(__file__).parent
TOKEN = DIR / "token.pickle"

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
            import html
            raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
            raw = re.sub(r"</(p|div|tr|li)>", "\n", raw, flags=re.IGNORECASE)
            raw = re.sub(r"<[^>]+>", "", raw)
            html_body = html.unescape(raw).strip()
        elif part_mime.startswith("multipart/"):
            nested = extract_body(part)
            if nested:
                plain = plain or nested
    return plain if plain else html_body


def has_attachments(payload):
    parts = payload.get("parts", [])
    for part in parts:
        if part.get("filename") and part.get("body", {}).get("attachmentId"):
            return True
        if part.get("mimeType", "").startswith("multipart/"):
            if has_attachments(part):
                return True
    return False


def main():
    service = get_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    my_email = profile["emailAddress"].lower()
    print(f"Logged in as: {my_email}\n")

    # Search broadly: last 10 days, anything mentioning katherine/birthday/memory/photo
    date_cutoff = (datetime.now() - timedelta(days=10)).strftime("%Y/%m/%d")

    queries = [
        f"after:{date_cutoff} katherine",
        f"after:{date_cutoff} birthday photo memory",
        f"after:{date_cutoff} photobook",
        f"after:{date_cutoff} subject:katherine",
        f"after:{date_cutoff} 70th birthday",
    ]

    # Also get IDs from the original thread to exclude
    original_results = service.users().messages().list(
        userId="me",
        q='subject:"A Special Request for Katherine\'s 70th Birthday"',
        maxResults=500,
    ).execute()
    known_ids = {m["id"] for m in original_results.get("messages", [])}
    print(f"Already processed {len(known_ids)} messages from original thread\n")

    # Collect unique message IDs from all queries
    candidate_ids = set()
    for q in queries:
        results = service.users().messages().list(userId="me", q=q, maxResults=100).execute()
        for m in results.get("messages", []):
            if m["id"] not in known_ids:
                candidate_ids.add(m["id"])

    print(f"Found {len(candidate_ids)} candidate messages outside the original thread\n")
    print("=" * 70)

    for msg_id in sorted(candidate_ids):
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

        name, addr = parseaddr(from_header)
        if addr.lower() == my_email:
            continue  # skip sent messages

        body = extract_body(msg["payload"])
        snippet = (body or "")[:300].replace("\n", " ").strip()
        attachments = has_attachments(msg["payload"])

        print(f"\nFrom: {name or addr}")
        print(f"Date: {date_header}")
        print(f"Subject: {subject}")
        print(f"Has attachments: {'YES' if attachments else 'no'}")
        print(f"Preview: {snippet}...")
        print("-" * 70)


if __name__ == "__main__":
    main()

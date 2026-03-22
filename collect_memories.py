#!/usr/bin/env python3
"""
Collect photos and memories from Gmail replies to Katherine's 70th birthday email.

Outputs:
  - photos/<SenderName>.<ext>      one file per attachment
  - memories.txt                   formatted text for Shutterfly photobook
"""

import base64
import os
import pickle
import re
import html
from email.utils import parseaddr
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Config ──────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
DIR = Path(__file__).parent
GOOGLE_DIR = DIR.parent / "google"
CREDENTIALS = GOOGLE_DIR / "credentials.json"
TOKEN = DIR / "token.pickle"  # separate token with read scope
PHOTOS_DIR = DIR / "photos"
MEMORIES_FILE = DIR / "memories.txt"

SUBJECT_QUERY = 'subject:"A Special Request for Katherine\'s 70th Birthday"'
IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/heic": ".heic",
    "image/heif": ".heif",
    "image/webp": ".webp",
    "image/tiff": ".tiff",
}


# ── Auth ────────────────────────────────────────────────────────────
def get_gmail_service():
    creds = None
    if TOKEN.exists():
        with open(TOKEN, "rb") as f:
            creds = pickle.load(f)

    # Check if existing token has the scopes we need
    if creds and hasattr(creds, "scopes") and not set(SCOPES).issubset(creds.scopes or set()):
        print("Token missing required scopes — re-authenticating...")
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


# ── Helpers ─────────────────────────────────────────────────────────
def sender_display_name(headers):
    """Extract a clean display name from the From header."""
    for h in headers:
        if h["name"].lower() == "from":
            name, addr = parseaddr(h["value"])
            if name:
                return name.strip()
            # Fall back to the part before @
            return addr.split("@")[0].strip()
    return "Unknown"


def sanitize_filename(name):
    """Convert a display name to a safe filename."""
    # Remove quotes and extra whitespace
    name = name.replace('"', "").replace("'", "").strip()
    # Replace spaces with underscores, remove non-alphanumeric chars
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def strip_html(text):
    """Rough HTML-to-text conversion."""
    # Replace <br> and block-level tags with newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|tr|li)>", "\n", text, flags=re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()


def extract_body(payload):
    """Recursively extract the best text body from a message payload."""
    mime = payload.get("mimeType", "")

    # Simple single-part message
    if mime == "text/plain" and "body" in payload and payload["body"].get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    # Multipart — prefer text/plain, fall back to text/html
    parts = payload.get("parts", [])
    plain = ""
    html_body = ""
    for part in parts:
        part_mime = part.get("mimeType", "")
        if part_mime == "text/plain" and part.get("body", {}).get("data"):
            plain = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        elif part_mime == "text/html" and part.get("body", {}).get("data"):
            html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        elif part_mime.startswith("multipart/"):
            nested = extract_body(part)
            if nested:
                plain = plain or nested

    if plain:
        return plain
    if html_body:
        return strip_html(html_body)
    return ""


def trim_quoted_reply(body):
    """Remove the quoted original message from a reply."""
    # Common reply markers (on the line itself, or preceded by blank lines)
    markers = [
        r"^>+\s*On .+ wrote:",                      # "> On Mon, Mar 17 ... wrote:"
        r"^On .+wrote:\s*$",                         # "On Mon, Mar 17, 2025 ... wrote:"
        r"^-{2,}\s*Original Message\s*-{2,}",       # "--- Original Message ---"
        r"^_{2,}",                                   # "______" (Outlook)
        r"^From:\s+",                                # "From: Jordan ..."
        r"^Sent from my ",                           # "Sent from my iPhone"
        r"^Get Outlook for ",                        # Outlook mobile
        r"^>+\s*Hello friends and family",           # Quoted original body
        r"^>+\s*As you well know",                   # Quoted original body variant
    ]
    lines = body.split("\n")
    cut_at = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        for marker in markers:
            if re.match(marker, stripped, re.IGNORECASE):
                cut_at = i
                break
        if cut_at < len(lines):
            break

    # Also strip trailing quote blocks (lines starting with >)
    result_lines = lines[:cut_at]
    while result_lines and result_lines[-1].strip().startswith(">"):
        result_lines.pop()

    trimmed = "\n".join(result_lines).strip()
    # Remove trailing email signatures (email, phone patterns at the very end)
    sig_lines = trimmed.split("\n")
    while sig_lines:
        last = sig_lines[-1].strip()
        # Remove lines that are just email addresses, phone numbers, or empty
        if not last:
            sig_lines.pop()
        elif re.match(r"^[\w.+-]+@[\w.-]+\.\w+$", last):
            sig_lines.pop()
        elif re.match(r"^[\d\.\-\(\)\s]{7,}$", last):
            sig_lines.pop()
        elif last.startswith("--"):
            sig_lines.pop()
        else:
            break

    trimmed = "\n".join(sig_lines).strip()
    return trimmed if trimmed else body.strip()


# ── Main ────────────────────────────────────────────────────────────
def main():
    PHOTOS_DIR.mkdir(exist_ok=True)

    service = get_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    print(f"Logged in as: {profile['emailAddress']}\n")

    # Search for all messages in threads matching the subject
    print(f"Searching: {SUBJECT_QUERY}")
    results = service.users().messages().list(
        userId="me", q=SUBJECT_QUERY, maxResults=500
    ).execute()
    message_ids = results.get("messages", [])
    print(f"Found {len(message_ids)} messages\n")

    if not message_ids:
        print("No replies found. Check the subject line or try a broader search.")
        return

    my_email = profile["emailAddress"].lower()
    memories = []
    photo_count = 0
    seen_message_ids = set()  # dedupe across thread expansions
    saved_photo_names = set()  # track photos already saved to avoid overwriting

    for msg_ref in message_ids:
        if msg_ref["id"] in seen_message_ids:
            continue
        seen_message_ids.add(msg_ref["id"])
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = msg["payload"].get("headers", [])
        sender_name = sender_display_name(headers)

        # Skip messages sent by me (the original outgoing email)
        from_addr = ""
        for h in headers:
            if h["name"].lower() == "from":
                _, from_addr = parseaddr(h["value"])
                break
        if from_addr.lower() == my_email:
            continue

        safe_name = sanitize_filename(sender_name)
        print(f"Processing reply from: {sender_name}")

        # ── Extract memory text ──
        body = extract_body(msg["payload"])
        memory_text = trim_quoted_reply(body)

        # Only keep messages that are actual memory submissions — skip
        # logistical replies ("I'll send something soon", "My pleasure!", etc.)
        # A real memory is typically at least ~80 chars of substantive text.
        clean_text = re.sub(r"\s+", " ", memory_text).strip()
        is_substantive = len(clean_text) > 80
        if memory_text and is_substantive:
            memories.append({"name": sender_name, "text": memory_text})

        # ── Download photo attachments ──
        parts = msg["payload"].get("parts", [])
        # Also check nested parts (multipart/mixed > multipart/alternative + attachments)
        all_parts = list(parts)
        for part in parts:
            if part.get("mimeType", "").startswith("multipart/"):
                all_parts.extend(part.get("parts", []))

        sender_photo_idx = 0
        for part in all_parts:
            mime = part.get("mimeType", "")
            filename = part.get("filename", "")
            att_id = part.get("body", {}).get("attachmentId")

            if not att_id:
                continue

            # Accept image attachments (skip tiny inline signature images)
            if mime in IMAGE_EXTENSIONS or (filename and any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS.values())):
                size = part.get("body", {}).get("size", 0)
                if size < 5000:
                    # Likely a tiny inline signature image — skip
                    continue

                ext = IMAGE_EXTENSIONS.get(mime, os.path.splitext(filename)[1] if filename else ".jpg")
                suffix = f"_{sender_photo_idx + 1}" if sender_photo_idx > 0 else ""
                photo_filename = f"{safe_name}{suffix}{ext}"

                # Skip if we already saved this exact filename (duplicate thread)
                if photo_filename in saved_photo_names:
                    continue
                saved_photo_names.add(photo_filename)

                photo_path = PHOTOS_DIR / photo_filename

                att = service.users().messages().attachments().get(
                    userId="me", messageId=msg_ref["id"], id=att_id
                ).execute()
                data = base64.urlsafe_b64decode(att["data"])

                with open(photo_path, "wb") as f:
                    f.write(data)

                print(f"  📷 Saved: photos/{photo_filename} ({len(data) // 1024} KB)")
                sender_photo_idx += 1
                photo_count += 1

    # ── Write formatted memories file ──
    with open(MEMORIES_FILE, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("  KATHERINE'S 70TH BIRTHDAY — MEMORIES FROM LOVED ONES\n")
        f.write("=" * 60 + "\n\n")

        for i, m in enumerate(memories, 1):
            f.write(f"── {m['name']} {'─' * (50 - len(m['name']))}──\n\n")
            f.write(f"{m['text']}\n\n\n")

        f.write("=" * 60 + "\n")
        f.write(f"  {len(memories)} memories collected\n")
        f.write("=" * 60 + "\n")

    print(f"\n{'=' * 50}")
    print(f"  Done!")
    print(f"  📝 {len(memories)} memories → {MEMORIES_FILE.name}")
    print(f"  📷 {photo_count} photos → photos/")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()

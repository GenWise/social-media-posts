#!/usr/bin/env python3
"""
Post text (+ optional image) to the GenWise LinkedIn page.

Usage:
    python3 post_to_linkedin.py                        # interactive prompt
    python3 post_to_linkedin.py --text "Hello world"   # text only
    python3 post_to_linkedin.py --text "..." --image /path/to/image.jpg

@mentions in post text:
    Use the format @[Display Name](urn:li:organization:XXXXX) for company mentions.
    e.g. "Attended @[Shiv Nadar School](urn:li:organization:3791226) last year"
    The script parses these, builds the annotation payload, and sends proper tagged mentions.

    Known URNs:
        Shiv Nadar School   urn:li:organization:3791226
        GenWise             urn:li:organization:42797325

Token refresh is handled automatically.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

ORG_URN      = "urn:li:organization:42797325"
API_BASE     = "https://api.linkedin.com/v2"
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
REFRESH_TOKEN      = os.getenv("LINKEDIN_REFRESH_TOKEN")
CLIENT_ID          = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET      = os.getenv("LINKEDIN_CLIENT_SECRET")


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------

def refresh_access_token():
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        token_data = json.loads(resp.read())

    new_token = token_data["access_token"]

    # Upsert back into ~/.env
    import re
    env_path = os.path.expanduser("~/.env")
    with open(env_path, "r") as f:
        content = f.read()
    if re.search(r"^LINKEDIN_ACCESS_TOKEN=.*$", content, re.MULTILINE):
        content = re.sub(r"^LINKEDIN_ACCESS_TOKEN=.*$", f"LINKEDIN_ACCESS_TOKEN={new_token}", content, flags=re.MULTILINE)
    else:
        content += f"\nLINKEDIN_ACCESS_TOKEN={new_token}"
    with open(env_path, "w") as f:
        f.write(content)

    print(f"  Access token refreshed (expires in {token_data.get('expires_in', '?')}s)")
    return new_token


def get_token():
    """Return access token, refreshing if needed."""
    token = ACCESS_TOKEN
    if not token:
        print("No LINKEDIN_ACCESS_TOKEN in ~/.env — run linkedin_auth.py first")
        sys.exit(1)
    return token


# ---------------------------------------------------------------------------
# Media upload (v2 assets API) — image and video
# ---------------------------------------------------------------------------

def upload_media(media_path: str, token: str) -> tuple[str, str]:
    """
    Upload image or video and return (asset_urn, media_category).
    media_category is 'IMAGE' or 'VIDEO' for the ugcPost payload.
    """
    import time

    ext = os.path.splitext(media_path)[1].lower()
    is_video = ext in ('.mp4', '.mov', '.avi', '.mkv', '.webm')

    recipe = "urn:li:digitalmediaRecipe:feedshare-video" if is_video else "urn:li:digitalmediaRecipe:feedshare-image"
    media_category = "VIDEO" if is_video else "IMAGE"

    # 1. Register upload
    register_payload = json.dumps({
        "registerUploadRequest": {
            "recipes": [recipe],
            "owner": ORG_URN,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/assets?action=registerUpload",
        data=register_payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        reg = json.loads(resp.read())

    upload_url = reg["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn  = reg["value"]["asset"]

    # 2. PUT the file bytes
    with open(media_path, "rb") as f:
        file_bytes = f.read()

    if is_video:
        mime = "video/mp4"
    else:
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif"}.get(ext.lstrip("."), "image/jpeg")

    put_req = urllib.request.Request(
        upload_url,
        data=file_bytes,
        headers={"Authorization": f"Bearer {token}", "Content-Type": mime},
        method="PUT",
    )
    with urllib.request.urlopen(put_req) as resp:
        pass  # 201 No Content

    # 3. For video, poll until AVAILABLE
    if is_video:
        print(f"  Video uploaded, waiting for processing...", end="", flush=True)
        for _ in range(30):
            time.sleep(5)
            status_req = urllib.request.Request(
                f"{API_BASE}/assets/{asset_urn.split(':')[-1]}",
                headers={"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0"}
            )
            try:
                with urllib.request.urlopen(status_req) as r:
                    data = json.loads(r.read())
                    state = data.get("recipes", [{}])[0].get("status", "")
                    if state == "AVAILABLE":
                        print(" ready.")
                        break
                    print(".", end="", flush=True)
            except Exception:
                print(".", end="", flush=True)

    print(f"  {'Video' if is_video else 'Image'} uploaded: {asset_urn}")
    return asset_urn, media_category


# ---------------------------------------------------------------------------
# First comment (for URL)
# ---------------------------------------------------------------------------

def post_first_comment(post_id: str, comment_text: str, token: str) -> dict:
    """Post a comment on a ugcPost — used to add URL as first comment."""
    payload = json.dumps({
        "actor": ORG_URN,
        "object": post_id,
        "message": {"text": comment_text},
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/socialActions/{urllib.parse.quote(post_id, safe='')}/comments",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return {"success": True, "data": json.loads(resp.read()) if resp.length else {}}
    except urllib.error.HTTPError as e:
        return {"success": False, "error": e.read().decode()}


# ---------------------------------------------------------------------------
# Mention parsing
# ---------------------------------------------------------------------------

def parse_mentions(text: str) -> tuple[str, list]:
    """
    Parse @[Display Name](urn:li:organization:XXXXX) patterns from text.
    Returns (clean_text, annotations) where annotations is a list of
    LinkedIn TextAnnotation dicts ready for the API payload.

    Example input:  "Hi @[Shiv Nadar School](urn:li:organization:3791226) students"
    Example output: ("Hi Shiv Nadar School students", [{...annotation...}])
    """
    import re

    annotations = []
    pattern = re.compile(r'@\[([^\]]+)\]\((urn:li:[^\)]+)\)')

    # Build clean text and collect annotation positions
    clean_text = text
    offset_delta = 0  # track how pattern length differs from display name length

    for m in pattern.finditer(text):
        display_name = m.group(1)
        entity_urn   = m.group(2)

        # Position in the *clean* text (after prior substitutions)
        start_in_original = m.start()
        # Count characters removed by prior substitutions
        prior_matches = list(pattern.finditer(text[:start_in_original]))
        prior_delta = sum(
            len(pm.group(0)) - len(pm.group(1)) for pm in prior_matches
        )
        start = start_in_original - prior_delta
        end   = start + len(display_name)

        annotations.append({
            "start": start,
            "length": len(display_name),
            "value": {
                "com.linkedin.common.CompanyAttributedEntity": {
                    "company": entity_urn
                }
            }
        })

    # Strip the @[...](urn) syntax, keep only the display name
    clean_text = pattern.sub(lambda m: m.group(1), text)
    return clean_text, annotations


# ---------------------------------------------------------------------------
# Post creation
# ---------------------------------------------------------------------------

def create_post(text: str, token: str, media_path: str = None) -> dict:
    """Create an org post with optional image or video. Returns API response dict."""

    # Parse @mentions
    clean_text, annotations = parse_mentions(text)

    share_commentary = {"text": clean_text}
    if annotations:
        share_commentary["attributes"] = annotations

    asset_urn = None
    media_category = "NONE"
    if media_path:
        print(f"  Uploading media: {media_path}")
        asset_urn, media_category = upload_media(media_path, token)

    if asset_urn:
        payload = {
            "author": ORG_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": share_commentary,
                    "shareMediaCategory": media_category,
                    "media": [{
                        "status": "READY",
                        "description": {"text": ""},
                        "media": asset_urn,
                        "title": {"text": ""},
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
    else:
        payload = {
            "author": ORG_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": share_commentary,
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

    req = urllib.request.Request(
        f"{API_BASE}/ugcPosts",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            post_id = resp.headers.get("x-restli-id", "")
            return {"success": True, "post_id": post_id}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 401:
            print("  Token expired — refreshing...")
            new_token = refresh_access_token()
            return create_post(text, new_token, media_path)
        return {"success": False, "status_code": e.code, "error": body}



# ---------------------------------------------------------------------------
# Reshare
# ---------------------------------------------------------------------------

def create_reshare(post_urn: str, commentary: str, token: str) -> dict:
    """Reshare an existing LinkedIn post with optional commentary."""

    clean_text, annotations = parse_mentions(commentary)

    share_commentary = {"text": clean_text}
    if annotations:
        share_commentary["attributes"] = annotations

    payload = {
        "author": ORG_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": share_commentary,
                "shareMediaCategory": "NONE",
                "resharedEntity": post_urn,
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    req = urllib.request.Request(
        f"{API_BASE}/ugcPosts",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            post_id = resp.headers.get("x-restli-id", "")
            return {"success": True, "post_id": post_id}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 401:
            print("  Token expired — refreshing...")
            new_token = refresh_access_token()
            return create_reshare(post_urn, commentary, new_token)
        return {"success": False, "status_code": e.code, "error": body}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Post to GenWise LinkedIn page")
    parser.add_argument("--text",    help="Post text")
    parser.add_argument("--media",   help="Path to image or video file (optional)")
    parser.add_argument("--comment", help="First comment text (e.g. URL). Posted immediately after.")
    parser.add_argument("--reshare", help="LinkedIn post URN to reshare (e.g. urn:li:ugcPost:XXXXX)")
    # Legacy --image still works
    parser.add_argument("--image",   help=argparse.SUPPRESS)
    args = parser.parse_args()

    text = args.text
    if not text:
        print("Enter post text (Ctrl+D when done):")
        text = sys.stdin.read().strip()

    if not text:
        print("No text provided.")
        sys.exit(1)

    media_path = args.media or args.image
    if media_path and not os.path.exists(media_path):
        print(f"Media file not found: {media_path}")
        sys.exit(1)

    token = get_token()

    if args.reshare:
        print(f"\nResharing post {args.reshare} to GenWise LinkedIn page...")
        result = create_reshare(args.reshare, text, token)

        if result["success"]:
            post_id = result["post_id"]
            post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
            print(f"\n✅ Reshared successfully!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {post_url}")

            if args.comment:
                print(f"\n  Adding first comment...")
                c = post_first_comment(post_id, args.comment, token)
                if c["success"]:
                    print(f"  ✅ First comment added")
                else:
                    print(f"  ⚠️  Comment failed: {c['error']}")
        else:
            print(f"\n❌ Reshare failed: {result}")
            sys.exit(1)
    else:
        print(f"\nPosting to GenWise LinkedIn page...")
        result = create_post(text, token, media_path)

        if result["success"]:
            post_id = result["post_id"]
            post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
            print(f"\n✅ Posted successfully!")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {post_url}")

            if args.comment:
                print(f"\n  Adding first comment...")
                c = post_first_comment(post_id, args.comment, token)
                if c["success"]:
                    print(f"  ✅ First comment added")
                else:
                    print(f"  ⚠️  Comment failed: {c['error']}")
        else:
            print(f"\n❌ Failed: {result}")
            sys.exit(1)


if __name__ == "__main__":
    main()

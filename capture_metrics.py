#!/usr/bin/env python3
"""
Monthly social media metrics capture for GenWise.

Pulls follower counts and engagement metrics from Twitter and LinkedIn,
then appends a summary row to the FOLLOWER_TRACKER tab in the
GW-Social-Media spreadsheet.

Usage:
    python3 capture_metrics.py                   # current month
    python3 capture_metrics.py --month 2026-05   # specific month

Twitter (Free tier): followers, following, total tweets, total likes.
LinkedIn: followers, impressions, unique impressions, clicks, likes, comments, shares.
"""

import os
import sys
import json
import argparse
import hmac
import hashlib
import time
import base64
import secrets
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from calendar import monthrange

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

ENV_PATH = os.getenv("ENV_PATH", os.path.expanduser("~/.env"))
load_dotenv(ENV_PATH)

# ── Config ──────────────────────────────────────────────────────────────────

SHEET_ID = "1ersqOc7F9-BxDNji9hJ2Ti9dA4G5-zQDNW3i9O8LIXg"
TAB_NAME = "FOLLOWER_TRACKER"
SA_KEY = os.getenv("SA_KEY_PATH", os.path.expanduser("~/.config/gcp/service-account-key.json"))
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TW_USER_ID = "895651801722044417"
TW_API_KEY = os.getenv("TWITTER_WORK_API_KEY")
TW_API_SECRET = os.getenv("TWITTER_WORK_API_KEY_SECRET")
TW_ACCESS_TOKEN = os.getenv("TWITTER_WORK_ACCESS_TOKEN")
TW_ACCESS_SECRET = os.getenv("TWITTER_WORK_ACCESS_TOKEN_SECRET")

LI_ORG_URN = "urn:li:organization:42797325"
LI_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LI_REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN")
LI_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LI_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LI_API_BASE = "https://api.linkedin.com/v2"


# ── Twitter OAuth 1.0a ─────────────────────────────────────────────────────

def tw_oauth_request(url):
    oauth_params = {
        "oauth_consumer_key": TW_API_KEY,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": TW_ACCESS_TOKEN,
        "oauth_version": "1.0",
    }

    parsed = urllib.parse.urlparse(url)
    query_params = dict(urllib.parse.parse_qsl(parsed.query))
    all_params = {**oauth_params, **query_params}

    param_string = "&".join(
        f"{urllib.parse.quote(k, safe='')}"
        f"={urllib.parse.quote(v, safe='')}"
        for k, v in sorted(all_params.items())
    )
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    base_string = (
        f"GET&{urllib.parse.quote(base_url, safe='')}"
        f"&{urllib.parse.quote(param_string, safe='')}"
    )
    signing_key = (
        f"{urllib.parse.quote(TW_API_SECRET, safe='')}"
        f"&{urllib.parse.quote(TW_ACCESS_SECRET, safe='')}"
    )
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params["oauth_signature"] = signature

    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )

    req = urllib.request.Request(url, headers={"Authorization": auth_header})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_twitter_metrics():
    url = "https://api.twitter.com/2/users/me?user.fields=public_metrics"
    data = tw_oauth_request(url)
    m = data["data"]["public_metrics"]
    return {
        "followers": m["followers_count"],
        "following": m["following_count"],
        "tweets": m["tweet_count"],
        "likes": m["like_count"],
    }


# ── LinkedIn ────────────────────────────────────────────────────────────────

def li_request(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return None
        raise


def li_refresh_token():
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": LI_REFRESH_TOKEN,
        "client_id": LI_CLIENT_ID,
        "client_secret": LI_CLIENT_SECRET,
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

    import re
    env_path = ENV_PATH
    with open(env_path, "r") as f:
        content = f.read()
    content = re.sub(
        r"^LINKEDIN_ACCESS_TOKEN=.*$",
        f"LINKEDIN_ACCESS_TOKEN={new_token}",
        content,
        flags=re.MULTILINE,
    )
    with open(env_path, "w") as f:
        f.write(content)

    print("  LinkedIn token refreshed")
    return new_token


def get_li_token():
    token = LI_ACCESS_TOKEN
    result = li_request(
        f"{LI_API_BASE}/organizationalEntityFollowerStatistics"
        f"?q=organizationalEntity&organizationalEntity={LI_ORG_URN}",
        token,
    )
    if result is None:
        token = li_refresh_token()
        result = li_request(
            f"{LI_API_BASE}/organizationalEntityFollowerStatistics"
            f"?q=organizationalEntity&organizationalEntity={LI_ORG_URN}",
            token,
        )
    return token, result


def get_linkedin_metrics(token, follower_data, start_ms, end_ms):
    # Seniority breakdown has the highest coverage of any segment type.
    # Still underreports vs the page total (~20% gap — API excludes
    # followers with incomplete profiles).
    total_followers = sum(
        seg["followerCounts"]["organicFollowerCount"]
        + seg["followerCounts"]["paidFollowerCount"]
        for seg in follower_data["elements"][0].get("followerCountsBySeniority", [])
    )

    engagement = {"impressions": 0, "unique_impressions": 0, "clicks": 0,
                  "likes": 0, "comments": 0, "shares": 0}

    if end_ms - start_ms > 86400000:
        share_url = (
            f"{LI_API_BASE}/organizationalEntityShareStatistics"
            f"?q=organizationalEntity&organizationalEntity={LI_ORG_URN}"
            f"&timeIntervals.timeGranularityType=MONTH"
            f"&timeIntervals.timeRange.start={start_ms}"
            f"&timeIntervals.timeRange.end={end_ms}"
        )
        share_data = li_request(share_url, token)

        if share_data and share_data.get("elements"):
            stats = share_data["elements"][0].get("totalShareStatistics", {})
            engagement = {
                "impressions": stats.get("impressionCount", 0),
                "unique_impressions": stats.get("uniqueImpressionsCount", 0),
                "clicks": stats.get("clickCount", 0),
                "likes": stats.get("likeCount", 0),
                "comments": stats.get("commentCount", 0),
                "shares": stats.get("shareCount", 0),
            }
    else:
        print("  (Skipping engagement stats — less than 1 day of data)")

    return {"followers": total_followers, **engagement}


# ── Sheets ──────────────────────────────────────────────────────────────────

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(SA_KEY, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds).spreadsheets()


def get_previous_row(sheets):
    result = sheets.values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB_NAME}'!A:A",
    ).execute()
    rows = result.get("values", [])
    if len(rows) < 2:
        return None, 0, 0

    last_row_num = len(rows)
    last_data = sheets.values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB_NAME}'!A{last_row_num}:N{last_row_num}",
    ).execute()
    vals = last_data.get("values", [[]])[0]
    prev_tw = int(vals[1]) if len(vals) > 1 and vals[1] else 0
    prev_li = int(vals[2]) if len(vals) > 2 and vals[2] else 0
    return vals, prev_tw, prev_li


def append_row(sheets, row):
    sheets.values().append(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB_NAME}'!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()


# ── Main ────────────────────────────────────────────────────────────────────

def parse_month(month_str):
    year, month = map(int, month_str.split("-"))
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    # End = first day of next month (LinkedIn API expects exclusive end)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if end > now:
        end = now
    return start, end, f"{year}-{month:02d}"


def main():
    parser = argparse.ArgumentParser(description="Capture monthly social media metrics")
    parser.add_argument("--month", help="Month to capture (YYYY-MM), default: current")
    parser.add_argument("--dry-run", action="store_true", help="Print metrics without writing to sheet")
    args = parser.parse_args()

    if args.month:
        start, end, label = parse_month(args.month)
    else:
        now = datetime.now(timezone.utc)
        # Default: previous completed month's engagement data
        if now.month == 1:
            prev_year, prev_month = now.year - 1, 12
        else:
            prev_year, prev_month = now.year, now.month - 1
        start, end, label = parse_month(f"{prev_year}-{prev_month:02d}")

    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    capture_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"Capturing metrics for {label} (captured on {capture_date})")

    # Twitter
    print("\n📊 Twitter (@Genwise_)...")
    try:
        tw = get_twitter_metrics()
        print(f"  Followers: {tw['followers']}")
        print(f"  Following: {tw['following']}")
        print(f"  Total tweets: {tw['tweets']}")
        print(f"  Total likes: {tw['likes']}")
    except Exception as e:
        print(f"  ERROR: {e}")
        tw = {"followers": "", "following": "", "tweets": "", "likes": ""}

    # LinkedIn
    print("\n📊 LinkedIn (GenWise page)...")
    try:
        li_token, follower_data = get_li_token()
        li = get_linkedin_metrics(li_token, follower_data, start_ms, end_ms)
        print(f"  Followers: {li['followers']}")
        print(f"  Impressions: {li['impressions']} (unique: {li['unique_impressions']})")
        print(f"  Clicks: {li['clicks']}")
        print(f"  Likes: {li['likes']}")
        print(f"  Comments: {li['comments']}")
        print(f"  Shares: {li['shares']}")
    except Exception as e:
        print(f"  ERROR: {e}")
        li = {"followers": "", "impressions": "", "unique_impressions": "",
              "clicks": "", "likes": "", "comments": "", "shares": ""}

    # Deltas
    if not args.dry_run:
        sheets = get_sheets_service()
        _, prev_tw, prev_li = get_previous_row(sheets)
        tw_delta = (tw["followers"] - prev_tw) if isinstance(tw["followers"], int) and prev_tw else ""
        li_delta = (li["followers"] - prev_li) if isinstance(li["followers"], int) and prev_li else ""
    else:
        tw_delta = ""
        li_delta = ""

    # Row: date, tw_followers, li_followers, tw_delta, li_delta,
    #       tw_following, tw_total_tweets, tw_total_likes,
    #       li_impressions, li_unique_impressions, li_clicks,
    #       li_likes, li_comments, li_shares
    row = [
        capture_date,
        tw.get("followers", ""),
        li.get("followers", ""),
        tw_delta,
        li_delta,
        tw.get("following", ""),
        tw.get("tweets", ""),
        tw.get("likes", ""),
        li.get("impressions", ""),
        li.get("unique_impressions", ""),
        li.get("clicks", ""),
        li.get("likes", ""),
        li.get("comments", ""),
        li.get("shares", ""),
    ]

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Row: {row}")

    if not args.dry_run:
        append_row(sheets, row)
        print(f"\nAppended to {TAB_NAME} tab.")

    # Summary
    print(f"\n── Summary ({label}) ──")
    print(f"  TW: {tw.get('followers', '?')} followers ({'+' if isinstance(tw_delta, int) and tw_delta >= 0 else ''}{tw_delta})")
    print(f"  LI: {li.get('followers', '?')} followers ({'+' if isinstance(li_delta, int) and li_delta >= 0 else ''}{li_delta})")
    if isinstance(li.get("impressions"), int):
        li_engagement = li["likes"] + li["comments"] + li["shares"]
        print(f"  LI engagement: {li['impressions']} impressions, {li['clicks']} clicks, {li_engagement} reactions")


if __name__ == "__main__":
    main()

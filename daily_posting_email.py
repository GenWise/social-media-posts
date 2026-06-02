#!/usr/bin/env python3
"""
Daily posting plan email — reads POSTS_MASTER via Apps Script proxy,
finds today's SCHEDULED/READY posts and overdue posts, sends summary
via SMTP2GO to rajesh@genwise.in.

Deployed on DO droplet as a cron job.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

PROXY_URL = "https://script.google.com/macros/s/AKfycbxCzwF7o0VmVQRu3ItQl4zHasNcsC2ybV7zBqPKrlM9RjbXO03MVGb7Z949WavIUZVSdg/exec"
DASHBOARD_URL = "https://genwise.github.io/social-media-posts/"

def load_env(path):
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass

load_env(os.path.expanduser("~/.env"))

SMTP2GO_API_KEY = os.environ.get("SMTP2GO_API_KEY", "")
TO_EMAIL = "rajesh@genwise.in"
FROM_EMAIL = "rajesh@genwise.in"


def fetch_posts():
    req = urllib.request.Request(PROXY_URL, headers={"User-Agent": "GW-DailyEmail/1.0"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if attempt == 0:
                continue
            raise RuntimeError(f"Proxy failed after 2 attempts: {e}")


def parse_date(s):
    """Parse scheduled_time from various formats into a date in IST."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.date()
        except ValueError:
            continue
    # JS Date string: "Mon Jun 01 2026 15:30:00 GMT+0530 (India Standard Time)"
    try:
        paren = s.find("(")
        if paren > 0:
            s = s[:paren].strip()
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(s)
        dt_ist = dt.astimezone(IST)
        return dt_ist.date()
    except Exception:
        pass
    return None


def build_html(today_posts, overdue_posts, today_str):
    table_style = (
        'style="border-collapse:collapse;width:100%;font-family:system-ui,sans-serif;font-size:14px"'
    )
    th_style = 'style="border:1px solid #ddd;padding:8px 10px;background:#f5f5f5;text-align:left"'
    td_style = 'style="border:1px solid #ddd;padding:8px 10px;vertical-align:top"'

    def post_table(posts):
        rows = ""
        for p in posts:
            hook = (p.get("hook") or p.get("final_post_text") or "")[:120]
            platform = p.get("variant_id") or p.get("platform") or "?"
            rows += f"""<tr>
                <td {td_style}>{p.get('post_id','')}</td>
                <td {td_style}>{platform}</td>
                <td {td_style}>{p.get('person_featured','')}</td>
                <td {td_style}>{hook}</td>
                <td {td_style}>{p.get('media_type','text')}</td>
                <td {td_style}>{p.get('status','')}</td>
                <td {td_style}>{p.get('scheduled_time','')}</td>
            </tr>"""
        return f"""<table {table_style}>
            <tr>
                <th {th_style}>Post ID</th>
                <th {th_style}>Platform</th>
                <th {th_style}>Person</th>
                <th {th_style}>Hook</th>
                <th {th_style}>Media</th>
                <th {th_style}>Status</th>
                <th {th_style}>Scheduled</th>
            </tr>{rows}</table>"""

    html = f"""<div style="font-family:system-ui,sans-serif;max-width:700px;margin:0 auto">
    <p>Good morning! Here's your posting plan for <strong>{today_str}</strong>.</p>"""

    if today_posts:
        html += f"<h3>Today's Posts ({len(today_posts)})</h3>" + post_table(today_posts)
    else:
        html += "<p>No posts scheduled for today.</p>"

    if overdue_posts:
        html += f'<h3 style="color:#c0392b">Overdue Posts ({len(overdue_posts)})</h3>' + post_table(overdue_posts)

    html += f"""<p style="margin-top:20px">
        <a href="{DASHBOARD_URL}" style="background:#ff8d39;color:#fff;padding:10px 20px;text-decoration:none;border-radius:4px;display:inline-block">
            Open Dashboard
        </a>
    </p>
    <p style="color:#888;font-size:12px;margin-top:30px">Automated daily summary from the GenWise social media pipeline.</p>
    </div>"""
    return html


def send_email(subject, html_body):
    payload = json.dumps({
        "api_key": SMTP2GO_API_KEY,
        "to": [TO_EMAIL],
        "sender": FROM_EMAIL,
        "subject": subject,
        "html_body": html_body,
    }).encode()

    req = urllib.request.Request(
        "https://api.smtp2go.com/v3/email/send",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        if result.get("data", {}).get("succeeded", 0) < 1:
            raise RuntimeError(f"SMTP2GO send failed: {result}")
        return result


def main():
    now_ist = datetime.now(IST)
    today = now_ist.date()
    today_str = now_ist.strftime("%a %b %d, %Y")

    try:
        data = fetch_posts()
    except RuntimeError as e:
        send_email(
            f"GenWise Social Media — {today_str} (ERROR)",
            f"<p>Could not fetch posts: {e}</p><p><a href='{DASHBOARD_URL}'>Check dashboard manually</a></p>",
        )
        print(f"[{now_ist}] ERROR: {e}")
        sys.exit(1)

    posts = data.get("posts", [])
    active_statuses = {"DRAFT", "READY", "SCHEDULED"}

    today_posts = []
    overdue_posts = []

    for p in posts:
        status = (p.get("status") or "").upper()
        if status not in active_statuses:
            continue
        sched_date = parse_date(p.get("scheduled_time", ""))
        if sched_date == today:
            today_posts.append(p)
        elif sched_date and sched_date < today:
            overdue_posts.append(p)

    subject = f"GenWise Social Media — Today's Posts ({today_str})"
    html = build_html(today_posts, overdue_posts, today_str)
    send_email(subject, html)
    print(f"[{now_ist}] Sent daily email: {len(today_posts)} today, {len(overdue_posts)} overdue")


if __name__ == "__main__":
    main()

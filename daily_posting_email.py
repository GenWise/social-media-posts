#!/usr/bin/env python3
"""
Daily posting plan email — reads POSTS_MASTER via Apps Script proxy,
lists the unposted pipeline (READY first), Mondays and Fridays
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


def build_html(ready_posts, scheduled_posts, draft_posts, today_str):
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
    <p>Posting pipeline as of <strong>{today_str}</strong>. Post the READY ones first.</p>"""

    if ready_posts:
        html += f"<h3>Ready to post ({len(ready_posts)})</h3>" + post_table(ready_posts)
    if scheduled_posts:
        html += f"<h3>Scheduled ({len(scheduled_posts)})</h3>" + post_table(scheduled_posts)
    if draft_posts:
        html += f'<h3 style="color:#888">Still in draft ({len(draft_posts)})</h3>' + post_table(draft_posts)

    html += f"""<p style="margin-top:20px">
        <a href="{DASHBOARD_URL}" style="background:#ff8d39;color:#fff;padding:10px 20px;text-decoration:none;border-radius:4px;display:inline-block">
            Open Dashboard
        </a>
    </p>
    <p style="color:#888;font-size:12px;margin-top:30px">Sent Mondays and Fridays while the pipeline has anything unposted.</p>
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

    # Twice a week (cron: Mon and Fri), and only while there is something unposted. The
    # old daily "today's posts" mail said "no posts today" 27 mornings out of 28 and
    # re-listed the same June drafts as overdue every time (2026-09-15). This lists the
    # whole open pipeline instead, READY first, so it gets exhausted.
    by_status = {s: [] for s in active_statuses}
    for p in posts:
        status = (p.get("status") or "").upper()
        if status in by_status:
            by_status[status].append(p)
    ready, scheduled, drafts = by_status["READY"], by_status["SCHEDULED"], by_status["DRAFT"]
    if not ready and not scheduled and not drafts:
        print(f"[{now_ist}] Pipeline empty - no email")
        return

    subject = f"GenWise Social Media — {len(ready)} ready, {len(scheduled)} scheduled, {len(drafts)} drafts ({today_str})"
    send_email(subject, build_html(ready, scheduled, drafts, today_str))
    print(f"[{now_ist}] Sent pipeline email: {len(ready)} ready, {len(scheduled)} scheduled, {len(drafts)} drafts")


if __name__ == "__main__":
    main()

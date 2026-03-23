#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 one-time auth flow.
Run this once to capture access + refresh tokens.
Tokens are saved to ~/.env as LINKEDIN_ACCESS_TOKEN and LINKEDIN_REFRESH_TOKEN.
"""

import os
import sys
import json
import webbrowser
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

CLIENT_ID = os.environ["LINKEDIN_CLIENT_ID"]
CLIENT_SECRET = os.environ["LINKEDIN_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = [
    "r_basicprofile",
    "w_organization_social",
    "r_organization_social",
    "rw_organization_admin",
]

# Global to capture auth code from callback
captured_code = None
captured_error = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code, captured_error
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            captured_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Auth successful! You can close this tab.</h2>")
        elif "error" in params:
            captured_error = params.get("error_description", params["error"])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h2>Error: {captured_error}</h2>".encode())
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress request logs


def build_auth_url():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "linkedin_auth_genwise",
    }
    return "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(params)


def exchange_code_for_token(code):
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
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
        return json.loads(resp.read())


def save_tokens_to_env(token_data):
    env_path = os.path.expanduser("~/.env")
    with open(env_path, "r") as f:
        content = f.read()

    def upsert(content, key, value):
        import re
        pattern = rf"^{key}=.*$"
        replacement = f"{key}={value}"
        if re.search(pattern, content, re.MULTILINE):
            return re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            return content + f"\n{key}={value}"

    content = upsert(content, "LINKEDIN_ACCESS_TOKEN", token_data["access_token"])
    if "refresh_token" in token_data:
        content = upsert(content, "LINKEDIN_REFRESH_TOKEN", token_data["refresh_token"])
    if "expires_in" in token_data:
        content = upsert(content, "LINKEDIN_TOKEN_EXPIRES_IN", str(token_data["expires_in"]))
    if "refresh_token_expires_in" in token_data:
        content = upsert(content, "LINKEDIN_REFRESH_TOKEN_EXPIRES_IN", str(token_data["refresh_token_expires_in"]))

    with open(env_path, "w") as f:
        f.write(content)


def main():
    auth_url = build_auth_url()
    print(f"\nOpening browser for LinkedIn authorization...")
    print(f"\nIf browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for callback on http://localhost:8080/callback ...")
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.timeout = 120  # 2 min timeout

    # Loop until we get the code or an error (ignores favicon/other stray requests)
    import time
    deadline = time.time() + 120
    while not captured_code and not captured_error and time.time() < deadline:
        server.handle_request()

    if captured_error:
        print(f"\nAuth failed: {captured_error}")
        sys.exit(1)

    if not captured_code:
        print("\nNo code received. Did you approve the app?")
        sys.exit(1)

    print("Code received. Exchanging for access token...")
    try:
        token_data = exchange_code_for_token(captured_code)
    except Exception as e:
        print(f"Token exchange failed: {e}")
        sys.exit(1)

    save_tokens_to_env(token_data)

    print("\nTokens saved to ~/.env")
    print(f"  Access token expires in: {token_data.get('expires_in', '?')}s (~{token_data.get('expires_in', 0)//86400} days)")
    if "refresh_token_expires_in" in token_data:
        print(f"  Refresh token expires in: {token_data['refresh_token_expires_in']//86400} days")
    print(f"  Scopes granted: {token_data.get('scope', '?')}")
    print("\nDone. You can now use post_to_linkedin.py")


if __name__ == "__main__":
    main()

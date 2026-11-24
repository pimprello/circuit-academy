"""Run this ONCE on your computer (open in IDLE, press F5) to get the YouTube refresh token
for the electronics channel. It installs what it needs, opens your browser, you pick the
channel's Google account and allow access, and it prints the three values to paste into
GitHub -> circuit-academy -> Settings -> Secrets and variables -> Actions."""
import subprocess, sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "google-auth-oauthlib"])
    from google_auth_oauthlib.flow import InstalledAppFlow

print("Paste the OAuth client ID and secret from Google Cloud Console")
print("(APIs & Services -> Credentials -> your 'Desktop app' OAuth client).\n")
client_id = input("Client ID: ").strip()
client_secret = input("Client secret: ").strip()

flow = InstalledAppFlow.from_client_config(
    {"installed": {"client_id": client_id, "client_secret": client_secret,
                   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                   "token_uri": "https://oauth2.googleapis.com/token",
                   "redirect_uris": ["http://localhost"]}},
    scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
print("\nYour browser will open. Sign in, choose the ELECTRONICS channel, and allow access.\n")
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

print("\nDone. Add these three secrets to the circuit-academy repo on GitHub:\n")
print("  YT_CLIENT_ID      =", client_id)
print("  YT_CLIENT_SECRET  =", client_secret)
print("  YT_REFRESH_TOKEN  =", creds.refresh_token)
input("\nPress Enter to close.")

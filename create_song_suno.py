"""
Create a song on Suno via browser automation.

Usage:
    python create_song_suno.py "upbeat pop song about summer"

Or from Discord: !create song upbeat pop song about summer

First run: Log in to Suno manually when the browser opens.
After that, your session is saved.

Requires: pip install playwright && playwright install chromium
"""

from pathlib import Path

# Persistent browser data (saves your Suno login)
USER_DATA_DIR = Path(__file__).parent / ".suno_browser_data"
SUNO_URL = "https://suno.com"


def create_song_on_suno(description: str, interactive: bool = True) -> bool:
    """Open Suno in browser, enter description, click Create. Returns True on success."""
    if not description or len(description.strip()) < 3:
        print("❌ Provide a song description (e.g. 'chill lo-fi beat for studying')")
        return False

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Install Playwright: pip install playwright && playwright install chromium")
        return False

    USER_DATA_DIR.mkdir(exist_ok=True)
    desc = description.strip()[:500]

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            viewport={"width": 1280, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(SUNO_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)

        # Click Sign In / Login first if visible (so user can enter credentials)
        login_selectors = [
            'a:has-text("Sign In")',
            'button:has-text("Sign In")',
            'a:has-text("Login")',
            'button:has-text("Login")',
            '[href*="login"]',
            '[href*="signin"]',
        ]
        for sel in login_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    print("🔐 Clicked Login — enter your credentials, waiting up to 2 minutes...")
                    page.wait_for_timeout(3000)
                    break
            except Exception:
                continue

        # Click Create / Get started if on landing page
        create_btn_selectors = [
            'a:has-text("Create")',
            'button:has-text("Create")',
            '[href="/create"]',
            'a[href*="create"]',
            'button:has-text("Get started")',
            'a:has-text("Get started")',
        ]
        for sel in create_btn_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    page.wait_for_timeout(3000)
                    break
            except Exception:
                continue

        # Find prompt text box - Suno uses textarea or contenteditable for song description
        prompt_selectors = [
            'textarea[placeholder*="describe"]',
            'textarea[placeholder*="prompt"]',
            'textarea[placeholder*="song"]',
            'textarea[placeholder*="imagine"]',
            'textarea[placeholder*="Create"]',
            'input[placeholder*="describe"]',
            'input[placeholder*="prompt"]',
            'div[contenteditable="true"][data-placeholder]',
            'textarea',
            'div[role="textbox"]',
            '[data-testid*="prompt"]',
            '[data-testid*="input"]',
        ]
        typed = False
        for sel in prompt_selectors:
            try:
                box = page.locator(sel).first
                if box.is_visible(timeout=2000):
                    box.click()
                    page.wait_for_timeout(500)
                    box.fill("")
                    box.type(desc, delay=40)
                    typed = True
                    print(f"✅ Entered: {desc[:60]}...")
                    break
            except Exception:
                continue

        if not typed:
            print("⚠️ Could not find prompt box. Log in to Suno and go to Create — waiting up to 2 minutes...")
            if interactive:
                input("Press Enter after you're on the Create page, or Ctrl+C to exit...")
                return create_song_on_suno(description, interactive=True)
            # Wait and retry for non-interactive (Discord)
            for attempt in range(24):
                page.wait_for_timeout(5000)
                for sel in prompt_selectors:
                    try:
                        box = page.locator(sel).first
                        if box.is_visible(timeout=1000):
                            box.click()
                            page.wait_for_timeout(300)
                            box.fill("")
                            box.type(desc, delay=40)
                            typed = True
                            break
                    except Exception:
                        continue
                if typed:
                    break
                print(f"   Still waiting... ({attempt * 5}s)")
            if not typed:
                print("❌ Timed out. Log in to Suno first, then run !create song again.")
                context.close()
                return False

        page.wait_for_timeout(1500)

        # Click Create / Generate button
        create_selectors = [
            'button:has-text("Create")',
            'button:has-text("Generate")',
            'button:has-text("Make")',
            '[data-testid*="create"]',
            '[data-testid*="generate"]',
            'button[type="submit"]',
            'a:has-text("Create")',
        ]
        for sel in create_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000) and btn.is_enabled():
                    btn.click()
                    print("✅ Clicked Create! Suno is generating your song...")
                    page.wait_for_timeout(5000)
                    break
            except Exception:
                continue

        if interactive:
            input("Press Enter to close browser (song keeps generating in Suno)...")
        context.close()
        return True


def main():
    import sys
    desc = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not desc:
        desc = input("Song description: ").strip()
    create_song_on_suno(desc)


if __name__ == "__main__":
    main()

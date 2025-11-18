#!/usr/bin/env python3
"""
Recapture screenshots with actual content visible.
Ensures proper loading time and waits for dynamic content.
"""
from playwright.sync_api import sync_playwright
import time
import os

def capture_screenshots():
    """Capture screenshots from local running instance."""
    with sync_playwright() as p:
        # Launch browser in headed mode to see what's happening (optional)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1200})
        page = context.new_page()

        base_url = "http://127.0.0.1:5001"
        screenshots_dir = "static/screenshots"

        # Ensure screenshots directory exists
        os.makedirs(screenshots_dir, exist_ok=True)

        screenshots = [
            {
                'name': 'updated_home.png',
                'url': '/',
                'wait_selector': '.card-title',
                'full_page': False,
                'description': 'Home page with stats'
            },
            {
                'name': 'add_form_empty.png',
                'url': '/add-interaction',
                'wait_selector': '#source_tool_id',
                'full_page': True,
                'description': 'Add interaction form'
            },
            {
                'name': 'interaction_list.png',
                'url': '/interactions',
                'wait_selector': '.card-header',
                'full_page': True,
                'description': 'Interaction list view'
            },
            {
                'name': 'interaction_detail.png',
                'url': '/interaction/1',
                'wait_selector': '.card-body',
                'full_page': True,
                'description': 'Interaction detail page'
            },
            {
                'name': 'edit_form.png',
                'url': '/interaction/1/edit',
                'wait_selector': '#source_tool_id',
                'full_page': True,
                'description': 'Edit interaction form'
            },
            {
                'name': 'rdl_viz.png',
                'url': '/enhanced-rdl-visualization',
                'wait_selector': '.card',
                'full_page': False,
                'description': 'RDL visualization',
                'wait_time': 3  # Extra time for rendering
            },
            {
                'name': 'user_guide.png',
                'url': '/user-guide',
                'wait_selector': '.card-body',
                'full_page': True,
                'description': 'User guide page'
            }
        ]

        for shot in screenshots:
            try:
                print(f"\n📸 Capturing: {shot['description']}")
                page.goto(f"{base_url}{shot['url']}")

                # Wait for page to be fully loaded
                page.wait_for_load_state("networkidle")

                # Wait for specific selector
                if shot.get('wait_selector'):
                    print(f"   Waiting for selector: {shot['wait_selector']}")
                    page.wait_for_selector(shot['wait_selector'], timeout=10000)

                # Handle clicks if needed
                if shot.get('click_first'):
                    print(f"   Clicking: {shot['click_first']}")
                    page.click(shot['click_first'])
                    page.wait_for_load_state("networkidle")
                    if shot.get('wait_selector'):
                        page.wait_for_selector(shot['wait_selector'], timeout=10000)

                if shot.get('click_second'):
                    print(f"   Clicking: {shot['click_second']}")
                    page.click(shot['click_second'])
                    page.wait_for_load_state("networkidle")
                    if shot.get('wait_selector'):
                        page.wait_for_selector(shot['wait_selector'], timeout=10000)

                # Extra wait time if specified
                wait_time = shot.get('wait_time', 2)
                print(f"   Waiting {wait_time}s for content to render...")
                time.sleep(wait_time)

                # Capture screenshot
                filepath = f"{screenshots_dir}/{shot['name']}"
                page.screenshot(path=filepath, full_page=shot['full_page'])

                # Check file size
                size = os.path.getsize(filepath)
                print(f"   ✅ Saved: {filepath} ({size:,} bytes)")

                if size < 5000:
                    print(f"   ⚠️  WARNING: File size is small, may be blank!")

            except Exception as e:
                print(f"   ❌ Error capturing {shot['name']}: {e}")
                continue

        browser.close()
        print("\n✅ Screenshot capture complete!")

if __name__ == "__main__":
    print("🎬 Starting screenshot capture...")
    print("📌 Make sure local server is running on http://127.0.0.1:5001")
    print("📌 Make sure database has sample data loaded")
    print()
    capture_screenshots()

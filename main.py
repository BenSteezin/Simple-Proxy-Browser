import asyncio
import random
from playwright.async_api import async_playwright

def read_proxies(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

async def open_browser_with_proxy(proxy):
    ip, port, _, _ = proxy.split(':')  # Ignore username and password
    async with async_playwright() as p:
        # Launch the browser with a global dummy proxy to satisfy Playwright requirements
        browser = await p.chromium.launch(headless=False, proxy={"server": "http://per-context"})

        # Create a new context with the specific proxy settings for each instance
        context = await browser.new_context(
            proxy={"server": f"http://{ip}:{port}"},
            accept_downloads=True,
            storage_state=None  # Ensure no storage state is persisted
        )
        
        page = await context.new_page()
        print(f"Opening browser with proxy: {ip}:{port}")
        
        # Navigate to a test site
        await page.goto('https://example.com', wait_until='domcontentloaded')

        # Attach an event listener to handle closing the browser
        async def on_close():
            await context.clear_cookies()
            await context.close()
            await browser.close()
            print(f"All fingerprints and session data have been wiped for proxy: {ip}:{port}")

        # Add the close listener to the browser
        browser.on("close", lambda: asyncio.create_task(on_close()))

        # Keep the script running until the browser is closed
        await asyncio.Event().wait()

async def main():
    file_path = 'proxies.txt'
    proxies = read_proxies(file_path)

    # Shuffle the proxies list for randomness
    random.shuffle(proxies)

    # Prompt for the number of instances
    num_instances = int(input(f"How many instances would you like to open? (max {len(proxies)}): "))
    num_instances = min(num_instances, len(proxies))  # Ensure it doesn't exceed available proxies

    tasks = []
    for i in range(num_instances):
        tasks.append(open_browser_with_proxy(proxies[i]))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

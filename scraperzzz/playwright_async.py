# =============================================================================
# Async scraper with playwright
# =============================================================================
#
# Scraping `https://angular2-hn.firebaseapp.com/news/1` (emulating navigator, scraping, API)
# Need to have Chrome installed on computer
#

import asyncio
import csv
import os
from playwright.async_api import async_playwright


def write_file(response, title):
    header = True if os.path.exists("data/angular2-%s.csv" % title) else False
    with open("data/angular2-%s.csv" % title, "a") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "points", "user", "time", "time_ago", "comments_count", "type", "url", "domain"])
        if not header:
            writer.writeheader()
        for r in response:
            writer.writerow({"id": r.get("id"), "title": r.get("title"), "points": r.get("points"), "user": r.get("user"), "time": r.get("time"), "time_ago": r.get("time_ago"), "comments_count": r.get("comments_count"), "type": r.get("type"), "url": r.get("url"), "domain": r.get("domain")})


async def next_page_and_screenshot(page, url):

    next = None

    async with page.expect_response(lambda r: "node-hnapi.herokuapp.com" in r.url) as intern_api:

        await page.goto(url)

    await page.wait_for_timeout(1000)

    await page.screenshot(path="data/angular2%s.png" % url, full_page=True)

    if await page.locator("a[class='more']").count() != 0:
        next = await page.locator("a[class='more']").get_attribute("href")
        print(await page.locator("a[class='more']").text_content())

    api_response = await intern_api.value

    html = await page.content()

    with open("data/angular2%s.html" % url, "w") as f:
        f.write(html)

    print(await page.title())

    return next, api_response


async def scrape_new(browser):
    context = await browser.new_context(base_url="https://angular2-hn.firebaseapp.com")

    page = await context.new_page()

    next, api_response = await next_page_and_screenshot(page, "")
    write_file(await api_response.json(), "new")

    while next:
        next, api_response = await next_page_and_screenshot(page, next)
        write_file(await api_response.json(), "new")

    await context.close()


async def scrape_show(browser):
    context = await browser.new_context(base_url="https://angular2-hn.firebaseapp.com")

    page = await context.new_page()

    next, api_response = await next_page_and_screenshot(page, "/show/1")
    write_file(await api_response.json(), "show")

    while next:
        next, api_response = await next_page_and_screenshot(page, next)
        write_file(await api_response.json(), "show")

    await context.close()


async def scrape_ask(browser):
    context = await browser.new_context(base_url="https://angular2-hn.firebaseapp.com")

    page = await context.new_page()

    next, api_response = await next_page_and_screenshot(page, "/ask/1")
    write_file(await api_response.json(), "ask")

    while next:
        next, api_response = await next_page_and_screenshot(page, next)
        write_file(await api_response.json(), "ask")

    await context.close()


async def scrape_jobs(browser):
    context = await browser.new_context(base_url="https://angular2-hn.firebaseapp.com")

    page = await context.new_page()

    next, api_response = await next_page_and_screenshot(page, "/jobs/1")
    write_file(await api_response.json(), "jobs")

    while next:
        next, api_response = await next_page_and_screenshot(page, next)
        write_file(await api_response.json(), "jobs")

    await context.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)

        task1 = asyncio.create_task(scrape_show(browser))
        task2 = asyncio.create_task(scrape_ask(browser))
        task3 = asyncio.create_task(scrape_jobs(browser))
        task4 = asyncio.create_task(scrape_new(browser))

        await task1
        await task2
        await task3
        await task4

        await browser.close()

asyncio.run(main())

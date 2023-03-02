#!/usr/bin/env python

import browser_cookie3
import csv
from http.cookies import SimpleCookie
from minet.web import CookieResolver
import os
from playwright_stealth import stealth_sync
from playwright.sync_api import sync_playwright
from random import uniform
import sys

metadata = {
    "id": None, "desc": None, "createTime": None, "originalItem": None,
    "video": ["id", "height", "width", "duration", "ratio", "cover", "originCover", "dynamicCover", "downloadAddr", "reflowCover", "bitrate", "format", "videoQuality"],
    "author": ["id", "uniqueId", "nickname", "avatarLarger", "signature", "verified", "secret"],
    "authorStats": ["followingCount", "followerCount", "heartCount", "videoCount", "diggCount", "heart"],
    "music": ["id", "title", "authorName", "original", "playUrl", "duration"],
    "stats": ["diggCount", "shareCount", "commentCount", "playCount"]
  #  "duetInfo": [], ----> to investigate
}
multi_fields = {
    "textExtra": "hashtagName",
  #  "challenges" : "title", redondant textExtra
    "stickersOnItem": "stickerText"
}

fields = []

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("""
To run this script, run as:\n\npython scraperzzz/playwright_tiktok_account_videos.py SEARCH_ACCOUNT NAME_OF_THE_DIRECTORY_IN_WHICH_EVERYTHING_WILL_BE_COLLECTED
        """)
    output_dir = sys.argv[2]
    account = sys.argv[1]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()

        try:
            jar = getattr(browser_cookie3, "chrome")()
        except browser_cookie3.BrowserCookieError:
            print("Could not extract cookies from chrome!")
            sys.exit()

        resolver = CookieResolver(jar)

        cookie = resolver("https://www.tiktok.com")

        tiktok_cookie = []

        parsed = SimpleCookie(cookie)

        for morsel in parsed.values():
            tiktok_cookie.append({"name": morsel.key, "value": morsel.coded_value, "url": "https://www.tiktok.com", })

        context.add_cookies(tiktok_cookie)
        page = context.new_page()
        stealth_sync(page)

        results = []
        page_nb = 0

        print("Requesting page %s" % page_nb)
        page.goto("https://www.tiktok.com/search/user?q=%s" % account)
        page.wait_for_timeout(1000 + uniform(1, 5000))
        page.wait_for_timeout(1000 + uniform(1, 5000))
        page.wait_for_timeout(1000 + uniform(1, 5000))
        html = page.content()
        with open("tiktok.html", "w") as f:
            f.write(html)
        with page.expect_response(lambda r: "/api/post/item_list/" in r.url) as intern_api:
            div = page.locator("div[data-e2e='search-user-container']").nth(0)
            div.locator("a[href='/@%s']" % account).nth(0).click()
        page.wait_for_timeout(1000 + uniform(1, 5000))
        page.wait_for_timeout(1000 + uniform(1, 5000))
        page.wait_for_timeout(1000 + uniform(1, 5000))

        api_response = intern_api.value
        data = api_response.json()["itemList"]
        for v in data:
            video = {}
            for key, val in metadata.items():
                if val and type(val) == list:
                    for field in val:
                        fieldname = "%s.%s" % (key, field)
                        if fieldname not in fields:
                            fields.append(fieldname)
                        video[fieldname] = v[key][field]
                else:
                    video[key] = v[key]
                    if key not in fields:
                        fields.append(key)
            for key, val in multi_fields.items():
                resKey = key + "s"
                if key in v:
                    video[resKey] = "|".join("|".join(el[val]) if type(el[val]) == list else el[val] for el in v[key])
                if resKey not in fields:
                    fields.append(resKey)
            results.append(video)
        page_nb += 1

        page.screenshot(path=f"data/tiktok/tiktok_account.png", full_page=True)

        html = page.content()
        with open(f"data/tiktok/tiktok.html", "w") as f:
            f.write(html)

        while True:
            print("Requesting page %s" % page_nb)
            with page.expect_response(lambda r: "/api/post/item_list/" in r.url) as intern_api:
                page.keyboard.press('PageDown')
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.keyboard.press('PageDown')
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.keyboard.press('PageDown')
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.wait_for_timeout(1000 + uniform(1, 5000))
                page.wait_for_timeout(1000 + uniform(1, 5000))
            api_response = intern_api.value
            response = api_response.json()
            has_more = response["hasMore"]
            data = response["itemList"]
            for v in data:
                video = {}
                for key, val in metadata.items():
                    if val and type(val) == list:
                        for field in val:
                            fieldname = "%s.%s" % (key, field)
                            if fieldname not in fields:
                                fields.append(fieldname)
                            video[fieldname] = v[key][field]
                    else:
                        video[key] = v[key]
                        if key not in fields:
                            fields.append(key)
                for key, val in multi_fields.items():
                    resKey = key + "s"
                    if key in v:
                        video[resKey] = "|".join("|".join(el[val]) if type(el[val]) == list else el[val] for el in v[key])
                    if resKey not in fields:
                        fields.append(resKey)
                results.append(video)
            page_nb += 1
            print(len(results))
            if not has_more:
                break

        output_file = os.path.join(output_dir, "videos.csv")
        with open(output_file, "w") as f:
            wr = csv.DictWriter(f, fields)
            wr.writeheader()
            wr.writerows(results)
        print("\n\nMetadata on %d videos downloaded in %s.\n\nDownload the corresponding videos by running:\nminet fetch --filename-template \"{line['id']}.{line['video.format']}\" video.downloadAddr %s -d %s" % (len(results), output_file, output_file, output_dir))

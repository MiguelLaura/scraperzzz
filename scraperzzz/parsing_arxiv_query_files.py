# =============================================================================
# Parsing arXiv query files
# =============================================================================
#
# Getting documents info with specific search
#

import requests
import time
import feedparser
import csv
from tqdm import tqdm


LIST_REQUEST_1 = [
    "participat*",
    "co-design",
    "the loop"
]

LIST_REQUEST_2 = [
    "machine learning",
    "ML",
    "artificial intelligence",
    "AI",
    "deep learning",
    "neural network",
]

base_url = 'http://export.arxiv.org/api/query?'


def get_entry(entry, first_word, second_word, query):

    query = query.replace("+", " ")
    query = query.replace("ANDNOT ", "\nNOT ")
    query = query.replace("AND ", "\n")
    query = query.replace("%22", " ")
    query = query.replace("ti:", "title contains ")
    query = query.replace("abs:", "abstract contains ")

    try:
        authors = '\n'.join(author.name for author in entry.authors)
    except AttributeError:
        authors = None

    try:
        journal_ref = entry.arxiv_journal_ref
    except AttributeError:
        journal_ref = 'No journal ref found'

    try:
        comment = entry.arxiv_comment
    except AttributeError:
        comment = 'No comment found'

    all_categories = [t['term'] for t in entry.tags]

    result = {
        'word 1': first_word,
        'word 2': second_word,
        'request': query,
        'title': entry.title,
        'abstract': entry.summary,
        'authors': authors,
        'published': entry.published,
        'last_update': entry.updated,
        'links': '\n'.join(link.href for link in entry.links),
        'category_terms': '\n'.join(all_categories),
        'journal_ref': journal_ref,
        'comments': comment,
        'search_time': feed.feed.updated,
        'link_api': url,
    }

    return result


with open('data/arXiv_ML.csv', 'w') as f:
    total = 0
    fieldnames = ['word 1', 'word 2', 'request', 'title', 'abstract', 'authors', 'published', 'last_update', 'links', 'category_terms', 'journal_ref', 'comments', 'search_time', 'link_api']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for first_word in LIST_REQUEST_1:
        first = first_word
        if " " in first_word:
            first = "%22" + first.replace(" ", "+") + "%22"
        for second_word in LIST_REQUEST_2:
            second = second_word
            if " " in second_word:
                second = "%22" + second.replace(" ", "+") + "%22"

            LIST_REQUEST_API = [
                "ti:%s+AND+ti:%s+ANDNOT+abs:%s+ANDNOT+abs:%s" % (first, second, first, second),
                "abs:%s+AND+abs:%s+ANDNOT+ti:%s+ANDNOT+ti:%s" % (first, second, first, second),
                "ti:%s+AND+ti:%s+AND+abs:%s+AND+abs:%s" % (first, second, first, second),
                "ti:%s+AND+abs:%s+ANDNOT+abs:%s+ANDNOT+ti:%s" % (first, second, first, second),
                "abs:%s+AND+ti:%s+ANDNOT+ti:%s+ANDNOT+abs:%s" % (first, second, first, second),
            ]
            for query in tqdm(LIST_REQUEST_API, total=5):
                url = base_url + "search_query=" + query + "&max_results=200"
                r = requests.get(url)
                feed = feedparser.parse(r.text)
                total += int(feed.feed.opensearch_totalresults)

                for entry in feed.entries:
                    result = get_entry(entry, first_word, second_word, query)
                    writer.writerow(result)

                time.sleep(3)

print(total)

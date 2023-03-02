# =============================================================================
# API Youtube
# =============================================================================
#
# Using Youtube API with multiple API keys (getting first comments)
#

import csv
import googleapiclient.discovery
import os


def first_api_key_first_page(developer_key, video_id):

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = developer_key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
    )
    response = request.execute()

    with open("data/youtube_%s.csv" % video_id, "w") as f:
        result = []
        for i in response["items"]:
            result.append(flattenjson(i, "__"))
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        writer.writeheader()
        for res in result:
            writer.writerow(res)

    return (response["nextPageToken"], video_id)


def second_api_key_second_page(info_video, developer_key):

    next_page_token, video_id = info_video

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = developer_key

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY
    )

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        pageToken=next_page_token
    )
    response = request.execute()

    with open("data/youtube_%s.csv" % video_id, "a") as f:
        result = []
        for i in response["items"]:
            result.append(flattenjson(i, "__"))
        writer = csv.DictWriter(f, fieldnames=result[0].keys())
        for res in result:
            writer.writerow(res)
    return response["nextPageToken"], video_id


def flattenjson(json, delim):
    val = {}
    for i in json.keys():
        if isinstance(json[i], dict):
            get = flattenjson(json[i], delim)
            for j in get.keys():
                val[i + delim + j] = get[j]
        else:
            val[i] = json[i]

    return val


# Insert the wanted API_KEY and VIDEO_ID
second_api_key_second_page(
    first_api_key_first_page("API_KEY", "VIDEO_ID"),
    "API_KEY"
)

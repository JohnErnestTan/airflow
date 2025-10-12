import json
import os
import time
from pathlib import Path

from googleapiclient.discovery import build


def _yt_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY environment variable.")
    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)

def _search_video_ids(youtube, query, max_items=100):
    ids, page_token = [], None
    while len(ids) < max_items:
        resp = youtube.search().list(
            q=query, part="id", type="video", maxResults=50, pageToken=page_token
        ).execute()
        ids.extend([it["id"]["videoId"] for it in resp.get("items", [])])
        page_token = resp.get("nextPageToken")
        if not page_token: break
        time.sleep(0.1)  
    return ids[:max_items]

def _fetch_video_meta(youtube, video_ids):
    items = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        resp = youtube.videos().list(
            id=",".join(chunk),
            part="snippet,statistics,contentDetails"
        ).execute()
        for v in resp.get("items", []):
            snip, stat = v.get("snippet", {}), v.get("statistics", {})
            items.append({
                "videoId": v["id"],
                "title": snip.get("title"),
                "description": snip.get("description"),
                "publishedAt": snip.get("publishedAt"),
                "channelTitle": snip.get("channelTitle"),
                "url": f"https://www.youtube.com/watch?v={v['id']}",
                "viewCount": int(stat.get("viewCount", 0)),
                "likeCount": int(stat.get("likeCount", 0)) if "likeCount" in stat else None,
                "commentCount": int(stat.get("commentCount", 0)) if "commentCount" in stat else None
            })
        time.sleep(0.1)
    return items

def fetch_videos_to_json(topic: str, output_json_path: str, max_results: int = 100):
    youtube = _yt_client()
    ids = _search_video_ids(youtube, topic, max_items=max_results)
    data = _fetch_video_meta(youtube, ids)
    out = Path(output_json_path)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

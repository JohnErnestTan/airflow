import json
import os
import time
from pathlib import Path
from typing import Iterable, List, Sequence

from googleapiclient.discovery import build

_SERVICE_NAME = "youtube"
_SERVICE_VERSION = "v3"
_SEARCH_PAGE_SIZE = 50 #max num of videos per API call
_DETAIL_PAGE_SIZE = 50
_API_THROTTLE_SECONDS = 0.2 #to prevent hitting rate limits


def _build_client():
    # Constructs the YouTube API client using the API key from environment variables.
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY environment variable.")
    return build(
        _SERVICE_NAME, _SERVICE_VERSION, developerKey=api_key, cache_discovery=False
    )


def _gather_video_ids(client, keyword: str, target_count: int) -> List[str]:
    collected: List[str] = []
    token = None
    while len(collected) < target_count:
        response = (
            client.search()
            .list(
                q=keyword,
                part="id",
                type="video",
                maxResults=_SEARCH_PAGE_SIZE,
                pageToken=token,
            )
            .execute()
        )
        for item in response.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if video_id:
                collected.append(video_id)
        token = response.get("nextPageToken")
        if not token:
            break
        time.sleep(_API_THROTTLE_SECONDS)
    return collected[:target_count]


def _fetch_video_payloads(client, identifiers: Sequence[str]) -> List[dict]:
    details: List[dict] = []
    for offset in range(0, len(identifiers), _DETAIL_PAGE_SIZE):
        subset = identifiers[offset : offset + _DETAIL_PAGE_SIZE]
        response = (
            client.videos()
            .list(id=",".join(subset), part="snippet,statistics,contentDetails")
            .execute()
        )
        details.extend(response.get("items", []))
        time.sleep(_API_THROTTLE_SECONDS)
    return details


def _normalize_payload(raw_items: Iterable[dict]) -> List[dict]:
    formatted: List[dict] = []
    for item in raw_items:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        video_id = item.get("id")
        formatted.append(
            {
                "videoId": video_id,
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "publishedAt": snippet.get("publishedAt"),
                "channelTitle": snippet.get("channelTitle"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "viewCount": int(stats.get("viewCount", 0)),
                "likeCount": (
                    int(stats.get("likeCount", 0)) if "likeCount" in stats else None
                ),
                "commentCount": (
                    int(stats.get("commentCount", 0))
                    if "commentCount" in stats
                    else None
                ),
            }
        )
    return formatted


def fetch_videos_to_json(topic: str, output_json_path: str, max_results: int = 100):
    youtube_client = _build_client()
    ids = _gather_video_ids(youtube_client, topic, target_count=max_results)
    raw_data = _fetch_video_payloads(youtube_client, ids)
    normalized = _normalize_payload(raw_data)
    destination_path = Path(output_json_path)
    destination_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return destination_path

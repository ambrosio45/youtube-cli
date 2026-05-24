#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import argparse
from datetime import datetime
from typing import Optional, List

from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
USE_PROXY = os.environ.get("USE_PROXY", "false").lower() == "true"
PROXY_USER = os.environ.get("PROXY_USER", "")
PROXY_PASS = os.environ.get("PROXY_PASS", "")


def format_number(n):
    if n == "N/A":
        return "N/A"
    return f"{int(n):,}".replace(",", ".")


def validate_environment():
    if not YOUTUBE_API_KEY:
        print("Error: YOUTUBE_API_KEY not configured", flush=True)
        print("", flush=True)
        print("Set the environment variable:", flush=True)
        print("  Linux/Mac: export YOUTUBE_API_KEY='your_key_here'", flush=True)
        print("  Windows:   set YOUTUBE_API_KEY=your_key_here", flush=True)
        sys.exit(1)


def validate_output_path(path: str) -> bool:
    if not os.path.exists(path):
        print(f"Error: directory not found: {path}", flush=True)
        sys.exit(1)
    if not os.path.isdir(path):
        print(f"Error: path must be a directory: {path}", flush=True)
        sys.exit(1)
    return True


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _enrich_results_with_details(results: List[dict], video_ids: List[str]) -> None:
    """Enriches results with API details (in-place)."""
    details = get_video_details(video_ids)
    for r in results:
        vid = r["video_id"]
        if vid in details:
            d = details[vid]
            r.update({
                "description": d["description"],
                "default_language": d["default_language"],
                "tags": d["tags"],
                "duration": d["duration"],
                "views": d["views"],
                "likes": d["likes"],
                "comments": d["comments"],
                "published_at": d["published_at"],
            })
        else:
            r.update({
                "default_language": "N/A",
                "tags": [],
                "duration": "00:00",
                "views": "N/A",
                "likes": "N/A",
                "comments": "N/A",
                "published_at": "N/A",
            })


def get_video_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:v=|\/embed\/|\/shorts\/|youtu\.be\/)([A-Za-z0-9_-]{11})",
        r"youtube\.com\/watch\?.*?v=([A-Za-z0-9_-]{11})",
        r"youtube\.com\/v\/([A-Za-z0-9_-]{11})",
        r"youtube\.com\/shorts\/([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def parse_duration(iso_duration: str) -> str:
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
    if not match:
        return "00:00"

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def get_video_metadata(video_id: str) -> dict:
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics", id=video_id
        )
        response = request.execute()

        if response["items"]:
            item = response["items"][0]
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            stats = item.get("statistics", {})

            published_at = snippet.get("publishedAt", "")
            if published_at:
                published_at = datetime.fromisoformat(
                    published_at.replace("Z", "+00:00")
                )
                published_str = published_at.strftime("%d/%m/%Y")
            else:
                published_str = "N/A"

            return {
                "title": snippet.get("title", "Unknown"),
                "description": snippet.get("description", ""),
                "channel": snippet.get("channelTitle", "Unknown"),
                "default_language": snippet.get("defaultLanguage", "N/A"),
                "tags": snippet.get("tags", []),
                "published_at": published_str,
                "duration": parse_duration(content.get("duration", "PT0M0S")),
                "views": stats.get("viewCount", "N/A"),
                "likes": stats.get("likeCount", "N/A"),
                "comments": stats.get("commentCount", "N/A"),
            }
    except Exception:
        pass
    return {
        "title": "Unknown",
        "description": "",
        "channel": "Unknown",
        "default_language": "N/A",
        "tags": [],
        "published_at": "N/A",
        "duration": "00:00",
        "views": "N/A",
        "likes": "N/A",
        "comments": "N/A",
    }


def sanitize_filename(name: str) -> str:
    invalid_chars = r'[<>:"/\\|?*]'
    name = re.sub(invalid_chars, "_", name)
    name = name.strip(". ")
    if len(name) > 200:
        name = name[:200]
    return name


def extract_transcript(url: str, languages: List[str]) -> Optional[str]:
    video_id = get_video_id(url)
    if not video_id:
        return None

    try:
        if USE_PROXY:
            from youtube_transcript_api.proxies import WebshareProxyConfig
            proxy = WebshareProxyConfig(proxy_username=PROXY_USER, proxy_password=PROXY_PASS)
            ytt_api = YouTubeTranscriptApi(proxy_config=proxy)
        else:
            ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=languages)
        dict_transcript = transcript.to_raw_data()

        lines = []
        for t in dict_transcript:
            lines.append(t["text"])

        return " ".join(lines)

    except Exception as erro:
        print(f"Error extracting transcript: {erro}", flush=True)
        return None


def process_url(url: str, output_dir: str) -> bool:
    video_id = get_video_id(url)
    if not video_id:
        print(f"Invalid URL: {url}", flush=True)
        return False

    print(f"Downloading video transcript...", flush=True)

    metadata = get_video_metadata(video_id)

    default_lang = metadata.get("default_language", "N/A")
    if default_lang != "N/A":
        languages = [default_lang, "en", "pt"]
    else:
        languages = ["en", "pt"]

    filename = sanitize_filename(f"{metadata['channel']} - {metadata['title']}")
    output_path = os.path.join(output_dir, f"{filename}.md")

    if os.path.exists(output_path):
        print(f"File already exists, skipping: {filename}.md", flush=True)
        return False

    transcript = extract_transcript(url, languages)
    if not transcript:
        print(f"Failed to extract transcript: {url}", flush=True)
        return False

    tags_str = ", ".join(metadata["tags"]) if metadata["tags"] else "N/A"

    lines = [
        f"# {metadata['title']}",
        "",
        f"**Channel:** {metadata['channel']}",
        "",
        f"**URL:** {url}",
        "",
        f"**Language:** {metadata['default_language']}",
        "",
        f"**Published:** {metadata['published_at']}",
        "",
        f"**Duration:** {metadata['duration']}",
        "",
        f"**Views:** {format_number(metadata['views'])}",
        "",
        f"**Likes:** {format_number(metadata['likes'])}",
        "",
        f"**Comments:** {format_number(metadata['comments'])}",
        "",
        f"**Tags:** {tags_str}",
        "",
        "---",
        "",
        transcript,
    ]

    content = "\n".join(lines)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Transcript saved successfully!", flush=True)
        print(f"   Channel: {metadata['channel']}", flush=True)
        print(f"   Duration: {metadata['duration']}", flush=True)
        print(f"   File: {filename}.md", flush=True)
        return True
    except Exception as e:
        print(f"Error saving file: {e}", flush=True)
        return False

    print(f"Downloading video transcript...", flush=True)

    metadata = get_video_metadata(video_id)

    default_lang = metadata.get("default_language", "N/A")
    if default_lang != "N/A":
        languages = [default_lang, "en", "pt"]
    else:
        languages = ["en", "pt"]

    filename = sanitize_filename(f"{metadata['channel']} - {metadata['title']}")
    output_path = os.path.join(output_dir, f"{filename}.md")

    if os.path.exists(output_path):
        print(f"File already exists, skipping: {filename}.md", flush=True)
        return False

    transcript = extract_transcript(url, languages)
    if not transcricao:
        print(f"Failed to extract transcript: {url}", flush=True)
        return False

    tags_str = ", ".join(metadata["tags"]) if metadata["tags"] else "N/A"

    lines = [
        f"# {metadata['title']}",
        "",
        f"**Channel:** {metadata['channel']}",
        "",
        f"**URL:** {url}",
        "",
        f"**Language:** {metadata['default_language']}",
        "",
        f"**Published:** {metadata['published_at']}",
        "",
        f"**Duration:** {metadata['duration']}",
        "",
        f"**Views:** {format_number(metadata['views'])}",
        "",
        f"**Likes:** {format_number(metadata['likes'])}",
        "",
        f"**Comments:** {format_number(metadata['comments'])}",
        "",
        f"**Tags:** {tags_str}",
        "",
        "---",
        "",
        transcricao,
    ]

    conteudo = "\n".join(lines)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(conteudo)
        print(f"Transcript saved successfully!", flush=True)
        print(f"   Channel: {metadata['channel']}", flush=True)
        print(f"   Duration: {metadata['duration']}", flush=True)
        print(f"   File: {filename}.md", flush=True)
        return True
    except Exception as erro:
        print(f"Error saving file: {erro}", flush=True)
        return False


def process_file(filepath: str, output_dir: str) -> bool:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}", flush=True)
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    video_ids = re.findall(
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|/v/|/embed/)([A-Za-z0-9_-]{11})",
        content,
    )

    video_ids = list(dict.fromkeys(video_ids))

    urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]

    if not urls:
        print(f"No YouTube URLs found in file: {filepath}", flush=True)
        return False

    print(f"Found {len(urls)} URLs in file", flush=True)

    success = 0
    for url in urls:
        if process_url(url, output_dir):
            success += 1

    print(f"Processed: {success}/{len(urls)} URLs successfully", flush=True)
    return success > 0


def get_video_details(video_ids: List[str]) -> dict:
    if not video_ids:
        return {}

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    details = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics", id=",".join(batch)
        )
        response = request.execute()

        for item in response.get("items", []):
            vid = item["id"]
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            stats = item.get("statistics", {})

            published_at = snippet.get("publishedAt", "")
            if published_at:
                try:
                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    published_str = dt.strftime("%d/%m/%Y")
                except:
                    published_str = published_at[:10]
            else:
                published_str = "N/A"

            details[vid] = {
                "description": snippet.get("description", ""),
                "default_language": snippet.get("defaultLanguage", "N/A"),
                "tags": snippet.get("tags", []),
                "duration": parse_duration(content.get("duration", "PT0M0S")),
                "views": stats.get("viewCount", "N/A"),
                "likes": stats.get("likeCount", "N/A"),
                "comments": stats.get("commentCount", "N/A"),
                "published_at": published_str,
            }

    return details


def get_video_comments(video_id: str, max_comments: int = 5) -> List[dict]:
    if max_comments <= 0:
        return []

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        comments = []
        next_page_token = None

        while len(comments) < max_comments:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_comments,
                pageToken=next_page_token,
                order="relevance",
            )
            response = request.execute()

            for item in response.get("items", []):
                if len(comments) >= max_comments:
                    break

                snippet = item.get("snippet", {})
                top_comment = snippet.get("topLevelComment", {}).get("snippet", {})

                comments.append(
                    {
                        "author": top_comment.get("authorDisplayName", "Unknown"),
                        "text": top_comment.get("textDisplay", ""),
                        "likes": top_comment.get("likeCount", 0),
                        "published": top_comment.get("publishedAt", "")[:10],
                    }
                )

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return comments

    except Exception as e:
        print(f"Error fetching comments: {e}", flush=True)
        return []


def search_videos(
    query: str,
    order: str,
    published_after: Optional[str],
    max_results: int,
) -> List[dict]:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    all_results = []
    video_ids = []
    next_page_token = None

    while len(all_results) < max_results:
        current_max = min(50, max_results - len(all_results))

        params = {
            "q": query,
            "type": "video",
            "part": "snippet",
            "order": order,
            "maxResults": current_max,
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        if published_after:
            params["publishedAfter"] = published_after

        request = youtube.search().list(**params)
        response = request.execute()

        for item in response.get("items", []):
            if len(all_results) >= max_results:
                break

            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            video_ids.append(video_id)

            all_results.append(
                {
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "video_id": video_id,
                    "description": snippet.get("description", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

        print(f"Searching: {len(all_results)}/{max_results}...", flush=True)

    _enrich_results_with_details(all_results, video_ids)

    return all_results


def get_channel_details(channel_id: str) -> dict:
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        request = youtube.channels().list(
            part="snippet,statistics,contentDetails", id=channel_id
        )
        response = request.execute()

        if response.get("items"):
            item = response["items"][0]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            return {
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "custom_url": snippet.get("customUrl", ""),
                "published_at": snippet.get("publishedAt", ""),
                "country": snippet.get("country", ""),
                "thumbnails": snippet.get("thumbnails", {}),
                "view_count": stats.get("viewCount", "0"),
                "subscriber_count": stats.get("subscriberCount", "0"),
                "video_count": stats.get("videoCount", "0"),
                "uploads_playlist_id": content.get("relatedPlaylists", {}).get(
                    "uploads", ""
                ),
            }
    except Exception as e:
        print(f"Error fetching channel details: {e}", flush=True)

    return {}


def search_channel_videos(
    channel_name: str,
    order: str,
    max_results: int,
) -> tuple:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    print(f"Searching for channel: {channel_name}...", flush=True)

    search_params = {
        "q": channel_name,
        "type": "channel",
        "part": "snippet",
        "maxResults": 1,
    }

    search_request = youtube.search().list(**search_params)
    search_response = search_request.execute()

    if not search_response.get("items"):
        print(f"Channel not found: {channel_name}", flush=True)
        return {}, []

    channel_id = search_response["items"][0]["id"].get("channelId")
    channel_title = search_response["items"][0]["snippet"].get("title")

    print(f"Channel found: {channel_title} (ID: {channel_id})", flush=True)

    channel_details = get_channel_details(channel_id)

    print(f"Fetching channel videos...", flush=True)

    all_results = []
    video_ids = []
    next_page_token = None

    while len(all_results) < max_results:
        current_max = min(50, max_results - len(all_results))

        params = {
            "channelId": channel_id,
            "type": "video",
            "part": "snippet",
            "order": order,
            "maxResults": current_max,
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        request = youtube.search().list(**params)
        response = request.execute()

        for item in response.get("items", []):
            if len(all_results) >= max_results:
                break

            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            video_ids.append(video_id)

            all_results.append(
                {
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "video_id": video_id,
                    "description": snippet.get("description", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

        print(f"Searching: {len(all_results)}/{max_results}...", flush=True)

    _enrich_results_with_details(all_results, video_ids)

    return channel_details, all_results


def format_search_results(
    results: List[dict],
    show_description: bool = False,
    max_comments: int = 0,
    channel_details: dict = None,
) -> str:
    lines = []

    if channel_details:
        lines.append("## Channel Statistics")
        lines.append("")
        lines.append(f"   **Name:** {channel_details.get('title', 'N/A')}")
        lines.append(f"   **Description:** {channel_details.get('description', 'N/A')}")
        lines.append(
            f"   **Custom URL:** {channel_details.get('custom_url', 'N/A')}"
        )
        lines.append(f"   **Country:** {channel_details.get('country', 'N/A')}")
        lines.append(
            f"   **Subscribers:** {format_number(channel_details.get('subscriber_count', '0'))}"
        )
        lines.append(
            f"   **Total Videos:** {format_number(channel_details.get('video_count', '0'))}"
        )
        lines.append(
            f"   **Total Views:** {format_number(channel_details.get('view_count', '0'))}"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

    if not results:
        return "No results found."

    for i, r in enumerate(results, 1):
        tags_str = ", ".join(r.get("tags", [])) if r.get("tags") else "N/A"

        lines.append(f"{i}. {r['title']}")
        lines.append("")
        lines.append(f"   Channel: {r['channel']}")
        lines.append(f"   URL: {r['url']}")
        lines.append(f"   Language: {r.get('default_language', 'N/A')}")
        lines.append(f"   Published: {r['published_at']}")
        lines.append(f"   Duration: {r['duration']}")
        lines.append(f"   Views: {format_number(r.get('views', 'N/A'))}")
        lines.append(f"   Likes: {format_number(r.get('likes', 'N/A'))}")
        lines.append(f"   Comments: {format_number(r.get('comments', 'N/A'))}")
        lines.append(f"   Tags: {tags_str}")

        if show_description and r.get("description"):
            lines.append("")
            lines.append(f"   Description: {r['description']}")

        if max_comments > 0 and r.get("comments_list"):
            lines.append("")
            lines.append(f"   Top {len(r['comments_list'])} Comments:")
            for j, c in enumerate(r["comments_list"], 1):
                lines.append(f"      {j}. {c['author']} ({c['likes']} likes)")
                lines.append(f"         {c['text'][:200]}")
                if len(c["text"]) > 200:
                    lines.append(f"         ...")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="YouTube CLI - Extract transcripts or search videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract transcript from video
  youtube "https://youtube.com/watch?v=VIDEO_ID" -o ./output

  # Search videos
  youtube -s "python tutorial" -o ./output
  youtube --search "topic" --maxResults 20 -o ./output

  # Channel search
  youtube --channel "Channel Name" -o ./output

  # Transcript extraction supports proxy (search does not)
  export USE_PROXY="true"
  export PROXY_USER="webshare_user"
  export PROXY_PASS="webshare_pass"
  youtube "URL" -o ./output
""",
    )

    parser.add_argument("input", nargs="?", help="URL, search term, or file with URLs")
    parser.add_argument(
        "extra_inputs", nargs="*", help="Additional URLs or search terms"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Output directory (required)"
    )
    parser.add_argument("--search", "-s", action="store_true", help="Search mode")
    parser.add_argument(
        "--order",
        default="relevance",
        choices=["relevance", "date", "viewCount", "rating"],
        help="Sort order (default: relevance)"
    )
    parser.add_argument(
        "--publishedAfter",
        help="Filter videos published after date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--maxResults", type=int, default=10,
        help="Maximum results to return (default: 10)"
    )
    parser.add_argument(
        "--comments", "-c", type=int, default=0,
        help="Number of top comments to include per video"
    )
    parser.add_argument(
        "--description", "-d", action="store_true",
        help="Include video description in output"
    )
    parser.add_argument(
        "--channel", action="store_true",
        help="Channel search mode"
    )

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    validate_environment()
    validate_output_path(args.output)

    if args.publishedAfter and not validate_date(args.publishedAfter):
        print(f"Error: invalid date '{args.publishedAfter}'", flush=True)
        print("Use format: YYYY-MM-DD (e.g. 2024-01-15)", flush=True)
        sys.exit(1)

    if args.publishedAfter:
        args.publishedAfter = f"{args.publishedAfter}T00:00:00Z"

    is_search = args.search or args.input == "search"
    is_channel = args.channel or args.input == "channel"

    if is_channel:
        if args.input == "channel":
            channel_name = args.extra_inputs[0] if args.extra_inputs else ""
        else:
            channel_name = args.input

        if not channel_name:
            print("Error: channel name is required", flush=True)
            sys.exit(1)

        channel_details, results = search_channel_videos(
            channel_name=channel_name,
            order=args.order,
            max_results=args.maxResults,
        )

        if args.comments > 0:
            print(f"Fetching top {args.comments} comments...", flush=True)
            for r in results:
                video_id = r.get("video_id")
                if video_id:
                    comments = get_video_comments(video_id, args.comments)
                    r["comments_list"] = comments

        output = format_search_results(
            results,
            show_description=args.description,
            max_comments=args.comments,
            channel_details=channel_details,
        )

        flags = []
        if args.order != "relevance":
            flags.append(f"--order {args.order}")
        if args.maxResults != 10:
            flags.append(f"--maxResults {args.maxResults}")
        if args.comments > 0:
            flags.append(f"--comments {args.comments}")
        if args.description:
            flags.append(f"--description")

        flags_str = " ".join(flags)
        channel_sanitized = re.sub(r'[<>:"/\\|?*]', "_", channel_name)
        filename = f"youtube channel {channel_sanitized} {flags_str}".strip()
        output_path = os.path.join(args.output, f"{filename}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# YouTube Channel: {channel_name}\n\n")
            if flags:
                f.write(f"**Flags:** {flags_str}\n\n")
            f.write("---\n\n")
            f.write(output)

        print(f"Saved: {output_path}", flush=True)

    elif is_search:
        if args.input == "search":
            query = args.extra_inputs[0] if args.extra_inputs else ""
            extra_inputs = (
                args.extra_inputs[1:] if len(args.extra_inputs) > 1 else []
            )
        else:
            query = args.input
            extra_inputs = args.extra_inputs

        if not query:
            print("Error: search term is required", flush=True)
            sys.exit(1)

        if extra_inputs:
            query = query + " " + " ".join(extra_inputs)

        published_after = None
        if args.publishedAfter:
            published_after = f"{args.publishedAfter}T00:00:00Z"

        results = search_videos(
            query=query,
            order=args.order,
            published_after=published_after,
            max_results=args.maxResults,
        )

        if args.comments > 0:
            print(f"Fetching top {args.comments} comments...", flush=True)
            for r in results:
                video_id = r.get("video_id")
                if video_id:
                    comments = get_video_comments(video_id, args.comments)
                    r["comments_list"] = comments

        output = format_search_results(
            results, show_description=args.description, max_comments=args.comments
        )

        flags = []
        if args.order != "relevance":
            flags.append(f"--order {args.order}")
        if args.publishedAfter:
            flags.append(f"--publishedAfter {args.publishedAfter}")
        if args.maxResults != 10:
            flags.append(f"--maxResults {args.maxResults}")
        if args.comments > 0:
            flags.append(f"--comments {args.comments}")
        if args.description:
            flags.append(f"--description")

        flags_str = " ".join(flags)
        query_sanitized = re.sub(r'[<>:"/\\|?*]', "_", query)
        filename = f"youtube search {query_sanitized} {flags_str}".strip()
        output_path = os.path.join(args.output, f"{filename}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# YouTube Search: {query}\n\n")
            if flags:
                f.write(f"**Flags:** {flags_str}\n\n")
            f.write("---\n\n")
            f.write(output)

        print(f"Saved: {output_path}", flush=True)

    else:
        urls = [args.input] + args.extra_inputs
        output_dir = args.output
        direct_urls = []
        url_file = None

        for entrada in urls:
            if entrada.endswith(".txt") or entrada.endswith(".md"):
                url_file = entrada
            else:
                direct_urls.append(entrada)

        if url_file and direct_urls:
            print(
                "Error: cannot use URL file together with direct URLs",
                flush=True,
            )
            sys.exit(1)

        if url_file:
            process_file(url_file, output_dir)
        else:
            for url in direct_urls:
                process_url(url, output_dir)


if __name__ == "__main__":
    main()

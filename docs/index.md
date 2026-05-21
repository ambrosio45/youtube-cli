# YouTube CLI - Documentation

## Overview

YouTube CLI is a command-line tool for extracting YouTube video transcripts and searching YouTube videos.

## Features

- Extract transcripts from single or multiple videos
- Batch processing from URL files
- Search videos by query
- Search all videos from a channel
- Get video metadata (views, likes, comments, etc.)
- Download top comments

## Quick Start

### 1. Install

```bash
pip install -e git+https://github.com/pedro/youtube-cli.git
```

### 2. Configure API Key

```bash
export YOUTUBE_API_KEY="your_youtube_api_key"
```

### 3. Extract Transcript

```bash
youtube "https://www.youtube.com/watch?v=VIDEO_ID" -o ./output
```

## Usage Examples

### Transcript Extraction

```bash
# Single video
youtube "URL" -o ./transcripts

# Multiple videos
youtube "URL1" "URL2" "URL3" -o ./transcripts

# From file (urls.txt contains one URL per line)
youtube urls.txt -o ./transcripts
```

### Video Search

```bash
# Basic search
youtube -s "python tutorial" -o ./output

# Search with filters
youtube -s "python tutorial" --order date --publishedAfter 2024-01-01 --maxResults 20 -o ./output
```

### Channel Search

```bash
# Find channel and list all videos
youtube --channel "Channel Name" -o ./output

# Most viewed videos from channel
youtube --channel "Channel Name" --order viewCount --maxResults 50 -o ./output
```

## Command Reference

### Required Arguments

- `entrada`: URL or search term
- `-o, --output`: Output directory (required)

### Optional Arguments

| Argument | Description |
|----------|-------------|
| `-s, --search` | Search mode |
| `--channel` | Channel search mode |
| `--order` | Sort by: relevance, date, viewCount, rating |
| `--maxResults N` | Maximum results (default: 10) |
| `--publishedAfter YYYY-MM-DD` | Filter by publish date |
| `-c N, --comments N` | Include top N comments |
| `-d, --description` | Include video description |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `YOUTUBE_API_KEY` | Yes | YouTube Data API key |
| `USE_PROXY` | No | Set to "true" to enable proxy |
| `PROXY_USER` | No | Proxy username |
| `PROXY_PASS` | No | Proxy password |

## Troubleshooting

### "YOUTUBE_API_KEY não configurada"

Set the `YOUTUBE_API_KEY` environment variable:

```bash
export YOUTUBE_API_KEY="your_key"
```

### Transcript extraction fails

- Video might not have captions
- Video might be region-restricted
- Try with proxy if behind a firewall

### API Quota Exceeded

- YouTube API has daily quota (default 10,000 units)
- Reduce `--maxResults` or implement caching
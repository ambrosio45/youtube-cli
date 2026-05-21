---
name: youtube-cli
description: Extract YouTube video transcripts from youtube links, search videos, and explore channels. Use when user mentions YouTube, transcripts, youtube links, video extraction, or exploring channels.
---

# YouTube CLI Skill

## Quick Start

### Installation

```bash
pip install -e git+https://github.com/pedro/youtube-cli.git
```

### Configuration

```bash
export YOUTUBE_API_KEY="your_youtube_api_key"
```

### Basic Usage

```bash
youtube "https://youtube.com/watch?v=VIDEO_ID" -o ./output
```

---

## Usage Modes

### 1. Extract Transcripts

```bash
# Single video
youtube "URL" -o ./output

# Multiple videos
youtube "URL1" "URL2" "URL3" -o ./output

# From file (processes ALL youtube links found in the file)
youtube urls.txt -o ./output
```

### 2. Search Videos

```bash
# Basic search
youtube -s "search term" -o ./output

# With filters
youtube -s "term" --maxResults 20 --order date -o ./output

# Filter by date
youtube -s "term" --publishedAfter 2024-01-01 -o ./output
```

### 3. Explore Channels

```bash
# Find channel and list all videos
youtube --channel "Channel Name" -o ./output

# With options
youtube --channel "Channel Name" --maxResults 50 --order date -o ./output
```

---

## Command Reference

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | **Required.** Output directory | - |
| `-s, --search` | Search mode | False |
| `--channel` | Channel search mode | False |
| `--order` | Sort: relevance, date, viewCount, rating | relevance |
| `--maxResults N` | Maximum results | 10 |
| `--publishedAfter YYYY-MM-DD` | Filter by publish date | None |
| `-c N, --comments N` | Include top N comments | 0 |
| `-d, --description` | Include video description | False |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `YOUTUBE_API_KEY` | Yes | YouTube Data API key |
| `USE_PROXY` | No | Set "true" to enable proxy |
| `PROXY_USER` | No | Proxy username |
| `PROXY_PASS` | No | Proxy password |

---

## ⚠️ Rate Limiting Warning

Making many consecutive API calls may result in IP ban from YouTube.

**For sustained or batch operations, use Webshare proxy:**
```bash
export USE_PROXY="true"
export PROXY_USER="your_webshare_user"
export PROXY_PASS="your_webshare_pass"
```

Note: Proxy configuration only works with Webshare proxy credentials.

---

## Output Format

Each mode generates `.md` files in the output directory:

- **Transcript**: One file per video with metadata + transcript
- **Search**: Single file with all search results
- **Channel**: Single file with channel stats + all videos

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "YOUTUBE_API_KEY não configurada" | Set the environment variable first |
| Transcript extraction fails | Video may not have captions available |
| "IP banned" or rate limit errors | Use proxy or wait before retrying |

For complete documentation, see [REFERENCE.md](REFERENCE.md).
For examples, see [EXAMPLES.md](EXAMPLES.md).
For troubleshooting guide, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
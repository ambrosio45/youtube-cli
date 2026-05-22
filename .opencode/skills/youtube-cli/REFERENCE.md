# YouTube CLI - Complete Reference

## Installation

### From Git

```bash
pip install -e git+https://github.com/ambrosio45/youtube-cli.git
```

### Development Mode

```bash
git clone https://github.com/ambrosio45/youtube-cli.git
cd youtube-cli
pip install -e .
```

---

## Configuration

### Environment Variables

Create a `.env` file or export variables:

```bash
# Required
export YOUTUBE_API_KEY="your_api_key_here"

# Optional - for proxy support
export USE_PROXY="true"
export PROXY_USER="your_webshare_username"
export PROXY_PASS="your_webshare_password"
```

### Getting a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Go to Credentials and create an API Key
5. Set quota as needed (default: 10,000 units/day)

---

## Commands

### Transcript Extraction

Extract transcripts from videos. Supports single URLs, multiple URLs, or files containing URLs.

```bash
# Single video
youtube "https://www.youtube.com/watch?v=VIDEO_ID" -o ./output

# Multiple videos
youtube "URL1" "URL2" "URL3" -o ./output

# From file (extracts ALL YouTube links found in the file)
youtube urls.txt -o ./output
youtube links.md -o ./output
```

**Important:** When providing a file, the tool will process every YouTube link found in the file content.

### Video Search

Search for videos by query string.

```bash
# Basic search
youtube -s "python tutorial" -o ./output

# Search with sorting
youtube -s "term" --order date -o ./output        # Most recent
youtube -s "term" --order viewCount -o ./output   # Most viewed
youtube -s "term" --order rating -o ./output      # Highest rated

# Filter by date (YYYY-MM-DD)
youtube -s "term" --publishedAfter 2024-01-01 -o ./output

# Limit results
youtube -s "term" --maxResults 50 -o ./output
```

### Channel Exploration

Search for a channel and list all its videos.

```bash
# Basic channel search
youtube --channel "Channel Name" -o ./output

# With options
youtube --channel "Channel Name" --maxResults 100 -o ./output
youtube --channel "Channel Name" --order date -o ./output
```

---

## Options Reference

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output PATH` | **Required.** Output directory for files | - |
| `-s, --search` | Enable search mode | False |
| `--channel` | Enable channel search mode | False |

### Search Options

| Option | Description | Default |
|--------|-------------|---------|
| `--order ORDER` | Sort order: relevance, date, viewCount, rating | relevance |
| `--maxResults N` | Maximum number of results to return | 10 |
| `--publishedAfter DATE` | Filter videos published after date (YYYY-MM-DD) | None |
| `--publishedBefore DATE` | Filter videos published before date (YYYY-MM-DD) | None |

### Output Options

| Option | Description | Default |
|--------|-------------|---------|
| `-c N, --comments N` | Include top N comments per video | 0 |
| `-d, --description` | Include video description in output | False |

---

## Output Format

### Transcript Output

```markdown
# Video Title

**Channel:** Channel Name
**URL:** https://youtube.com/watch?v=...
**Language:** en
**Published:** 01/01/2024
**Duration:** 12:34
**Views:** 1.234
**Likes:** 567
**Comments:** 89
**Tags:** tag1, tag2

---

Transcript text content here...
```

### Search Output

```markdown
# YouTube Search: search term

**Flags:** --maxResults 10 --order date

---

1. Video Title

   Channel: Channel Name
   URL: https://youtube.com/watch?v=...
   Language: en
   Published: 01/01/2024
   Duration: 12:34
   Views: 1.234
   Likes: 567
   Comments: 89
   Tags: tag1, tag2

2. Another Video
    ...
```

### Channel Output

```markdown
# YouTube Channel: Channel Name

**Flags:** --maxResults 50 --order date

---

## Channel Statistics

   **Name:** Channel Name
   **Subscribers:** 1.234.567
   **Total Videos:** 890
   **Total Views:** 123.456.789

---

1. Video Title
    ...
```

---

## Environment Variables Detail

| Variable | Required | Description |
|----------|----------|-------------|
| `YOUTUBE_API_KEY` | Yes | YouTube Data API v3 key |
| `USE_PROXY` | No | Enable proxy: "true" or "false" |
| `PROXY_USER` | No | Username for proxy authentication |
| `PROXY_PASS` | No | Password for proxy authentication |

---

## API Quotas

YouTube Data API v3 has daily quotas:

- Default: 10,000 units/day
- Each search request: 100 units
- Each video list request: 1 unit (when fetching individual videos)

**Tips to minimize quota usage:**
- Use `--maxResults` wisely
- Process URLs in batches
- Enable caching if implementing wrapper

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (invalid arguments, API failure, etc.) |

---

For examples, see [EXAMPLES.md](EXAMPLES.md).
For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
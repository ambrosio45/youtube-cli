# YouTube CLI

CLI tool for extracting YouTube video transcripts and searching YouTube videos.

## Installation

```bash
pip install -e git+https://github.com/pedro/youtube-cli.git
```

Or in development mode:

```bash
git clone https://github.com/pedro/youtube-cli.git
cd youtube-cli
pip install -e .
```

## Configuration

Before using the tool, set your YouTube API key:

```bash
# Linux/Mac
export YOUTUBE_API_KEY="your_api_key_here"

# Windows (Command Prompt)
set YOUTUBE_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:YOUTUBE_API_KEY="your_api_key_here"
```

### Optional: Proxy Configuration

If behind a proxy:

```bash
export USE_PROXY="true"
export PROXY_USER="your_username"
export PROXY_PASS="your_password"
```

## Usage

### Extract Transcript from Video

```bash
youtube "https://www.youtube.com/watch?v=VIDEO_ID" -o ./output
```

Extract from multiple videos:

```bash
youtube "URL1" "URL2" "URL3" -o ./output
```

Or use a file containing URLs (one per line):

```bash
youtube urls.txt -o ./output
```

### Search Videos

```bash
youtube --search "python tutorial" -o ./output
youtube -s "search term" --maxResults 20 -o ./output
youtube -s "term" --order date --publishedAfter 2024-01-01 -o ./output
```

### Channel Search

```bash
youtube --channel "Channel Name" -o ./output
youtube --channel "Channel Name" --maxResults 50 --order date -o ./output
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output` | **Required.** Output directory | - |
| `-s, --search` | Search mode | False |
| `--channel` | Channel search mode | False |
| `--order` | Sort order: relevance, date, viewCount, rating | relevance |
| `--maxResults` | Max results to return | 10 |
| `--publishedAfter` | Filter by date (YYYY-MM-DD) | - |
| `-c, --comments N` | Include top N comments | 0 |
| `-d, --description` | Show video description | False |

## Output Format

### Transcript Output

```markdown
# Video Title

**Canal:** Channel Name
**URL:** https://youtube.com/watch?v=...
**Idioma:** en
**Publicado em:** 01/01/2024
**Duração:** 12:34
**Views:** 1.234
**Likes:** 567
**Comentários:** 89
**Tags:** tag1, tag2

---

Transcript text here...
```

### Search/Channel Output

```markdown
# YouTube Search: search term

**Flags:** --maxResults 10

---

1. Video Title

   Canal: Channel Name
   URL: https://youtube.com/watch?v=...
   Idioma: en
   Publicação: 01/01/2024
   Duração: 12:34
   Views: 1.234
   Likes: 567
   Comentários: 89
   Tags: tag1, tag2
```

## Getting a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Go to Credentials and create an API Key
5. Set the quota as needed (default is 10,000 units/day)

## License

MIT
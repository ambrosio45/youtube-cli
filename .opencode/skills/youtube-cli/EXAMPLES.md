# YouTube CLI - Usage Examples

## Basic Examples

### Extract a Single Transcript

```bash
youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o ./transcripts
```

### Extract Multiple Transcripts

```bash
youtube "URL1" "URL2" "URL3" -o ./transcripts
```

---

## Search Examples

### Find Python Tutorials

```bash
youtube -s "python tutorial for beginners" -o ./search-results
```

### Find Recent Videos Only

```bash
youtube -s "tech review" --order date --publishedAfter 2024-01-01 -o ./recent
```

### Find Most Viewed Videos

```bash
youtube -s "music" --order viewCount --maxResults 20 -o ./popular
```

---

## Channel Examples

### List All Videos from a Channel

```bash
youtube --channel "Channel Name" -o ./channel-output
```

### Get Most Viewed Videos from Channel

```bash
youtube --channel "Channel Name" --order viewCount --maxResults 50 -o ./channel-output
```

---

## Batch Processing

### Process URLs from a File

```bash
# Create a file with URLs (one per line)
echo "https://youtube.com/watch?v=VIDEO1" > urls.txt
echo "https://youtube.com/watch?v=VIDEO2" >> urls.txt
echo "https://youtu.be/VIDEO3" >> urls.txt

# Process all URLs
youtube urls.txt -o ./batch-output
```

### Process All Links from a Markdown File

```bash
# If you have a README or notes file with YouTube links
youtube my-notes.md -o ./output
```

**Warning:** The tool extracts ALL YouTube URLs found in the file, not just one per line.

---

## Advanced Options

### Include Video Descriptions

```bash
youtube -s "search" -d -o ./output
```

### Include Top Comments

```bash
youtube -s "search" -c 10 -o ./output  # Top 10 comments per video
```

### Combine Multiple Options

```bash
youtube -s "python" --order date --publishedAfter 2024-01-01 --maxResults 50 -c 5 -d -o ./output
```

---

## Proxy Usage

For batch operations or when YouTube blocks your IP:

```bash
export USE_PROXY="true"
export PROXY_USER="your_webshare_username"
export PROXY_PASS="your_webshare_password"

youtube -s "batch search" -o ./output
youtube urls.txt -o ./batch-output
```

---

## Workflow Examples

### Research Workflow

1. Search for relevant videos:
   ```bash
   youtube -s "topic research" --maxResults 20 -o ./research
   ```

2. Extract transcripts from interesting ones:
   ```bash
   youtube "URL1" "URL2" "URL3" -o ./transcripts
   ```

3. Get channel info for creators:
   ```bash
   youtube --channel "Creator Name" -o ./channels
   ```

### Content Archive Workflow

1. Get all videos from a channel:
   ```bash
   youtube --channel "Channel Name" --maxResults 100 -o ./archive
   ```

2. Batch extract transcripts:
   ```bash
   youtube urls.txt -o ./transcripts
   ```

---

## Common Issues

### Rate Limiting

If you get rate limited:
```bash
# Wait and retry with proxy
export USE_PROXY="true"
export PROXY_USER="webshare_user"
export PROXY_PASS="webshare_pass"
```

### No Captions Available

Some videos don't have captions:
- Try different videos
- Video may be region-restricted
- Content owner disabled captions

---

For troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
For complete reference, see [REFERENCE.md](REFERENCE.md).
# YouTube CLI - Troubleshooting Guide

## Common Errors

### "YOUTUBE_API_KEY não configurada"

**Cause:** Environment variable not set.

**Solution:**
```bash
export YOUTUBE_API_KEY="your_api_key_here"
```

---

### "URL inválida" / Invalid URL

**Cause:** URL format not recognized.

**Solution:**
- Ensure URL is a valid YouTube URL
- Supported formats:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`
  - `https://www.youtube.com/shorts/VIDEO_ID`
  - `https://www.youtube.com/v/VIDEO_ID`

---

### Transcript Extraction Fails

**Causes:**
- Video doesn't have captions
- Video is region-restricted
- Content owner disabled captions

**Solutions:**
- Try a different video
- Use a proxy if content is region-locked
- Video may not be available in your region

---

### IP Banned / Rate Limited

**Cause:** Too many API requests in short time.

**Solution:**
- Wait 24 hours (quota usually resets)
- Use Webshare proxy:
  ```bash
  export USE_PROXY="true"
  export PROXY_USER="your_webshare_user"
  export PROXY_PASS="your_webshare_pass"
  ```

---

### "Arquivo não encontrado"

**Cause:** File path doesn't exist.

**Solution:**
- Check that the file exists
- Use full path if relative path doesn't work
- Ensure you have read permissions

---

### Empty Results / No Videos Found

**Causes:**
- Search query returns no results
- Channel name not found
- API quota exceeded

**Solutions:**
- Try different search terms
- Check channel name spelling
- Verify API key is valid
- Check quota usage in Google Cloud Console

---

### Proxy Authentication Failed

**Cause:** Invalid proxy credentials.

**Solution:**
- Verify Webshare proxy credentials
- Ensure `PROXY_USER` and `PROXY_PASS` are correct
- Webshare proxy is the only supported proxy type

---

## API Quota Issues

### Understanding Quotas

YouTube Data API v3 default quota: **10,000 units/day**

| Operation | Cost |
|-----------|------|
| Search | 100 units |
| Video list (single) | 1 unit |
| Channel list | 1 unit |

### Avoiding Quota Issues

1. **Use `--maxResults` wisely** - Don't fetch more than needed
2. **Batch URL processing** - Process URLs in groups
3. **Cache results** - Store results for later use
4. **Monitor usage** - Check Google Cloud Console regularly

---

## Environment Setup Issues

### Python Version

Requires Python 3.8 or higher.

```bash
python --version
```

### pip install fails

```bash
# Try with verbose output
pip install -e git+https://github.com/pedro/youtube-cli.git -v

# Or install dependencies first
pip install youtube-transcript-api google-api-python-client
pip install -e git+https://github.com/pedro/youtube-cli.git
```

---

## Getting Help

- See [REFERENCE.md](REFERENCE.md) for complete documentation
- See [EXAMPLES.md](EXAMPLES.md) for usage examples
- Report issues at: https://github.com/pedro/youtube-cli/issues
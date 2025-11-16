# 📦 HƯỚNG DẪN: Cài đặt yt-dlp để lấy metadata đầy đủ

## ✅ ĐÃ CẬP NHẬT

Script `auto_extractor_json.py` đã được cập nhật để lấy **đầy đủ metadata** từ YouTube video:

- ✅ Title (đã có)
- ✅ Description
- ✅ Tags/Keywords
- ✅ Hashtags (extract từ description)
- ✅ Playlist
- ✅ Thumbnail (URL)
- ✅ Thumbnails (tất cả sizes)
- ✅ Thumbnail text
- ✅ Timestamp 1, 2, 3 (extract từ description)
- ✅ Category
- ✅ Visibility
- ✅ Age restricted
- ✅ View count, Like count, Comment count
- ✅ Duration
- ✅ Upload date
- ✅ Channel info
- ✅ Location
- ✅ Language
- ✅ License
- ✅ Và nhiều thông tin khác...

---

## 📦 CÀI ĐẶT yt-dlp

### Trên máy local (Windows)

```powershell
# Nếu dùng venv
.\venv\Scripts\activate
pip install yt-dlp

# Hoặc không dùng venv
pip install yt-dlp
```

### Trên server (trong n8n container)

```bash
# Vào container
docker exec -it n8n-data-n8n-1 sh

# Activate venv và cài yt-dlp
source /opt/venv/bin/activate
pip install yt-dlp

# Hoặc cài system-wide (không khuyến nghị)
pip install --break-system-packages yt-dlp
```

### Hoặc cập nhật Dockerfile

Thêm vào `~/n8n-data/Dockerfile`:

```dockerfile
FROM n8nio/n8n
USER root
RUN apk add --no-cache ffmpeg python3 py3-pip
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install scrapetube youtube-transcript-api yt-dlp google-auth google-auth-oauthlib google-api-python-client
USER node
```

Sau đó rebuild container:
```bash
cd ~/n8n-data
docker compose build n8n
docker compose restart n8n
```

---

## 🧪 TEST SCRIPT

Sau khi cài yt-dlp, test script:

```bash
# Trên server
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "dQw4w9WgXcQ"'
```

Kết quả sẽ có đầy đủ metadata trong JSON output.

---

## 📋 OUTPUT JSON MỚI

Script giờ sẽ trả về JSON với cấu trúc:

```json
{
  "success": true,
  "videoId": "...",
  "title": "...",
  "url": "...",
  "transcript": "...",
  "transcriptSegments": [...],
  "wordCount": 1234,
  "transcriptLanguage": "vi",
  "description": "...",
  "tags": ["tag1", "tag2"],
  "keywords": ["tag1", "tag2"],
  "hashtags": ["#hashtag1", "#hashtag2"],
  "playlist": "Playlist Name",
  "playlistId": "...",
  "thumbnail": "https://...",
  "thumbnails": [...],
  "thumbnailText": "...",
  "timestamp1": 123,
  "timestamp2": 456,
  "timestamp3": 789,
  "category": "Education",
  "categoryId": "27",
  "visibility": "public",
  "ageRestricted": false,
  "viewCount": 12345,
  "likeCount": 567,
  "commentCount": 89,
  "duration": 3600,
  "uploadDate": "20240101",
  "channel": "Channel Name",
  "channelId": "...",
  "channelUrl": "...",
  "uploader": "...",
  "uploaderId": "...",
  "location": "...",
  "language": "vi",
  "license": "...",
  "timestamp": "2025-01-20T..."
}
```

---

## ⚠️ LƯU Ý

1. **Nếu yt-dlp chưa cài:** Script vẫn chạy được nhưng chỉ có transcript, không có metadata
2. **yt-dlp cần internet:** Đảm bảo container có kết nối internet
3. **Rate limiting:** YouTube có thể giới hạn số request, không gọi quá nhiều lần

---

## 🔄 CẬP NHẬT REQUIREMENTS.TXT

File `requirements.txt` đã được cập nhật với `yt-dlp`.

Trên server, cài lại dependencies:

```bash
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && pip install -r /home/node/scripts/requirements.txt'
```

---

**Sau khi cài yt-dlp, script sẽ lấy được đầy đủ metadata!** ✅


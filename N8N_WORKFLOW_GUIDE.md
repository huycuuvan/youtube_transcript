# Hướng dẫn Flow n8n: YouTube Transcript → Video Hoàn chỉnh

## 📋 Tổng quan Flow

Flow này tự động:
1. ✅ Lấy transcript từ kênh YouTube (tự động chạy định kỳ)
2. ✅ (Optional) Lưu vào Google Sheets
3. ✅ Dịch transcript sang tiếng Anh (xử lý >10k từ)
4. ✅ Tóm tắt và tạo 3-5 image prompts
5. ✅ Generate ảnh từ prompts
6. ✅ Chuyển text thành voice tiếng Anh (TTS)
7. ✅ Ghép ảnh + voice → video hoàn chỉnh
8. ✅ Lưu metadata video

---

## 🔧 Các Node trong Flow

### 1. **Schedule Trigger** (Cron)
- **Chức năng**: Chạy tự động theo lịch
- **Cấu hình**: Mỗi 6 giờ (có thể thay đổi)
- **Output**: Trigger event

### 2. **Execute Script - Get Transcript**
- **Chức năng**: Chạy Python script để lấy transcript
- **Command**: 
  ```bash
  cd /path/to/youtube_extractor && python3 auto_extractor.py --output-json
  ```
- **Output**: JSON với `videoId`, `title`, `transcript`

### 3. **Parse Script Output**
- **Chức năng**: Parse output từ script thành JSON chuẩn
- **Code**: Xử lý cả JSON và text output
- **Output**: 
  ```json
  {
    "videoId": "abc123",
    "title": "Video Title",
    "transcript": "Full transcript text...",
    "timestamp": "2025-01-20T..."
  }
  ```

### 4. **Check Transcript Exists**
- **Chức năng**: Kiểm tra transcript có tồn tại không
- **Logic**: Nếu transcript rỗng → dừng flow
- **Output**: Continue nếu có transcript

### 5. **Save to Google Sheets (Optional)**
- **Chức năng**: Lưu transcript vào Google Sheets
- **Cấu hình**: 
  - Sheet ID từ environment variable
  - Columns: Timestamp, Title, VideoID, Transcript
- **Note**: Node này có thể bỏ qua nếu không cần

### 6. **Chunk Transcript**
- **Chức năng**: Chia transcript thành các chunk nhỏ (~4000 ký tự)
- **Lý do**: Tránh vượt token limit khi dịch
- **Output**: Nhiều items, mỗi item là 1 chunk

### 7. **Translate Chunk (NCA)**
- **Chức năng**: Gọi NCA Toolkit API để dịch từng chunk
- **Endpoint**: `http://nca:8080/api/llm/translate`
- **Body**:
  ```json
  {
    "text": "{{ chunkText }}",
    "sourceLang": "vi",
    "targetLang": "en",
    "model": "gpt-4o-mini"
  }
  ```
- **Output**: Translated text cho mỗi chunk

### 8. **Merge Translations**
- **Chức năng**: Gộp tất cả các chunk đã dịch thành 1 text hoàn chỉnh
- **Code**: Sort theo chunkIndex và join lại
- **Output**: Full translated text

### 9. **Summarize & Extract Image Prompts (NCA)**
- **Chức năng**: Tóm tắt và tạo image prompts
- **Endpoint**: `http://nca:8080/api/llm/summarize`
- **Body**:
  ```json
  {
    "text": "{{ translatedText }}",
    "task": "summarize_and_extract_visual_concepts",
    "model": "gpt-4o",
    "prompt": "Summarize in 8 bullet points. Create 3-5 image prompts..."
  }
  ```
- **Output**: Summary + array of image prompts

### 10. **Prepare Image Prompts**
- **Chức năng**: Parse response và tạo items cho mỗi prompt
- **Code**: Extract `imagePrompts` array, limit 3-5 prompts
- **Output**: Nhiều items, mỗi item là 1 prompt

### 11. **Generate Image (NCA)**
- **Chức năng**: Generate ảnh từ prompt
- **Endpoint**: `http://nca:8080/api/image/generate`
- **Body**:
  ```json
  {
    "prompt": "{{ imagePrompt }}",
    "size": "1920x1080",
    "model": "stable-diffusion-xl",
    "steps": 30
  }
  ```
- **Output**: Image URL/path

### 12. **Collect All Images**
- **Chức năng**: Thu thập tất cả ảnh đã generate
- **Code**: Sort và collect image URLs
- **Output**: Array of image URLs

### 13. **Text to Speech (NCA)**
- **Chức năng**: Chuyển translated text thành voice
- **Endpoint**: `http://nca:8080/api/audio/tts`
- **Body**:
  ```json
  {
    "text": "{{ translatedText }}",
    "voice": "en-US-Neural2-D",
    "speed": 1.0,
    "format": "mp3"
  }
  ```
- **Output**: Audio URL/path

### 14. **Prepare Video Data**
- **Chức năng**: Tính toán duration và chuẩn bị data cho video
- **Code**: 
  - Tính duration dựa trên word count
  - Chia duration cho số ảnh
- **Output**: Video composition data

### 15. **Compose Video (NCA)**
- **Chức năng**: Ghép ảnh + audio → video
- **Endpoint**: `http://nca:8080/api/video/compose`
- **Body**:
  ```json
  {
    "images": ["url1", "url2", ...],
    "audioUrl": "audio_url",
    "subtitles": "translated text",
    "durationPerImage": 10,
    "transitions": "fade",
    "outputFormat": "mp4",
    "resolution": "1920x1080"
  }
  ```
- **Output**: Final video URL/path

### 16. **Save Video Metadata**
- **Chức năng**: Lưu metadata video vào Google Sheets
- **Columns**: Timestamp, Title, VideoID, VideoURL, Status
- **Output**: Confirmation

---

## 🔗 Kết nối giữa các Node

```
Schedule Trigger
    ↓
Execute Script
    ↓
Parse Script Output
    ↓
Check Transcript Exists
    ├─→ Save to Google Sheets (Optional) [END]
    └─→ Chunk Transcript
            ↓
        Translate Chunk (NCA) [Loop qua từng chunk]
            ↓
        Merge Translations
            ├─→ Summarize & Extract Image Prompts (NCA)
            └─→ Text to Speech (NCA)
                    ↓
                Prepare Image Prompts
                    ↓
                Generate Image (NCA) [Loop qua từng prompt]
                    ↓
                Collect All Images
                    ↓
                Prepare Video Data
                    ↓
                Compose Video (NCA)
                    ↓
                Save Video Metadata
```

---

## ⚙️ Cấu hình Environment Variables

Thêm vào n8n environment variables:

```bash
# Google Sheets
GOOGLE_SHEET_ID=your_sheet_id_here
SHEET_NAME=Trang tính1

# YouTube
YOUTUBE_CHANNEL_URL=https://www.youtube.com/c/YourChannel

# NCA Toolkit (nếu cần override)
NCA_BASE_URL=http://nca:8080
```

---

## 📝 Lưu ý quan trọng

### 1. **Script Python cần output JSON**
- Script `auto_extractor.py` cần được cập nhật để output JSON format
- Xem file `auto_extractor_json.py` để tham khảo

### 2. **NCA Toolkit Endpoints**
- Đảm bảo NCA Toolkit đã cài đặt và chạy
- Các endpoint có thể khác tùy version NCA
- Kiểm tra API docs của NCA Toolkit

### 3. **Xử lý lỗi**
- Thêm Error Trigger nodes để handle lỗi
- Retry logic cho các API calls
- Logging để debug

### 4. **Performance**
- Transcript >10k từ sẽ mất thời gian
- Cân nhắc tăng timeout cho các HTTP Request nodes
- Có thể chạy parallel cho image generation

### 5. **Storage**
- Video output có thể rất lớn
- Cân nhắc upload lên S3/Cloud Storage
- Cleanup files cũ định kỳ

---

## 🚀 Cách Import vào n8n

1. Mở n8n interface
2. Click **Workflows** → **Import from File**
3. Chọn file `n8n_workflow_youtube_to_video.json`
4. Review và adjust các node theo cấu hình của bạn
5. Test với 1 video nhỏ trước
6. Activate workflow

---

## 🧪 Testing

1. **Test từng node riêng lẻ**:
   - Execute Script node với test data
   - Test NCA endpoints với curl/Postman

2. **Test flow nhỏ**:
   - Bỏ qua Schedule Trigger
   - Dùng Manual Trigger
   - Test với video ngắn (<1000 từ)

3. **Test full flow**:
   - Chạy với video thật
   - Monitor logs và errors
   - Kiểm tra output quality

---

## 📊 Monitoring

- Check n8n execution logs
- Monitor NCA Toolkit logs: `docker logs nca`
- Check Google Sheets để verify data
- Monitor disk space cho video files

---

## 🔄 Optimization Tips

1. **Parallel Processing**:
   - Image generation có thể chạy parallel
   - Translation chunks có thể xử lý song song

2. **Caching**:
   - Cache transcript nếu video đã xử lý
   - Cache translations để tránh dịch lại

3. **Queue System**:
   - Dùng Redis/RabbitMQ cho long-running tasks
   - Separate video composition thành background job

---

## ❓ Troubleshooting

### Script không output JSON
→ Cập nhật `auto_extractor.py` với `--output-json` flag

### NCA API timeout
→ Tăng timeout trong HTTP Request nodes (300s → 600s)

### Video composition fail
→ Check ffmpeg trong NCA container, verify image/audio URLs

### Google Sheets permission error
→ Re-authenticate Google Sheets credentials trong n8n

---

## 📚 Resources

- [n8n Documentation](https://docs.n8n.io/)
- [NCA Toolkit GitHub](https://github.com/nocodearchitects/nca-toolkit)
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)


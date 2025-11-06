# 📊 Tóm tắt Flow: YouTube → Video Hoàn chỉnh

## 🎯 Mục tiêu
Tự động hóa quy trình: Lấy transcript từ YouTube → Dịch → Tạo ảnh → Tạo voice → Ghép video

---

## 🔄 Flow Diagram (Đơn giản)

```
[Schedule] → [Get Transcript] → [Parse] → [Check]
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
            [Save to Sheets]                    [Chunk Transcript]
            (Optional)                                  ↓
                                                [Translate Chunks]
                                                         ↓
                                                [Merge Translations]
                                                         ↓
                    ┌─────────────────┬─────────────────┐
                    ↓                 ↓                 ↓
        [Summarize & Extract]    [Text to Speech]    (parallel)
                    ↓                 ↓
        [Prepare Image Prompts]       │
                    ↓                 │
        [Generate Images]             │
                    ↓                 │
        [Collect Images]              │
                    └────────┬────────┘
                             ↓
                    [Prepare Video Data]
                             ↓
                    [Compose Video]
                             ↓
                    [Save Metadata]
```

---

## 📦 Danh sách Node (16 nodes)

### **Trigger & Input**
1. ✅ **Schedule Trigger** - Chạy tự động mỗi 6 giờ
2. ✅ **Execute Script** - Chạy Python script lấy transcript
3. ✅ **Parse Script Output** - Parse JSON từ script

### **Validation & Storage**
4. ✅ **Check Transcript Exists** - Kiểm tra có transcript không
5. ✅ **Save to Google Sheets** (Optional) - Lưu transcript

### **Translation Pipeline**
6. ✅ **Chunk Transcript** - Chia transcript thành chunks nhỏ
7. ✅ **Translate Chunk (NCA)** - Dịch từng chunk (loop)
8. ✅ **Merge Translations** - Gộp các chunk đã dịch

### **Image Generation Pipeline**
9. ✅ **Summarize & Extract Image Prompts (NCA)** - Tóm tắt + tạo prompts
10. ✅ **Prepare Image Prompts** - Chuẩn bị items cho mỗi prompt
11. ✅ **Generate Image (NCA)** - Generate ảnh (loop 3-5 lần)
12. ✅ **Collect All Images** - Thu thập tất cả ảnh

### **Audio & Video Pipeline**
13. ✅ **Text to Speech (NCA)** - Chuyển text → voice (chạy song song với image gen)
14. ✅ **Prepare Video Data** - Tính toán duration, chuẩn bị data
15. ✅ **Compose Video (NCA)** - Ghép ảnh + audio → video
16. ✅ **Save Video Metadata** - Lưu metadata vào Sheets

---

## 🔑 Key Features

### ✅ Xử lý transcript dài (>10k từ)
- **Chunking**: Chia thành chunks ~4000 ký tự
- **Parallel Translation**: Có thể xử lý song song
- **Merge**: Gộp lại thành text hoàn chỉnh

### ✅ Tạo ảnh tự động
- **AI Summarization**: Tóm tắt nội dung
- **Prompt Generation**: Tạo 3-5 prompts phù hợp
- **Image Generation**: Generate ảnh với SDXL/Flux

### ✅ Video Composition
- **TTS**: Text → Voice tự nhiên
- **Timing**: Tự động tính duration cho mỗi ảnh
- **Composition**: Ghép ảnh + audio + subtitles

---

## ⚙️ Cấu hình cần thiết

### 1. **Python Script**
- File: `auto_extractor_json.py`
- Command: `python3 auto_extractor_json.py --output-json`
- Output: JSON format

### 2. **NCA Toolkit**
- Base URL: `http://nca:8080`
- Endpoints cần:
  - `/api/llm/translate`
  - `/api/llm/summarize`
  - `/api/image/generate`
  - `/api/audio/tts`
  - `/api/video/compose`

### 3. **Environment Variables**
```bash
GOOGLE_SHEET_ID=your_sheet_id
SHEET_NAME=Trang tính1
YOUTUBE_CHANNEL_URL=https://www.youtube.com/c/YourChannel
```

---

## 📝 Các bước triển khai

1. ✅ **Cài NCA Toolkit** trên server
2. ✅ **Upload script** `auto_extractor_json.py` lên server
3. ✅ **Import workflow** `n8n_workflow_youtube_to_video.json` vào n8n
4. ✅ **Cấu hình** environment variables
5. ✅ **Test** với video nhỏ trước
6. ✅ **Activate** workflow

---

## ⏱️ Thời gian xử lý ước tính

- **Get Transcript**: 10-30 giây
- **Translation** (10k từ): 2-5 phút
- **Summarize**: 30-60 giây
- **Generate Images** (5 ảnh): 2-5 phút
- **TTS**: 1-3 phút
- **Compose Video**: 3-10 phút

**Tổng**: ~10-25 phút cho 1 video (tùy độ dài)

---

## 🐛 Troubleshooting

### Script không chạy
→ Check Python path, dependencies, permissions

### NCA API timeout
→ Tăng timeout trong HTTP Request nodes

### Video composition fail
→ Check ffmpeg, image/audio URLs, disk space

### Google Sheets error
→ Re-authenticate credentials

---

## 📚 Files liên quan

- `n8n_workflow_youtube_to_video.json` - Workflow file để import
- `auto_extractor_json.py` - Python script cải tiến
- `N8N_WORKFLOW_GUIDE.md` - Hướng dẫn chi tiết từng node

---

## 🚀 Next Steps

1. Review và adjust workflow theo nhu cầu
2. Test từng node riêng lẻ
3. Test full flow với video nhỏ
4. Monitor và optimize performance
5. Scale up cho production


# 📋 TỔNG KẾT SETUP: YouTube Transcript → Video với n8n + NCA Toolkit

**Ngày:** 2025-11-07  
**Mục tiêu:** Tự động hóa quy trình lấy transcript YouTube → Dịch → Tạo ảnh → TTS → Ghép video

---

## 🎯 QUY TRÌNH TỔNG THỂ

```
1. Schedule Trigger (n8n)
   ↓
2. Execute Script → Lấy transcript từ YouTube
   ↓
3. Parse JSON Output
   ↓
4. Chunk Transcript (chia nhỏ nếu >10k từ)
   ↓
5. Translate (OpenAI API) - TẠM THỜI CHƯA CẦN
   ↓
6. Summarize & Extract Image Prompts (OpenAI API)
   ↓
7. Generate Images (Stable Diffusion/DALL-E)
   ↓
8. Text to Speech (ElevenLabs/Azure TTS)
   ↓
9. Compose Video (NCA Toolkit)
   ↓
10. Save Metadata
```

---

## 📦 CÁC THÀNH PHẦN ĐÃ CÀI ĐẶT

### ✅ 1. Script Python - Lấy Transcript
- **File:** `auto_extractor_json.py`
- **Chức năng:** Lấy transcript từ YouTube channel
- **Output:** JSON format cho n8n
- **Dependencies:** `scrapetube`, `youtube-transcript-api`

### ✅ 2. NCA Toolkit
- **Image:** Built from source (`stephengpope/no-code-architects-toolkit`)
- **Port:** 8080
- **API Key:** `4345b22022915fd98f1e1c1f024ceb52932709ebe0a112db8312664f86c53157`
- **Endpoints có sẵn:**
  - `/v1/toolkit/test` ✅
  - `/v1/media/transcribe` ✅
  - `/v1/video/caption_video`
  - `/v1/video/concatenate`
  - `/v1/ffmpeg/ffmpeg_compose`
  - `/v1/code/execute/execute_python`

### ✅ 3. MinIO Storage
- **Image:** `minio/minio:latest`
- **Ports:** 9000 (API), 9001 (Web UI)
- **Credentials:** `minioadmin` / `minioadmin123`
- **Bucket:** `nca-toolkit`

### ✅ 4. n8n Workflow
- **File:** `n8n_workflow_youtube_to_video.json`
- **Status:** Đã tạo, cần cập nhật endpoints

---

## 🐳 DOCKER COMPOSE CHUẨN

**File:** `~/n8n-data/docker-compose.yml`

```yaml
version: '3.7'

services:
  n8n:
    build: .
    restart: always
    ports:
      - "5678:5678"
    environment:
      - GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
      - WEBHOOK_URL=https://vidflow.id.vn/
      - N8N_HOST=vidflow.id.vn
    volumes:
      - ./n8n-local-files:/home/node/.n8n
      - ./scripts:/home/node/scripts
    networks:
      - n8n-network

  minio:
    image: minio/minio:latest
    restart: always
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
    command: server /data --console-address ":9001"
    volumes:
      - ./minio-data:/data
    networks:
      - n8n-network

  nca:
    build: ./nca-toolkit
    restart: always
    ports:
      - "8080:8080"
    environment:
      - TZ=Asia/Ho_Chi_Minh
      - API_KEY=4345b22022915fd98f1e1c1f024ceb52932709ebe0a112db8312664f86c53157
      - LOCAL_STORAGE_PATH=/app/data
      - MAX_QUEUE_LENGTH=10
      - GUNICORN_WORKERS=4
      - GUNICORN_TIMEOUT=300
      - S3_ENDPOINT_URL=http://minio:9000
      - S3_ACCESS_KEY=minioadmin
      - S3_SECRET_KEY=minioadmin123
      - S3_BUCKET_NAME=nca-toolkit
      - S3_REGION=us-east-1
    volumes:
      - ./nca-data:/app/data
    networks:
      - n8n-network
    depends_on:
      - minio

networks:
  n8n-network:
    driver: bridge
```

---

## 🔧 DOCKERFILE CHO N8N

**File:** `~/n8n-data/Dockerfile`

```dockerfile
FROM n8nio/n8n
USER root
RUN apk add --no-cache ffmpeg python3 py3-pip
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install scrapetube youtube-transcript-api google-auth google-auth-oauthlib google-api-python-client
USER node
```

---

## 📝 CÁC LỆNH QUAN TRỌNG

### 1. Setup ban đầu

```bash
# Clone NCA Toolkit
cd ~/n8n-data
git clone https://github.com/stephengpope/no-code-architects-toolkit.git nca-toolkit

# Tạo API key
API_KEY=$(openssl rand -hex 32)
echo "API_KEY=$API_KEY"

# Tạo thư mục data
mkdir -p ~/n8n-data/{scripts,nca-data,minio-data}

# Build và start
docker compose build nca
docker compose up -d
```

### 2. Setup Python script

```bash
# Clone repo YouTube transcript
cd ~
git clone https://github.com/huycuuvan/youtube_transcript.git

# Copy script vào n8n
cp ~/youtube_transcript/auto_extractor_json.py ~/n8n-data/scripts/
chmod +x ~/n8n-data/scripts/auto_extractor_json.py

# Test script
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json'
```

### 3. Tạo MinIO bucket

```bash
# Truy cập MinIO Web UI
# URL: http://your-server-ip:9001
# Login: minioadmin / minioadmin123
# Tạo bucket: nca-toolkit
```

### 4. Test NCA Toolkit

```bash
# Test endpoint
curl -X GET "http://localhost:8080/v1/toolkit/test" \
  -H "x-api-key: 4345b22022915fd98f1e1c1f024ceb52932709ebe0a112db8312664f86c53157"

# Test transcribe
curl -X POST "http://localhost:8080/v1/media/transcribe" \
  -H "x-api-key: 4345b22022915fd98f1e1c1f024ceb52932709ebe0a112db8312664f86c53157" \
  -H "Content-Type: application/json" \
  -d '{
    "media_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "task": "transcribe",
    "include_text": true
  }'
```

### 5. Test từ n8n container

```bash
# Test kết nối
docker exec -it n8n-data-n8n-1 sh -c 'curl -X GET "http://nca:8080/v1/toolkit/test" -H "x-api-key: 4345b22022915fd98f1e1c1f024ceb52932709ebe0a112db8312664f86c53157"'
```

### 6. Recreate containers (khi sửa network)

```bash
cd ~/n8n-data
docker compose stop n8n nca
docker compose rm -f n8n nca
docker compose up -d n8n nca
```

---

## ⚠️ CÁC LỖI THƯỜNG GẶP VÀ CÁCH SỬA

### 1. Lỗi: "No such file or directory" khi chạy script

**Nguyên nhân:** Script không có trong container hoặc đường dẫn sai

**Giải pháp:**
```bash
# Copy script vào đúng thư mục
cp ~/youtube_transcript/auto_extractor_json.py ~/n8n-data/scripts/
chmod +x ~/n8n-data/scripts/auto_extractor_json.py

# Đảm bảo volume mount đúng trong docker-compose.yml
# volumes:
#   - ./scripts:/home/node/scripts
```

### 2. Lỗi: "Permission denied" khi cài Python packages

**Nguyên nhân:** Không có quyền root

**Giải pháp:**
```bash
# Dùng --user root
docker exec -it --user root n8n-data-n8n-1 sh -c 'pip3 install --break-system-packages package_name'

# Hoặc cài vào venv
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && pip install package_name'
```

### 3. Lỗi: "externally-managed-environment" khi cài pip

**Nguyên nhân:** Python 3.12+ không cho phép cài system-wide

**Giải pháp:**
```bash
# Dùng venv (đã setup trong Dockerfile)
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && pip install package_name'

# Hoặc dùng flag
docker exec -it --user root n8n-data-n8n-1 sh -c 'pip3 install --break-system-packages package_name'
```

### 4. Lỗi: "The connection cannot be established" trong n8n

**Nguyên nhân:** Containers không cùng Docker network

**Giải pháp:**
```bash
# Kiểm tra network
docker inspect n8n-data-n8n-1 | grep -A 5 "Networks"
docker inspect n8n-data-nca-1 | grep -A 5 "Networks"

# Recreate containers
docker compose stop n8n nca
docker compose rm -f n8n nca
docker compose up -d n8n nca

# Hoặc connect thủ công
docker network connect n8n-data_n8n-network n8n-data-n8n-1
```

### 5. Lỗi: "Permission denied: '/tmp/jobs'" trong NCA

**Nguyên nhân:** Container không có quyền tạo thư mục

**Giải pháp:**
```bash
# Tạo thư mục với quyền đúng
docker exec -it --user root n8n-data-nca-1 sh -c 'mkdir -p /app/data/jobs && chmod -R 777 /app/data'

# Đảm bảo LOCAL_STORAGE_PATH=/app/data trong docker-compose.yml
```

### 6. Lỗi: "No cloud storage settings provided"

**Nguyên nhân:** NCA cần S3 hoặc GCP storage

**Giải pháp:**
- Cài MinIO (S3-compatible)
- Cấu hình S3 environment variables trong docker-compose.yml
- Tạo bucket `nca-toolkit` trong MinIO

### 7. Lỗi: "Invalid payload: 'true' is not of type 'boolean'"

**Nguyên nhân:** n8n gửi string "true" thay vì boolean

**Giải pháp:**
- Trong n8n, dùng "Using JSON" thay vì "Using Fields Below"
- Hoặc dùng expression: `={{ true }}` thay vì `true`

### 8. Lỗi: "Error opening input: Invalid data found" khi transcribe YouTube/SoundCloud

**Nguyên nhân:** NCA không có yt-dlp hoặc soundcloud-dl để download từ các platform

**Giải pháp:**
```bash
# Cài yt-dlp và soundcloud-dl vào NCA container
docker exec -it --user root n8n-data-nca-1 sh -c 'pip install yt-dlp soundcloud-dl'

# Hoặc cập nhật Dockerfile của NCA
# Thêm: RUN pip install yt-dlp soundcloud-dl

# Restart NCA
docker compose restart nca
```

**Lưu ý:** NCA chỉ có thể xử lý file audio/video trực tiếp. Để xử lý YouTube/SoundCloud:
- Cài yt-dlp/soundcloud-dl vào NCA container
- Hoặc download file trước, sau đó upload lên server và gửi URL file trực tiếp

### 9. Lỗi: "404 Not Found" khi gọi endpoint

**Nguyên nhân:** URL path sai

**Giải pháp:**
- Kiểm tra routes trong logs: `docker compose logs nca | grep "Registering:"`
- Dùng đúng path: `/v1/media/transcribe` (không phải `/api/...`)

### 10. Lỗi: "datetime.utcnow() is deprecated"

**Nguyên nhân:** Code dùng deprecated function

**Giải pháp:**
- Thay `datetime.utcnow()` bằng `datetime.now().isoformat()`

---

## 📁 CẤU TRÚC THƯ MỤC

```
~/n8n-data/
├── docker-compose.yml          # Cấu hình Docker services
├── Dockerfile                  # Dockerfile cho n8n (có Python + venv)
├── n8n-local-files/           # Data của n8n
├── scripts/                   # Python scripts
│   └── auto_extractor_json.py # Script lấy transcript
├── nca-toolkit/               # NCA Toolkit source code
│   └── (cloned from GitHub)
├── nca-data/                 # Data của NCA Toolkit
└── minio-data/               # Data của MinIO

~/youtube_transcript/          # Repo GitHub
├── auto_extractor.py
├── auto_extractor_json.py     # Version có output JSON
└── requirements.txt
```

---

## 🔑 THÔNG TIN QUAN TRỌNG

### API Keys & Credentials

- **NCA API Key:** `4345b22022915fd98f1e1c1f024ceb52932709ebe0a112db8312664f86c53157`
- **MinIO Access Key:** `minioadmin`
- **MinIO Secret Key:** `minioadmin123`
- **MinIO Bucket:** `nca-toolkit`

### Ports

- **n8n:** `5678`
- **NCA Toolkit:** `8080`
- **MinIO API:** `9000`
- **MinIO Web UI:** `9001`

### Network

- **Network name:** `n8n-data_n8n-network` hoặc `n8n-network`
- **Service names:** `n8n`, `nca`, `minio`

---

## 🚀 QUY TRÌNH SETUP TỪ ĐẦU

### Bước 1: Clone repos

```bash
# Clone NCA Toolkit
cd ~/n8n-data
git clone https://github.com/stephengpope/no-code-architects-toolkit.git nca-toolkit

# Clone YouTube transcript script
cd ~
git clone https://github.com/huycuuvan/youtube_transcript.git
```

### Bước 2: Tạo API key và cấu hình

```bash
# Tạo API key cho NCA
API_KEY=$(openssl rand -hex 32)
echo "API_KEY=$API_KEY"  # Lưu lại key này

# Tạo thư mục
mkdir -p ~/n8n-data/{scripts,nca-data,minio-data}
```

### Bước 3: Cấu hình docker-compose.yml

- Copy nội dung docker-compose.yml ở trên
- Thay `API_KEY` bằng key vừa tạo
- Đảm bảo tất cả services cùng network `n8n-network`

### Bước 4: Build và start

```bash
cd ~/n8n-data

# Build NCA
docker compose build nca

# Start tất cả
docker compose up -d

# Kiểm tra
docker ps | grep -E "n8n|nca|minio"
```

### Bước 5: Setup Python script

```bash
# Copy script
cp ~/youtube_transcript/auto_extractor_json.py ~/n8n-data/scripts/
chmod +x ~/n8n-data/scripts/auto_extractor_json.py

# Test
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json'
```

### Bước 6: Tạo MinIO bucket

1. Truy cập: `http://your-server-ip:9001`
2. Login: `minioadmin` / `minioadmin123`
3. Tạo bucket: `nca-toolkit`

### Bước 7: Test NCA

```bash
# Test endpoint
curl -X GET "http://localhost:8080/v1/toolkit/test" \
  -H "x-api-key: YOUR_API_KEY"
```

### Bước 8: Import workflow vào n8n

1. Mở n8n: `http://your-server-ip:5678`
2. Workflows → Import from File
3. Chọn `n8n_workflow_youtube_to_video.json`
4. Cập nhật các node với endpoints đúng

---

## 📊 ENDPOINTS NCA TOOLKIT

### ✅ Endpoints có sẵn và đã test

- `GET /v1/toolkit/test` - Test API
- `POST /v1/media/transcribe` - Transcribe audio/video
- `POST /v1/toolkit/authenticate` - Authenticate
- `GET /v1/toolkit/job/status` - Check job status

### ❌ Endpoints KHÔNG có (cần dùng service khác)

- `/v1/llm/translate` - Dùng OpenAI API trực tiếp
- `/v1/llm/summarize` - Dùng OpenAI API trực tiếp
- `/v1/image/generate` - Dùng Stable Diffusion/DALL-E
- `/v1/audio/tts` - Dùng ElevenLabs/Azure TTS
- `/v1/video/compose` - Dùng `/v1/ffmpeg/ffmpeg_compose` thay thế

### 📝 Endpoints khác có sẵn

- `POST /v1/video/caption_video` - Thêm caption
- `POST /v1/video/concatenate` - Ghép video
- `POST /v1/video/cut` - Cắt video
- `POST /v1/video/split` - Chia video
- `POST /v1/video/trim` - Trim video
- `POST /v1/ffmpeg/ffmpeg_compose` - Compose video với ffmpeg
- `POST /v1/code/execute/execute_python` - Chạy Python code
- `POST /v1/image/convert/image_to_video` - Convert image to video

---

## 🔧 CẤU HÌNH N8N WORKFLOW

### Node: Execute Script - Get Transcript

**Command:**
```bash
source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json
```

### Node: HTTP Request - NCA Toolkit

**Cấu hình chung:**
- Method: `POST`
- URL: `http://nca:8080/v1/...` (không dùng `localhost`)
- Authentication: `None`
- Send Headers: `ON`
  - Name: `x-api-key`
  - Value: `4345b22022915fd98f1e1c1f024ceb52932709ebe0a112db8312664f86c53157`
- Send Body: `ON`
- Body Content Type: `JSON`
- Specify Body: `Using JSON` (không dùng "Using Fields Below" cho boolean)

**Ví dụ JSON Body:**
```json
{
  "media_url": "https://example.com/audio.mp3",
  "task": "transcribe",
  "include_text": true,
  "include_srt": true
}
```

---

## 🐛 TROUBLESHOOTING

### Kiểm tra containers

```bash
# Xem containers đang chạy
docker ps | grep -E "n8n|nca|minio"

# Xem logs
docker compose logs nca | tail -50
docker compose logs n8n | tail -50

# Kiểm tra network
docker network inspect n8n-data_n8n-network
```

### Kiểm tra kết nối

```bash
# Test từ n8n container
docker exec -it n8n-data-n8n-1 sh -c 'ping -c 2 nca'
docker exec -it n8n-data-n8n-1 sh -c 'curl http://nca:8080/v1/toolkit/test -H "x-api-key: YOUR_KEY"'
```

### Restart services

```bash
# Restart một service
docker compose restart nca

# Restart tất cả
docker compose restart

# Recreate (khi sửa config)
docker compose down
docker compose up -d
```

---

## 📚 TÀI LIỆU THAM KHẢO

- **NCA Toolkit GitHub:** https://github.com/stephengpope/no-code-architects-toolkit
- **n8n Documentation:** https://docs.n8n.io/
- **MinIO Documentation:** https://min.io/docs/

---

## ✅ CHECKLIST HOÀN THÀNH

- [x] Script Python lấy transcript hoạt động
- [x] NCA Toolkit đã cài đặt và chạy
- [x] MinIO storage đã cấu hình
- [x] Docker network đã setup đúng
- [x] Endpoints đã test thành công
- [ ] Workflow n8n đã import và cấu hình
- [ ] Cài yt-dlp cho NCA (nếu cần YouTube)
- [ ] Tích hợp OpenAI API cho translation
- [ ] Tích hợp image generation service
- [ ] Tích hợp TTS service

---

## 🎯 BƯỚC TIẾP THEO

1. **Cài yt-dlp và soundcloud-dl vào NCA** (nếu cần xử lý YouTube/SoundCloud trực tiếp)
   ```bash
   docker exec -it --user root n8n-data-nca-1 sh -c 'pip install yt-dlp soundcloud-dl'
   docker compose restart nca
   ```
2. **Cập nhật n8n workflow** với endpoints đúng
3. **Tích hợp OpenAI API** cho translation/summarize
4. **Tích hợp image generation** (Stable Diffusion/DALL-E)
5. **Tích hợp TTS** (ElevenLabs/Azure TTS)
6. **Test end-to-end workflow**

## 📌 LƯU Ý QUAN TRỌNG

### NCA Toolkit chỉ xử lý file trực tiếp
- ✅ File audio/video có URL trực tiếp: `https://example.com/audio.mp3`
- ❌ YouTube URL: Cần cài yt-dlp
- ❌ SoundCloud URL: Cần cài soundcloud-dl
- ❌ Các platform khác: Cần tool tương ứng

### Giải pháp thay thế
1. **Download file trước** bằng script Python (yt-dlp, soundcloud-dl)
2. **Upload lên server** hoặc MinIO
3. **Gửi URL file trực tiếp** cho NCA

---

**Lưu ý:** File này nên được cập nhật khi có thay đổi trong setup hoặc phát hiện lỗi mới.


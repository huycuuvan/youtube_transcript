# 🔧 Sửa lỗi: "No such file or directory" trong n8n

## ❌ Lỗi hiện tại
```
Command failed: cd /path/to/youtube_extractor && python3 auto_extractor.py --output-json
/bin/sh: cd: line 0: can't cd to /path/to/youtube_extractor: No such file or directory
```

## ✅ Giải pháp

### **Cách 1: Đặt script trong n8n container (Khuyến nghị)**

#### Bước 1: Upload script lên server
```bash
# SSH vào server
ssh user@your-server

# Tạo thư mục scripts trong n8n-data
cd ~/n8n-data
mkdir -p scripts

# Upload auto_extractor_json.py vào thư mục scripts
# (Dùng scp, sftp, hoặc copy trực tiếp)
```

#### Bước 2: Mount volume vào docker-compose.yml
Sửa file `~/n8n-data/docker-compose.yml`:

```yaml
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
      - ./scripts:/home/node/scripts  # ← Thêm dòng này
```

#### Bước 3: Cài dependencies trong n8n container
```bash
# Vào container n8n
docker exec -it n8n-data-n8n-1 sh

# Cài Python và dependencies
apk add python3 py3-pip
pip3 install scrapetube youtube-transcript-api

# Thoát
exit
```

#### Bước 4: Cập nhật command trong n8n workflow
Trong node "Execute Script - Get Transcript", đổi command thành:
```bash
cd /home/node/scripts && python3 auto_extractor_json.py --output-json
```

---

### **Cách 2: Đặt script trên host và mount vào container**

#### Bước 1: Tạo thư mục trên host
```bash
mkdir -p ~/youtube_extractor
# Upload auto_extractor_json.py vào đây
```

#### Bước 2: Mount vào docker-compose.yml
```yaml
volumes:
  - ./n8n-local-files:/home/node/.n8n
  - ~/youtube_extractor:/home/node/youtube_extractor  # ← Thêm dòng này
```

#### Bước 3: Cập nhật command
```bash
cd /home/node/youtube_extractor && python3 auto_extractor_json.py --output-json
```

---

### **Cách 3: Dùng HTTP Request thay vì Execute Command**

Nếu không muốn chạy script trong container, có thể:
1. Tạo một API endpoint đơn giản (Flask/FastAPI) để chạy script
2. Gọi API đó từ n8n bằng HTTP Request node

---

## 🔍 Kiểm tra đường dẫn hiện tại

### Trong n8n container:
```bash
# Vào container
docker exec -it n8n-data-n8n-1 sh

# Kiểm tra thư mục hiện tại
pwd

# Liệt kê files
ls -la /home/node/

# Kiểm tra Python
which python3
python3 --version

# Thoát
exit
```

### Trên host:
```bash
# Kiểm tra thư mục n8n-data
ls -la ~/n8n-data/

# Kiểm tra scripts folder
ls -la ~/n8n-data/scripts/
```

---

## 📝 Cập nhật Workflow

Sau khi chọn cách và setup xong, cập nhật command trong workflow:

1. Mở workflow trong n8n
2. Click vào node "Execute Script - Get Transcript"
3. Sửa command field với đường dẫn đúng
4. Test lại node

---

## 🧪 Test command trực tiếp

Test command trước khi đưa vào n8n:

```bash
# Vào container
docker exec -it n8n-data-n8n-1 sh

# Test command
cd /home/node/scripts && python3 auto_extractor_json.py --output-json

# Nếu thiếu dependencies, cài thêm
pip3 install scrapetube youtube-transcript-api
```

---

## ⚠️ Lưu ý

1. **Python dependencies**: Script cần `scrapetube` và `youtube-transcript-api`
2. **Permissions**: Đảm bảo script có quyền execute
3. **Working directory**: Script có thể cần file config, đảm bảo đường dẫn đúng
4. **Environment variables**: Nếu script dùng env vars, thêm vào docker-compose.yml

---

## 🚀 Quick Fix (Tạm thời)

Nếu muốn test nhanh, có thể:

1. Copy script vào thư mục hiện tại của container:
```bash
docker cp auto_extractor_json.py n8n-data-n8n-1:/tmp/
```

2. Dùng command:
```bash
python3 /tmp/auto_extractor_json.py --output-json
```

Nhưng cách này sẽ mất khi container restart. Nên dùng volume mount (Cách 1 hoặc 2).


# ⚡ Quick Fix: Sửa lỗi đường dẫn trong n8n

## 🔴 Lỗi
```
can't cd to /path/to/youtube_extractor: No such file or directory
```

## ✅ Giải pháp nhanh (3 bước)

### **Bước 1: Tạo thư mục và copy script**

SSH vào server và chạy:

```bash
# Tạo thư mục scripts
mkdir -p ~/n8n-data/scripts

# Copy script vào (từ máy local của bạn)
# Dùng scp hoặc upload qua SFTP
scp auto_extractor_json.py user@server:~/n8n-data/scripts/
```

### **Bước 2: Cập nhật docker-compose.yml**

Mở file `~/n8n-data/docker-compose.yml` và thêm dòng volume mount:

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
      - ./scripts:/home/node/scripts  # ← THÊM DÒNG NÀY
```

### **Bước 3: Restart container và cài dependencies**

```bash
cd ~/n8n-data
docker compose restart

# Vào container
docker exec -it n8n-data-n8n-1 sh

# Cài Python và dependencies
apk add python3 py3-pip
pip3 install scrapetube youtube-transcript-api

# Test script
cd /home/node/scripts
python3 auto_extractor_json.py --output-json

# Thoát
exit
```

### **Bước 4: Cập nhật workflow trong n8n**

1. Mở workflow trong n8n
2. Click node "Execute Script - Get Transcript"
3. Đổi command thành:
   ```bash
   cd /home/node/scripts && python3 auto_extractor_json.py --output-json
   ```
4. Click "Execute step" để test

---

## 🎯 Hoặc dùng script tự động

Nếu đã có file `setup_n8n_script.sh`:

```bash
chmod +x setup_n8n_script.sh
./setup_n8n_script.sh
```

Script sẽ tự động:
- Tạo thư mục scripts
- Copy file vào đúng chỗ
- Cập nhật docker-compose.yml (nếu bạn đồng ý)
- Hướng dẫn các bước tiếp theo

---

## ✅ Kiểm tra

Sau khi setup, test command:

```bash
docker exec -it n8n-data-n8n-1 sh -c 'cd /home/node/scripts && python3 auto_extractor_json.py --output-json'
```

Nếu thấy output JSON → ✅ Thành công!

---

## 📝 Lưu ý

- Đường dẫn trong workflow đã được cập nhật thành `/home/node/scripts`
- Nếu container name khác `n8n-data-n8n-1`, kiểm tra bằng: `docker ps`
- Nếu vẫn lỗi, xem file `FIX_PATH_ERROR.md` để có thêm options


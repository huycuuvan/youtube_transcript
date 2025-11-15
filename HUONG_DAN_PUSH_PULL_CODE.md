# 📤 HƯỚNG DẪN: Push Code lên GitHub và Pull trên Server

## 🔄 QUY TRÌNH

```
Local (Windows) → Push lên GitHub → Server → Pull code mới → Copy vào n8n container
```

---

## 📤 BƯỚC 1: PUSH CODE LÊN GITHUB (Từ máy local)

### 1. Kiểm tra trạng thái Git

```bash
# Kiểm tra file đã thay đổi
git status

# Xem các thay đổi
git diff auto_extractor_json.py
```

### 2. Add và Commit

```bash
# Add file đã sửa
git add auto_extractor_json.py

# Hoặc add tất cả thay đổi
git add .

# Commit với message
git commit -m "Update: Hỗ trợ channel URL và dynamic video ID"

# Push lên GitHub
git push origin main
```

**Lưu ý:** Nếu chưa có remote, thêm remote trước:
```bash
git remote add origin https://github.com/huycuuvan/youtube_transcript.git
git branch -M main
git push -u origin main
```

---

## 📥 BƯỚC 2: PULL CODE TRÊN SERVER

### Cách 1: Pull và Copy thủ công (Khuyến nghị)

```bash
# SSH vào server
ssh user@your-server-ip

# Vào thư mục repo đã clone
cd ~/youtube_transcript

# Pull code mới
git pull origin main

# Copy script mới vào n8n scripts folder
cp auto_extractor_json.py ~/n8n-data/scripts/

# Set quyền thực thi
chmod +x ~/n8n-data/scripts/auto_extractor_json.py

# Kiểm tra file đã được copy
ls -lh ~/n8n-data/scripts/auto_extractor_json.py
```

### Cách 2: Pull trực tiếp trong container (Nếu repo đã mount vào container)

Nếu bạn đã mount repo vào container, có thể pull trực tiếp:

```bash
# Vào container
docker exec -it n8n-data-n8n-1 sh

# Vào thư mục repo (nếu đã mount)
cd /path/to/repo

# Pull code
git pull origin main
```

---

## 🧪 BƯỚC 3: TEST SCRIPT MỚI

Sau khi copy script mới, test ngay:

```bash
# Test script với video ID
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "dQw4w9WgXcQ"'

# Test script với channel URL
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"'
```

---

## 🔄 SCRIPT TỰ ĐỘNG HÓA (Tùy chọn)

Tạo script để tự động pull và copy:

**File: `~/update_script.sh`**

```bash
#!/bin/bash

echo "🔄 Đang pull code mới từ GitHub..."
cd ~/youtube_transcript
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Pull thành công!"
    echo "📋 Đang copy script vào n8n..."
    cp auto_extractor_json.py ~/n8n-data/scripts/
    chmod +x ~/n8n-data/scripts/auto_extractor_json.py
    echo "✅ Hoàn thành! Script đã được cập nhật."
    
    # Test script
    echo "🧪 Đang test script..."
    docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --help'
else
    echo "❌ Lỗi khi pull code!"
    exit 1
fi
```

**Cách dùng:**
```bash
# Tạo file
nano ~/update_script.sh
# Paste nội dung trên, sau đó:
chmod +x ~/update_script.sh

# Chạy script
~/update_script.sh
```

---

## 📋 CHECKLIST

- [ ] ✅ Đã commit code mới trên local
- [ ] ✅ Đã push lên GitHub
- [ ] ✅ Đã SSH vào server
- [ ] ✅ Đã pull code mới từ GitHub
- [ ] ✅ Đã copy script vào `~/n8n-data/scripts/`
- [ ] ✅ Đã set quyền thực thi (`chmod +x`)
- [ ] ✅ Đã test script mới
- [ ] ✅ Đã test trong n8n workflow

---

## ⚠️ LƯU Ý

1. **Backup trước khi update:**
   ```bash
   # Backup script cũ
   cp ~/n8n-data/scripts/auto_extractor_json.py ~/n8n-data/scripts/auto_extractor_json.py.backup
   ```

2. **Kiểm tra version:**
   - Script mới có hàm `extract_video_id_from_url()` và hỗ trợ channel URL
   - Kiểm tra bằng: `grep "extract_video_id_from_url" ~/n8n-data/scripts/auto_extractor_json.py`

3. **Nếu có lỗi:**
   - Restore từ backup: `cp ~/n8n-data/scripts/auto_extractor_json.py.backup ~/n8n-data/scripts/auto_extractor_json.py`
   - Hoặc pull lại version cũ: `git checkout HEAD~1 auto_extractor_json.py`

---

## 🚀 QUICK COMMANDS

**Tất cả trong một lệnh:**

```bash
# Trên server
cd ~/youtube_transcript && \
git pull origin main && \
cp auto_extractor_json.py ~/n8n-data/scripts/ && \
chmod +x ~/n8n-data/scripts/auto_extractor_json.py && \
echo "✅ Đã cập nhật script thành công!"
```

---

## 📌 TÓM TẮT

1. **Local:** `git add . && git commit -m "message" && git push`
2. **Server:** `cd ~/youtube_transcript && git pull && cp auto_extractor_json.py ~/n8n-data/scripts/`
3. **Test:** `docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --help'`

**Xong!** Script mới đã sẵn sàng sử dụng trong n8n workflow.


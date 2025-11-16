# 🔧 FIX: Lỗi Command trong n8n Workflow

## ❌ VẤN ĐỀ PHÁT HIỆN

### 1. Typo trong Command
```
--output-js on  ❌ (SAI)
--output-json   ✅ (ĐÚNG)
```

### 2. Lỗi Connection
```
"The connection cannot be established, this usually occurs due to an incorrect host (domain) value"
```

---

## 🔧 GIẢI PHÁP

### Bước 1: Sửa Command trong n8n

**Command hiện tại (SAI):**
```bash
cd /home/node/scripts && python3 auto_extractor_json.py --output-js on --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"
```

**Command đúng:**
```bash
cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"
```

**Hoặc nếu muốn dùng environment variable:**
```bash
cd /home/node/scripts && source /opt/venv/bin/activate && python3 auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"
```

---

## 🔍 KIỂM TRA LỖI CONNECTION

### Nguyên nhân có thể:

1. **Container không có internet**
2. **scrapetube không hoạt động**
3. **Python venv chưa được activate**

### Cách kiểm tra:

```bash
# 1. Kiểm tra internet trong container
docker exec -it n8n-data-n8n-1 ping -c 2 youtube.com

# 2. Kiểm tra scrapetube
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && python3 -c "import scrapetube; print(\"OK\")"'

# 3. Test script trực tiếp
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"'
```

---

## ✅ COMMAND ĐÚNG CHO N8N

### Option 1: Không dùng venv (nếu Python packages đã cài system-wide)

```bash
cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "{{ $json.videoId }}"
```

### Option 2: Dùng venv (Khuyến nghị)

```bash
cd /home/node/scripts && source /opt/venv/bin/activate && python3 auto_extractor_json.py --output-json --video-id "{{ $json.videoId }}"
```

### Option 3: Dùng environment variable

**Command:**
```bash
cd /home/node/scripts && source /opt/venv/bin/activate && python3 auto_extractor_json.py --output-json
```

**Environment Variables trong n8n node:**
- Name: `YOUTUBE_VIDEO_ID`
- Value: `={{ $json.videoId }}` hoặc `={{ $json.youtubeUrl }}`

---

## 🧪 TEST SCRIPT TRỰC TIẾP

Trước khi test trong n8n, test script trực tiếp trong container:

```bash
# Test với channel URL
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"'

# Test với video ID
docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "dQw4w9WgXcQ"'
```

---

## 📋 CHECKLIST

- [ ] ✅ Đã sửa `--output-js on` → `--output-json`
- [ ] ✅ Đã thêm `source /opt/venv/bin/activate` (nếu cần)
- [ ] ✅ Đã test script trực tiếp trong container
- [ ] ✅ Đã kiểm tra internet trong container
- [ ] ✅ Đã kiểm tra scrapetube hoạt động
- [ ] ✅ Đã test trong n8n workflow

---

## 🚀 QUICK FIX

**Trong n8n node "Execute Script - Get Transcript":**

1. **Command:**
   ```bash
   cd /home/node/scripts && source /opt/venv/bin/activate && python3 auto_extractor_json.py --output-json --video-id "{{ $json.videoId }}"
   ```

2. **Nếu lấy từ Google Sheets:**
   ```bash
   cd /home/node/scripts && source /opt/venv/bin/activate && python3 auto_extractor_json.py --output-json --video-id "{{ $json['A'] }}"
   ```

3. **Nếu dùng channel URL trực tiếp:**
   ```bash
   cd /home/node/scripts && source /opt/venv/bin/activate && python3 auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"
   ```

---

## ⚠️ LƯU Ý

1. **`--output-json`** không cần giá trị (không phải `--output-json on`)
2. **Channel URL** đã được script hỗ trợ - sẽ tự động lấy video mới nhất
3. **Nếu vẫn lỗi connection:** Kiểm tra container có internet và scrapetube đã được cài đúng

---

**Sau khi sửa command, test lại trong n8n!** ✅



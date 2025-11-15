# 📝 HƯỚNG DẪN: Lấy YouTube Link Dynamic từ Google Sheets

## ✅ Đã cập nhật script Python

Script `auto_extractor_json.py` đã được cập nhật để:
- ✅ Nhận YouTube URL hoặc Video ID từ argument `--video-id`
- ✅ Tự động trích xuất Video ID từ các định dạng URL:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`
  - Hoặc chỉ cần `VIDEO_ID` (11 ký tự)
- ✅ **Hỗ trợ Channel URL** - Nếu truyền channel URL, sẽ tự động lấy video mới nhất từ channel:
  - `https://www.youtube.com/c/CHANNEL_NAME`
  - `https://www.youtube.com/channel/CHANNEL_ID`
  - `https://www.youtube.com/user/USER_NAME`
  - `https://www.youtube.com/@HANDLE`
- ✅ Hỗ trợ nhận từ environment variable: `YOUTUBE_VIDEO_ID` hoặc `YOUTUBE_VIDEO_URL`

---

## 🔧 CÁCH THÊM NODE TRONG N8N

### Bước 1: Thêm node để lấy link từ Google Sheets

1. **Thêm node "Google Sheets"** (Read operation) trước node "Execute Script - Get Transcript"
   - **Operation:** `Read`
   - **Document ID:** Chọn Google Sheet của bạn
   - **Sheet Name:** Chọn sheet chứa YouTube link
   - **Range:** Ví dụ `A2:A2` (ô chứa YouTube link) hoặc `A2` (lấy từ hàng 2, cột A)
   - **Options:** 
     - Bật "Return All" nếu muốn lấy nhiều link
     - Hoặc chỉ lấy 1 link đầu tiên

### Bước 2: Thêm node "Code" để trích xuất Video ID

1. **Thêm node "Code"** giữa Google Sheets và Execute Script
   - **Name:** `Extract Video ID from URL`
   - **Code:**
   ```javascript
   // Lấy YouTube URL từ Google Sheets
   const youtubeUrl = $input.item.json['A'] || $input.item.json[0] || $input.item.json.youtubeUrl || $input.item.json.url || '';
   
   // Trích xuất Video ID từ URL
   function extractVideoId(url) {
     if (!url) return null;
     
     // Nếu đã là video ID (11 ký tự)
     if (/^[a-zA-Z0-9_-]{11}$/.test(url)) {
       return url;
     }
     
     // Các pattern YouTube URL
     const patterns = [
       /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
       /youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})/
     ];
     
     for (const pattern of patterns) {
       const match = url.match(pattern);
       if (match) {
         return match[1];
       }
     }
     
     return null;
   }
   
   const videoId = extractVideoId(youtubeUrl);
   
   if (!videoId) {
     throw new Error(`Không thể trích xuất Video ID từ URL: ${youtubeUrl}`);
   }
   
   return {
     json: {
       videoId: videoId,
       youtubeUrl: youtubeUrl,
       timestamp: new Date().toISOString()
     }
   };
   ```

### Bước 3: Cập nhật node "Execute Script - Get Transcript"

1. **Sửa command** trong node "Execute Script - Get Transcript":
   - **Command cũ:**
     ```bash
     cd /home/node/scripts && python3 auto_extractor_json.py --output-json
     ```
   
   - **Command mới:**
     ```bash
     cd /home/node/scripts && python3 auto_extractor_json.py --output-json --video-id "{{ $json.videoId }}"
     ```

---

## 📋 CÁCH KHÁC: Dùng Environment Variable

Nếu bạn muốn dùng environment variable thay vì argument:

### Cách 1: Sửa Execute Command node

**Command:**
```bash
cd /home/node/scripts && YOUTUBE_VIDEO_ID="{{ $json.videoId }}" python3 auto_extractor_json.py --output-json
```

### Cách 2: Dùng Set node để set environment variable

1. **Thêm node "Set"** trước Execute Script
   - **Keep Only Set Fields:** `OFF`
   - **Fields to Set:**
     - **Name:** `YOUTUBE_VIDEO_ID`
     - **Value:** `={{ $json.videoId }}`
   
2. **Sửa Execute Script node:**
   - **Command:**
     ```bash
     cd /home/node/scripts && python3 auto_extractor_json.py --output-json
     ```
   - **Options → Environment Variables:**
     - **Name:** `YOUTUBE_VIDEO_ID`
     - **Value:** `={{ $json.videoId }}`

---

## 🎯 VÍ DỤ: Lấy link từ Google Sheets

### Cấu trúc Google Sheet:

| A (YouTube URL) | B (Title) | C (Status) |
|----------------|-----------|------------|
| https://www.youtube.com/watch?v=dQw4w9WgXcQ | Video 1 | Pending |
| https://youtu.be/abc123xyz | Video 2 | Pending |

### Workflow Flow:

```
Schedule Trigger (hoặc Manual Trigger)
    ↓
Google Sheets (Read) - Lấy link từ cột A
    ↓
Code (Extract Video ID) - Trích xuất Video ID
    ↓
Execute Script - Get Transcript (với --video-id)
    ↓
Parse Script Output
    ↓
... (các node tiếp theo)
```

---

## 🔄 XỬ LÝ NHIỀU LINK (Loop)

Nếu bạn muốn xử lý nhiều link từ Google Sheets:

1. **Google Sheets node:**
   - **Range:** `A2:A100` (lấy nhiều link)
   - **Return All:** `ON`

2. **Thêm node "Split In Batches"** sau Google Sheets (nếu cần)
   - **Batch Size:** `1` (xử lý từng link một)

3. **Các node tiếp theo sẽ tự động loop qua từng link**

---

## ⚠️ LƯU Ý

1. **Format URL:** Script hỗ trợ các format:
   - ✅ **Video URL:**
     - `https://www.youtube.com/watch?v=VIDEO_ID`
     - `https://youtu.be/VIDEO_ID`
     - `https://www.youtube.com/embed/VIDEO_ID`
     - `VIDEO_ID` (chỉ ID, 11 ký tự)
   - ✅ **Channel URL (sẽ lấy video mới nhất):**
     - `https://www.youtube.com/c/CHANNEL_NAME`
     - `https://www.youtube.com/channel/CHANNEL_ID`
     - `https://www.youtube.com/user/USER_NAME`
     - `https://www.youtube.com/@HANDLE`

2. **Error Handling:** 
   - Nếu không tìm thấy Video ID từ video URL, script sẽ trả về JSON error
   - Nếu là channel URL, script sẽ tự động lấy video mới nhất từ channel đó

3. **Fallback:** Nếu không có `--video-id`, script sẽ lấy video mới nhất từ kênh mặc định (như cũ)

4. **Lỗi "The connection cannot be established":**
   - Kiểm tra container n8n có internet không: `docker exec -it n8n-data-n8n-1 ping -c 2 youtube.com`
   - Kiểm tra scrapetube có hoạt động: `docker exec -it n8n-data-n8n-1 sh -c 'source /opt/venv/bin/activate && python3 -c "import scrapetube; print(\"OK\")"'`

---

## 🧪 TEST

Sau khi thêm node, test bằng cách:

1. **Thêm link vào Google Sheet** (cột A, hàng 2)
2. **Chạy workflow thủ công** (Manual Trigger)
3. **Kiểm tra output** của node "Extract Video ID" và "Execute Script"

---

## 📌 TÓM TẮT CÁC BƯỚC

1. ✅ Script đã được cập nhật (hỗ trợ URL và Video ID)
2. ➕ Thêm node **Google Sheets (Read)** để lấy link
3. ➕ Thêm node **Code** để trích xuất Video ID
4. ✏️ Sửa node **Execute Script** để truyền `--video-id "{{ $json.videoId }}"`

**Xong!** Flow giờ sẽ lấy link động từ Google Sheets thay vì lấy video mới nhất từ kênh.


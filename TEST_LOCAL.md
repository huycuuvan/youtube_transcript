# 🧪 TEST SCRIPT TRÊN MÁY LOCAL

## ✅ Đã cài yt-dlp

Bạn đã cài yt-dlp thành công! Giờ test script.

---

## 🚀 CÁC LỆNH TEST

### Test 1: Lấy video mới nhất từ kênh mặc định

```powershell
python auto_extractor_json.py --output-json
```

### Test 2: Lấy video từ channel URL cụ thể

```powershell
python auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24"
```

### Test 3: Lấy video từ video ID cụ thể

```powershell
python auto_extractor_json.py --output-json --video-id "dQw4w9WgXcQ"
```

### Test 4: Lấy video từ video URL đầy đủ

```powershell
python auto_extractor_json.py --output-json --video-id "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Test 5: Lấy video từ channel URL khác

```powershell
python auto_extractor_json.py --output-json --video-id "https://www.youtube.com/@channelname"
```

---

## 📋 XEM KẾT QUẢ

### Lưu kết quả vào file JSON

```powershell
python auto_extractor_json.py --output-json --video-id "dQw4w9WgXcQ" > test_output.json
```

Sau đó mở file `test_output.json` để xem.

### Xem kết quả trực tiếp (format đẹp)

```powershell
python auto_extractor_json.py --output-json --video-id "dQw4w9WgXcQ" | python -m json.tool
```

---

## 🔍 KIỂM TRA CÁC TRƯỜNG DỮ LIỆU

Sau khi chạy, kiểm tra JSON output có đầy đủ:

- ✅ `title`
- ✅ `description`
- ✅ `tags`
- ✅ `keywords`
- ✅ `hashtags`
- ✅ `playlist`
- ✅ `thumbnail`
- ✅ `thumbnails`
- ✅ `thumbnailText`
- ✅ `timestamp1`, `timestamp2`, `timestamp3`
- ✅ `category`
- ✅ `visibility`
- ✅ `audience`
- ✅ `location`
- ✅ `viewCount`, `likeCount`, `commentCount`
- ✅ `duration`
- ✅ `uploadDate`
- ✅ `channel`, `channelId`, `channelUrl`
- ✅ `transcript`
- ✅ Và các trường khác...

---

## ⚠️ LƯU Ý

1. **Nếu không có transcript:** Script vẫn chạy và trả về metadata
2. **Nếu video không có thông tin nào:** Field sẽ là `""`, `[]`, `0`, hoặc `null`
3. **Nếu lỗi:** Kiểm tra internet và thử lại

---

## 🎯 QUICK TEST

**Test nhanh với video phổ biến:**

```powershell
python auto_extractor_json.py --output-json --video-id "dQw4w9WgXcQ" | python -m json.tool
```

**Hoặc test với channel:**

```powershell
python auto_extractor_json.py --output-json --video-id "https://www.youtube.com/c/TH%E1%BB%9CIS%E1%BB%B0TV24" | python -m json.tool
```

---

**Chạy các lệnh trên để test!** ✅


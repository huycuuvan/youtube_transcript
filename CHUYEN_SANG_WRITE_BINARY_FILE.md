# Chuyển sang Node "Write Binary File"

## Vấn đề

Node "Read/Write Files from Disk" **không có option riêng** cho File Name trong n8n version của bạn. Node này chỉ có field "File Path and Name" chung, và khi bạn nhập full path thì bị lỗi.

## Giải pháp: Dùng Node "Write Binary File"

Node "Write Binary File" có **2 fields riêng biệt**:
- **File Path**: Chỉ thư mục
- **File Name**: Tên file (có thể dùng expression)

## Các bước thực hiện

### Bước 1: Xóa node "Read/Write Files from Disk"

1. Quay lại **canvas** (click "Back to canvas")
2. Click vào node **"Read/Write Files from Disk"**
3. Press `Delete` hoặc right-click → **Delete**

### Bước 2: Thêm node "Write Binary File"

1. Click vào node **"Text to Speech (OpenAI)"** (hoặc "Text to Speech (NCA)")
2. Bạn sẽ thấy dấu **"+"** ở output của node
3. Click dấu **"+"
4. Gõ **"Write Binary File"** trong search bar
5. Chọn node **"Write Binary File"** từ kết quả

### Bước 3: Cấu hình node "Write Binary File"

Click vào node vừa thêm, cấu hình:

#### 1. File Name:
- Click vào field **"File Name"**
- Click icon **`fx`** để bật expression mode
- Nhập expression:
  ```javascript
  {{ `audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3` }}
  ```
  Hoặc đơn giản hơn:
  ```
  audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3
  ```

#### 2. File Path:
- Click vào field **"File Path"**
- Nhập:
  ```
  /home/node/output
  ```

#### 3. Input Binary Field:
- Click vào field **"Input Binary Field"**
- Nhập: `data` (hoặc `audio` - kiểm tra output của node TTS)
- Để kiểm tra: Click node "Text to Speech" → Tab "OUTPUT" → Tab "Binary" → Xem field name

### Bước 4: Test node

1. Click **"Execute step"** trên node "Write Binary File"
2. Kiểm tra output:
   - Sẽ có 3 items (tương ứng 3 chunks)
   - Mỗi item có `fileName` trong JSON output
3. Kiểm tra files đã được tạo:
   ```bash
   docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/
   ```
   Sẽ thấy:
   - `audio_chunk_0_*.mp3`
   - `audio_chunk_1_*.mp3`
   - `audio_chunk_2_*.mp3`

## So sánh 2 Nodes

| Tính năng | Read/Write Files from Disk | Write Binary File |
|-----------|---------------------------|-------------------|
| File Path | Chỉ directory | Chỉ directory |
| File Name | ❌ Không có field riêng | ✅ Có field riêng |
| Expression | Phức tạp | Dễ dùng |
| Phù hợp | Đọc/Ghi file text | ✅ Ghi binary data |

## Cấu hình chi tiết

### File Name Expression

**Cách 1: Template string (đơn giản)**
```
audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3
```

**Cách 2: JavaScript expression (dùng fx)**
```javascript
{{ `audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3` }}
```

**Cách 3: Nếu chunkIndex không có**
```javascript
{{ `audio_chunk_${$input.item.json.chunkIndex || 0}_${Date.now()}.mp3` }}
```

### Input Binary Field

Để biết chính xác field name:

1. Click node **"Text to Speech (OpenAI)"**
2. Xem tab **"OUTPUT"**
3. Click tab **"Binary"**
4. Xem field name là gì:
   - Nếu thấy `data` → Nhập `data`
   - Nếu thấy `audio` → Nhập `audio`

## Flow sau khi chuyển

```
Text to Speech (OpenAI)
    ↓ (3 items, mỗi item có binary.data)
Write Binary File
    ↓ (File Name: audio_chunk_{{ $json.chunkIndex }}.mp3)
    ↓ (File Path: /home/node/output)
    ↓ (3 files được tạo)
Code (Create File List)
    ↓
Execute Command (FFmpeg Merge)
```

## Troubleshooting

### Lỗi: "File name is required"
- **Nguyên nhân**: File Name field trống
- **Giải pháp**: Đảm bảo đã nhập expression trong File Name

### Lỗi: "Binary field not found"
- **Nguyên nhân**: Input Binary Field sai
- **Giải pháp**: Kiểm tra output của node TTS, xem field name là `data` hay `audio`

### Files không được tạo
- **Kiểm tra**: Thư mục `/home/node/output` có tồn tại không
- **Giải pháp**: 
  ```bash
  docker exec -it n8n-data-n8n-1 mkdir -p /home/node/output && chmod 777 /home/node/output
  ```

### File name không động (tất cả cùng tên)
- **Nguyên nhân**: Expression không được evaluate
- **Giải pháp**: 
  - Đảm bảo đã click icon `fx` để bật expression mode
  - Hoặc dùng `{{ }}` syntax

## Lưu ý

1. **Node "Write Binary File"** phù hợp hơn cho binary data (audio, image, video)
2. **File Name** có thể dùng expression để tạo tên động
3. **File Path** chỉ cần directory, không cần filename
4. **Input Binary Field** phải khớp với output của node trước

## Next Steps

Sau khi node "Write Binary File" chạy thành công:
1. ✅ 3 files audio chunks đã được lưu
2. ⬜ Thêm node "Code" để tạo file list
3. ⬜ Thêm node "Execute Command" để merge bằng FFmpeg

Bạn đã thêm node "Write Binary File" chưa? Cần tôi giải thích thêm phần nào không?



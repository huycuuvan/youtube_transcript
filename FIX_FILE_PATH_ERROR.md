# Fix Lỗi: "The directory path was expected but the given path is a file"

## Vấn đề

Node "Read/Write Files from Disk" yêu cầu:
- **File Path**: Chỉ là thư mục (không có tên file)
- **File Name**: Tên file riêng biệt

Nhưng bạn đang cung cấp full path: `/home/node/output/audio_chunk_0_*.mp3`

## Giải pháp 1: Sửa Node "Read/Write Files from Disk" (Khuyến nghị)

### Cách 1: Tách File Path và File Name

1. **File Path and Name**: Chỉ nhập thư mục
   ```
   /home/node/output
   ```

2. **Thêm Option**: Click "Add option" → Chọn "File Name"
   - **File Name**: `={{ \`audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3\` }}`

### Cách 2: Dùng Expression cho File Path

1. **File Path and Name**: 
   ```
   /home/node/output
   ```

2. **Add Option → File Name**:
   ```
   audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3
   ```

## Giải pháp 2: Dùng Node "Write Binary File" (Tốt hơn)

Node "Write Binary File" có 2 fields riêng biệt, dễ dùng hơn:

### Cách thêm:
1. **Xóa node "Read/Write Files from Disk"** hiện tại
2. **Thêm node "Write Binary File"**:
   - Click node "Text to Speech (OpenAI)"
   - Click dấu "+"
   - Gõ "Write Binary File" và chọn

### Cấu hình:
- **File Name**: `={{ \`audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3\` }}`
- **File Path**: `/home/node/output`
- **Input Binary Field**: `data` (hoặc `audio` - kiểm tra output của node TTS)

## So sánh 2 Nodes

| Node | File Path | File Name | Ưu điểm |
|------|-----------|-----------|---------|
| **Read/Write Files from Disk** | Chỉ directory | Option riêng | Linh hoạt |
| **Write Binary File** | Chỉ directory | Field riêng | Dễ dùng hơn |

## Hướng dẫn Chi tiết: Sửa Node "Read/Write Files from Disk"

### Bước 1: Sửa File Path
1. Click vào field "File Path and Name"
2. Xóa expression hiện tại
3. Chỉ nhập: `/home/node/output`

### Bước 2: Thêm File Name Option
1. Scroll xuống phần "Options"
2. Click "Add option"
3. Chọn "File Name" từ dropdown
4. Nhập expression:
   ```
   audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3
   ```
   Hoặc dùng `fx`:
   ```
   {{ `audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3` }}
   ```

### Bước 3: Test
1. Click "Execute step"
2. Kiểm tra xem file có được tạo không

## Hướng dẫn Chi tiết: Dùng Node "Write Binary File" (Khuyến nghị)

### Bước 1: Xóa node cũ
1. Click node "Read/Write Files from Disk"
2. Press `Delete` hoặc right-click → Delete

### Bước 2: Thêm node mới
1. Click node "Text to Speech (OpenAI)"
2. Click dấu "+" ở output
3. Gõ "Write Binary File" và chọn

### Bước 3: Cấu hình
1. **File Name**: 
   - Click icon `fx`
   - Nhập: `={{ \`audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3\` }}`

2. **File Path**: 
   ```
   /home/node/output
   ```

3. **Input Binary Field**: 
   - Kiểm tra output của node TTS
   - Thường là `data` hoặc `audio`

### Bước 4: Test
1. Click "Execute step"
2. Kiểm tra output → Sẽ thấy 3 files được tạo

## Code Expression cho File Name

### Cách 1: Template string
```
audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3
```

### Cách 2: JavaScript expression (dùng fx)
```javascript
{{ `audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3` }}
```

### Cách 3: Concatenation
```javascript
{{ 'audio_chunk_' + $json.chunkIndex + '_' + Date.now() + '.mp3' }}
```

## Kiểm tra Input Binary Field

Để biết chính xác field name:

1. Click node "Text to Speech (OpenAI)"
2. Xem tab "OUTPUT" → Tab "Binary"
3. Xem field name là gì (thường là `data` hoặc `audio`)

## Troubleshooting

### Vẫn báo lỗi "directory expected"
- **Kiểm tra**: File Path có chứa tên file không
- **Giải pháp**: Chỉ để directory: `/home/node/output`

### File không được tạo
- **Kiểm tra**: File Name option có được thêm chưa
- **Giải pháp**: Đảm bảo có option "File Name" với expression đúng

### File name không động
- **Kiểm tra**: Expression có dùng `fx` icon không
- **Giải pháp**: Click icon `fx` và nhập expression

## Khuyến nghị

**Dùng node "Write Binary File"** vì:
- ✅ Có 2 fields riêng biệt (File Path và File Name)
- ✅ Dễ cấu hình hơn
- ✅ Ít lỗi hơn
- ✅ Phù hợp với binary data

## Sau khi fix

Sau khi sửa xong, test lại:
1. Click "Execute step"
2. Nếu thành công, bạn sẽ thấy:
   - 3 items trong output
   - Mỗi item có `fileName` trong JSON
   - Files được tạo trong `/home/node/output`

Bạn muốn sửa node hiện tại hay thay bằng "Write Binary File"?



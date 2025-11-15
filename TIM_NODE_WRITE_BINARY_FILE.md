# Cách Tìm Node "Write Binary File" trong n8n

## Vấn đề

Bạn đang thấy danh sách "Convert to File" actions, nhưng cần tìm node **"Write Binary File"**.

## Cách tìm đúng

### Cách 1: Tìm trực tiếp

1. **Xóa text trong search bar** (nếu có)
2. **Gõ chính xác**: `Write Binary File`
3. Hoặc gõ: `Write Binary`
4. Hoặc gõ: `Binary File`

### Cách 2: Tìm trong danh mục

1. **Quay lại** (click mũi tên back)
2. **Tìm theo category**:
   - Gõ: `file`
   - Hoặc: `write`
   - Hoặc: `binary`
3. **Tìm node có icon** giống như:
   - 📄 File icon
   - 💾 Save icon
   - Không phải icon "Convert" (mũi tên)

### Cách 3: Tìm trong Core Nodes

Node "Write Binary File" là **core node** của n8n, nên:

1. **Xóa search bar**
2. **Scroll xuống** xem các core nodes
3. Tìm trong section **"Files"** hoặc **"Core"**

## Tên node chính xác

Node có thể có tên:
- ✅ **"Write Binary File"** (tên đầy đủ)
- ✅ **"Write Binary"** (tên ngắn)
- ✅ **"Binary File"** (tên khác)

## Phân biệt với "Convert to File"

| Node | Icon | Mục đích |
|------|------|----------|
| **Convert to File** | 🔄 Convert icon | Chuyển đổi format (CSV, JSON, etc.) |
| **Write Binary File** | 📄 File icon | ✅ Lưu binary data (audio, image) vào file |

## Nếu không tìm thấy

### Cách 1: Dùng node khác tương đương

Nếu không có "Write Binary File", có thể dùng:

1. **"Read/Write Files from Disk"**:
   - Operation: "Write File to Disk"
   - File Path: `/home/node/output`
   - File Name: Dùng trong expression của File Path
   - Input Binary Field: `data`

2. **"HTTP Request"** để upload lên MinIO/S3

### Cách 2: Kiểm tra n8n version

Node "Write Binary File" có thể không có trong version cũ. Kiểm tra:

```bash
# Xem n8n version
docker exec -it n8n-data-n8n-1 n8n --version
```

Nếu version < 1.0, có thể cần update hoặc dùng node khác.

## Hướng dẫn chi tiết: Tìm node

### Bước 1: Quay lại
- Click **mũi tên back** (góc trên bên trái)
- Hoặc click **"Back to canvas"**

### Bước 2: Click dấu "+"
- Click vào node **"Text to Speech (OpenAI)"**
- Click dấu **"+"** ở output

### Bước 3: Tìm node
- **Xóa** text trong search bar (nếu có)
- **Gõ**: `write binary`
- Hoặc: `binary file`
- Hoặc: `write file`

### Bước 4: Chọn node
- Tìm node có **icon file** (không phải icon convert)
- Tên: **"Write Binary File"** hoặc tương tự
- Click để chọn

## Screenshot mô tả

Node "Write Binary File" sẽ có:
- **Icon**: 📄 File icon (màu xanh hoặc trắng)
- **Tên**: "Write Binary File" hoặc "Write Binary"
- **Category**: Files / Core Nodes
- **Không phải**: "Convert to File" (có icon mũi tên)

## Alternative: Dùng "Read/Write Files from Disk"

Nếu vẫn không tìm thấy "Write Binary File", dùng "Read/Write Files from Disk":

### Cấu hình:
1. **Operation**: "Write File to Disk"
2. **File Path and Name**: 
   ```
   /home/node/output/audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3
   ```
   (Dùng full path với expression)
3. **Input Binary Field**: `data`

## Quick Check

Để biết node nào có sẵn:

1. Click dấu **"+"** 
2. **Không gõ gì** trong search bar
3. **Scroll** xem tất cả nodes
4. Tìm trong section **"Files"**

Bạn có thấy node nào có tên "Write Binary" hoặc "Write File" không? Nếu không, chúng ta sẽ dùng "Read/Write Files from Disk" với full path expression.



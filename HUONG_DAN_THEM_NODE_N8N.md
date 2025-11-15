# Hướng dẫn Thêm Node trong n8n

## Cách 1: Thêm Node từ Canvas (Khuyến nghị)

### Bước 1: Quay lại Canvas
1. Click **"Back to canvas"** ở góc trên bên trái
2. Bạn sẽ thấy toàn bộ workflow với các nodes đã có

### Bước 2: Thêm Node mới
1. **Tìm vị trí muốn thêm node**:
   - Click vào node trước đó (ví dụ: "Text to Speech (OpenAI)")
   - Bạn sẽ thấy một **dấu "+"** xuất hiện ở output của node đó

2. **Click vào dấu "+"**:
   - Một search bar sẽ hiện ra
   - Gõ tên node bạn muốn thêm (ví dụ: "Write Binary File", "Read/Write Files", "Code", etc.)

3. **Chọn node từ kết quả tìm kiếm**:
   - n8n sẽ tự động kết nối node mới với node trước đó

### Bước 3: Cấu hình Node
1. Click vào node vừa thêm
2. Cấu hình các parameters trong panel bên phải
3. Click **"Execute step"** để test node

## Cách 2: Thêm Node từ Menu

1. Ở canvas, click **"+"** ở bất kỳ đâu
2. Hoặc click **"Add node"** button ở toolbar
3. Tìm và chọn node từ danh sách
4. Kéo node đến vị trí mong muốn
5. Kết nối node bằng cách kéo từ output của node này đến input của node khác

## Cách 3: Thêm Node giữa 2 Nodes đã có

1. **Xóa connection** giữa 2 nodes:
   - Click vào connection line giữa 2 nodes
   - Press `Delete` hoặc click "Remove connection"

2. **Thêm node mới**:
   - Click dấu "+" ở output của node đầu tiên
   - Chọn node mới
   - Node mới sẽ tự động kết nối

3. **Kết nối node mới với node cuối**:
   - Kéo từ output của node mới đến input của node cuối

## Các Node Phổ biến cho Workflow của bạn

### 1. **Write Binary File** (Lưu file audio)
- **Tìm**: Gõ "Write Binary File" hoặc "Write File"
- **Dùng khi**: Cần lưu binary data (audio, image, video) vào disk
- **Parameters**:
  - File Name: `audio_chunk_{{ $json.chunkIndex }}.mp3`
  - File Path: `/home/node/output`
  - Input Binary Field: `audio` (hoặc `data`)

### 2. **Read/Write Files from Disk** (Đọc/Ghi file)
- **Tìm**: Gõ "Read/Write Files"
- **Dùng khi**: Cần đọc/ghi file từ disk
- **Parameters**:
  - Operation: "Write File to Disk"
  - File Path and Name: `/home/node/output/audio_chunk_0.mp3`
  - Input Binary Field: `data`

### 3. **Code** (JavaScript)
- **Tìm**: Gõ "Code"
- **Dùng khi**: Cần xử lý data, transform, merge, etc.
- **Ví dụ**: Merge audio chunks, parse JSON, etc.

### 4. **Execute Command** (Chạy lệnh shell)
- **Tìm**: Gõ "Execute Command"
- **Dùng khi**: Cần chạy FFmpeg, Python script, etc.
- **Ví dụ**: `ffmpeg -f concat -i list.txt -c copy output.mp3`

### 5. **HTTP Request** (Gọi API)
- **Tìm**: Gõ "HTTP Request"
- **Dùng khi**: Gọi OpenAI API, NCA Toolkit, etc.

### 6. **IF** (Điều kiện)
- **Tìm**: Gõ "IF"
- **Dùng khi**: Cần phân nhánh workflow dựa trên điều kiện

### 7. **Merge** (Gộp data)
- **Tìm**: Gõ "Merge"
- **Dùng khi**: Cần gộp nhiều items thành một

## Ví dụ: Thêm Node "Write Binary File" sau "Text to Speech"

### Bước 1: Quay lại Canvas
- Click **"Back to canvas"**

### Bước 2: Thêm Node
1. Click vào node **"Text to Speech (OpenAI)"**
2. Bạn sẽ thấy dấu **"+"** ở output của node
3. Click dấu **"+"**
4. Gõ **"Write Binary File"** hoặc **"Write File"**
5. Chọn node từ kết quả

### Bước 3: Cấu hình
1. Click vào node **"Write Binary File"** vừa thêm
2. Trong panel bên phải, cấu hình:
   - **File Name**: `={{ \`audio_chunk_${$json.chunkIndex}_${Date.now()}.mp3\` }}`
   - **File Path**: `/home/node/output`
   - **Input Binary Field**: `audio` (hoặc `data` - tùy vào output của node TTS)

### Bước 4: Test
1. Click **"Execute step"** để test node
2. Kiểm tra output xem file đã được lưu chưa

## Lưu ý quan trọng

### 1. **Binary Data Field Name**
- Node "Text to Speech (OpenAI)" trả về binary trong `$binary.audio` (vì `outputPropertyName: "audio"`)
- Node "Write Binary File" cần biết field name này
- Nếu không chắc, kiểm tra output của node TTS:
  - Click node TTS → Xem tab "OUTPUT" → Tab "Binary"
  - Xem field name là `audio` hay `data`

### 2. **File Path**
- Đảm bảo path tồn tại và có quyền ghi
- Trong Docker: `/home/node/output` phải được mount trong `docker-compose.yml`

### 3. **Kết nối Nodes**
- Nodes sẽ tự động kết nối khi thêm từ dấu "+"
- Có thể kết nối thủ công bằng cách kéo từ output của node này đến input của node khác

### 4. **Multiple Outputs**
- Một node có thể có nhiều outputs (ví dụ: IF node có 2 outputs: true/false)
- Kết nối từng output đến node tương ứng

## Troubleshooting

### Không thấy dấu "+"
- Đảm bảo bạn đang ở canvas (không phải trong configuration panel)
- Click vào node để thấy output connection point

### Node không kết nối được
- Kiểm tra xem node có output không (một số node chỉ có input)
- Kiểm tra data type: một số node chỉ nhận binary, một số chỉ nhận JSON

### Không tìm thấy node
- Thử tìm với tên khác (ví dụ: "Write File" thay vì "Write Binary File")
- Kiểm tra xem node có phải community node không (cần cài thêm)

## Quick Reference: Node Names trong n8n

| Chức năng | Node Name trong n8n |
|-----------|-------------------|
| Lưu binary file | `Write Binary File` |
| Đọc/Ghi file | `Read/Write Files from Disk` |
| Chạy code JS | `Code` |
| Chạy lệnh shell | `Execute Command` |
| Gọi API | `HTTP Request` |
| Điều kiện | `IF` |
| Gộp data | `Merge` |
| Split data | `Split Out` |
| Lặp qua items | `Loop Over Items` |

## Ví dụ Workflow: Save Audio Chunks

```
Text to Speech (OpenAI)
    ↓
Write Binary File
    ↓ (File Name: audio_chunk_{{ $json.chunkIndex }}.mp3)
    ↓ (File Path: /home/node/output)
    ↓ (Input Binary Field: audio)
Code (Create File List)
    ↓
Execute Command (FFmpeg Merge)
```

Cần tôi giải thích thêm phần nào không?



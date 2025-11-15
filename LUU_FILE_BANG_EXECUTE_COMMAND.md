# Lưu File Audio bằng Execute Command Node

## Vấn đề

Node "Write Binary File" không có trong n8n của bạn. Cần cách khác để lưu binary audio data vào file.

## Giải pháp: Dùng "Execute Command" Node

Dùng node "Execute Command" để chạy lệnh shell ghi binary data vào file.

## Các bước thực hiện

### Bước 1: Thêm node "Execute Command"

1. Click node **"Text to Speech (OpenAI)"**
2. Click dấu **"+"** ở output
3. Gõ **"Execute Command"** và chọn

### Bước 2: Cấu hình node

#### Command:
```bash
cd /home/node/output && echo "{{ $binary.data.data }}" | base64 -d > "audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3"
```

**Hoặc cách tốt hơn** - dùng `cat` với here-document:

```bash
cd /home/node/output && cat > "audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3" << 'EOF'
{{ $binary.data.data }}
EOF
```

**Hoặc cách đơn giản nhất** - dùng Python script:

```bash
cd /home/node/output && python3 -c "
import sys
import base64
import json

# Read input from stdin
data = sys.stdin.read()
try:
    # Try to parse as JSON
    item = json.loads(data)
    # Get binary data
    binary_data = item.get('binary', {}).get('data', {}).get('data', '')
    # Decode base64 if needed
    if binary_data:
        audio_bytes = base64.b64decode(binary_data)
        # Write to file
        filename = f\"audio_chunk_{item.get('json', {}).get('chunkIndex', 0)}_{item.get('json', {}).get('timestamp', '')}.mp3\"
        with open(filename, 'wb') as f:
            f.write(audio_bytes)
        print(f\"File saved: {filename}\")
except Exception as e:
    print(f\"Error: {e}\", file=sys.stderr)
    sys.exit(1)
"
```

## Giải pháp Tốt nhất: Dùng Code Node + Execute Command

### Bước 1: Thêm node "Code" để prepare data

Sau node "Text to Speech (OpenAI)", thêm node "Code":

```javascript
// Prepare binary data for file writing
const binaryData = $input.item.binary?.data || $input.item.binary?.audio;

if (!binaryData) {
  throw new Error('No binary data found');
}

// Get binary data as base64
let base64Data;
if (Buffer.isBuffer(binaryData.data)) {
  base64Data = binaryData.data.toString('base64');
} else if (typeof binaryData.data === 'string') {
  base64Data = binaryData.data;
} else {
  throw new Error('Invalid binary data format');
}

// Get chunk index
const chunkIndex = $input.item.json.chunkIndex || 0;
const timestamp = Date.now();
const fileName = `audio_chunk_${chunkIndex}_${timestamp}.mp3`;

return {
  json: {
    ...$input.item.json,
    fileName: fileName,
    base64Data: base64Data,
    filePath: `/home/node/output/${fileName}`
  }
};
```

### Bước 2: Thêm node "Execute Command" để ghi file

Sau node "Code", thêm node "Execute Command":

#### Command:
```bash
cd /home/node/output && echo "{{ $json.base64Data }}" | base64 -d > "{{ $json.fileName }}"
```

**Hoặc dùng Python (an toàn hơn):**

```bash
cd /home/node/output && python3 << 'PYTHON_SCRIPT'
import sys
import base64
import json

# Read JSON from stdin
data = sys.stdin.read()
item = json.loads(data)

# Decode base64
audio_bytes = base64.b64decode(item['base64Data'])

# Write file
with open(item['fileName'], 'wb') as f:
    f.write(audio_bytes)

print(f"File saved: {item['fileName']}")
PYTHON_SCRIPT
```

**Input cho Python script:**
- Trong node "Execute Command", cần pass JSON data vào stdin
- Có thể dùng: `echo '{{ JSON.stringify($json) }}' | python3 ...`

## Giải pháp Đơn giản nhất: Dùng Code Node để ghi file trực tiếp

Nếu n8n cho phép, có thể dùng Code node với `fs` module:

```javascript
const fs = require('fs');
const path = require('path');

const binaryData = $input.item.binary?.data || $input.item.binary?.audio;

if (!binaryData) {
  throw new Error('No binary data found');
}

// Get binary buffer
let buffer;
if (Buffer.isBuffer(binaryData.data)) {
  buffer = binaryData.data;
} else if (typeof binaryData.data === 'string') {
  buffer = Buffer.from(binaryData.data, 'base64');
} else {
  throw new Error('Invalid binary data format');
}

// Get chunk index
const chunkIndex = $input.item.json.chunkIndex || 0;
const timestamp = Date.now();
const fileName = `audio_chunk_${chunkIndex}_${timestamp}.mp3`;
const filePath = `/home/node/output/${fileName}`;

// Write file
fs.writeFileSync(filePath, buffer);

return {
  json: {
    ...$input.item.json,
    fileName: fileName,
    filePath: filePath,
    fileSize: buffer.length
  }
};
```

## Giải pháp Khuyến nghị: Dùng Execute Command với base64

### Node "Execute Command":

**Command:**
```bash
cd /home/node/output && echo "{{ $binary.data.data }}" | base64 -d > "audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3" && echo "Saved: audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3"
```

**Lưu ý:**
- `$binary.data.data` là base64 string từ OpenAI TTS
- `base64 -d` decode base64 thành binary
- `>` ghi vào file

## Flow hoàn chỉnh

```
Text to Speech (OpenAI)
    ↓ (3 items, mỗi item có binary.data)
Execute Command (Save Audio Chunk)
    ↓ (Command: base64 decode và ghi file)
    ↓ (3 files: audio_chunk_0_*.mp3, audio_chunk_1_*.mp3, audio_chunk_2_*.mp3)
Code (Create File List)
    ↓
Execute Command (FFmpeg Merge)
```

## Kiểm tra Binary Data Format

Để biết chính xác format của binary data:

1. Click node "Text to Speech (OpenAI)"
2. Xem tab "OUTPUT" → Tab "Binary"
3. Xem structure:
   - Nếu là `data.data` (base64 string) → Dùng `base64 -d`
   - Nếu là `data.data` (Buffer) → Cần convert sang base64 trước

## Troubleshooting

### Lỗi: "base64: invalid input"
- **Nguyên nhân**: Binary data không phải base64
- **Giải pháp**: Kiểm tra format, có thể cần dùng Python script

### Lỗi: "No such file or directory"
- **Nguyên nhân**: Thư mục `/home/node/output` chưa tồn tại
- **Giải pháp**: 
  ```bash
  docker exec -it n8n-data-n8n-1 mkdir -p /home/node/output && chmod 777 /home/node/output
  ```

### File không được tạo
- **Kiểm tra**: Command có chạy thành công không
- **Giải pháp**: Xem output của node "Execute Command", có error message không

## Quick Test Command

Test trực tiếp trong container:

```bash
# Vào container
docker exec -it n8n-data-n8n-1 sh

# Test base64 decode
echo "base64_string_here" | base64 -d > test.mp3

# Kiểm tra file
ls -lh /home/node/output/test.mp3
```

Bạn muốn thử cách nào? Tôi khuyến nghị dùng **Execute Command với base64 decode** (đơn giản nhất).



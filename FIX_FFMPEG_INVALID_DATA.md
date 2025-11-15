# Fix: FFmpeg "Invalid data found when processing input"

## Vấn đề

FFmpeg báo lỗi:
- `Failed to find two consecutive MPEG audio frames`
- `Invalid data found when processing input`
- `Impossible to open '/home/node/output/audio_chunk_0_*.mp3'`

**Nguyên nhân có thể:**
1. Files không được lưu đúng (base64 decode sai)
2. Files bị corrupt hoặc rỗng
3. Files không tồn tại

## Kiểm tra Files

### Bước 1: Kiểm tra files có tồn tại không

```bash
docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/audio_chunk_*.mp3
```

### Bước 2: Kiểm tra file size

```bash
docker exec -it n8n-data-n8n-1 sh -c "cd /home/node/output && for f in audio_chunk_*.mp3; do echo \"$f: $(stat -c%s \"$f\") bytes\"; done"
```

Nếu files có size = 0 hoặc rất nhỏ → Files bị corrupt.

### Bước 3: Kiểm tra file có phải MP3 hợp lệ không

```bash
docker exec -it n8n-data-n8n-1 sh -c "cd /home/node/output && file audio_chunk_*.mp3"
```

Hoặc test với FFmpeg:

```bash
docker exec -it n8n-data-n8n-1 sh -c "cd /home/node/output && ffmpeg -i audio_chunk_0_*.mp3 -f null - 2>&1 | head -20"
```

## Giải pháp: Sửa cách lưu file

Vấn đề có thể là base64 decode không đúng. Sửa command lưu file:

### Cách 1: Dùng Python để decode base64 đúng cách

Sửa command trong node "Execute Command" (Save Audio Chunk):

```bash
cd /home/node/output && python3 << 'PYTHON_SCRIPT'
import sys
import base64
import json

# Read input from stdin
try:
    # Get binary data from environment or stdin
    # n8n passes data differently, need to get from binary field
    import os
    
    # Try to get from stdin (if passed as JSON)
    data = sys.stdin.read()
    if data:
        item = json.loads(data)
        binary_data = item.get('binary', {}).get('data', {}).get('data', '')
    else:
        # Fallback: read from environment
        binary_data = os.environ.get('BINARY_DATA', '')
    
    if not binary_data:
        print("Error: No binary data found", file=sys.stderr)
        sys.exit(1)
    
    # Decode base64
    audio_bytes = base64.b64decode(binary_data)
    
    # Get chunk index
    chunk_index = item.get('json', {}).get('chunkIndex', 0) if data else 0
    timestamp = item.get('json', {}).get('timestamp', '') if data else ''
    
    # Write file
    filename = f"audio_chunk_{chunk_index}_{timestamp}.mp3"
    with open(filename, 'wb') as f:
        f.write(audio_bytes)
    
    print(f"Saved: {filename} ({len(audio_bytes)} bytes)")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT
```

**Vấn đề**: n8n không pass binary data qua stdin dễ dàng.

### Cách 2: Dùng Code Node để prepare data trước

Thêm node "Code" trước "Execute Command" (Save Chunk):

```javascript
// Prepare binary data for file writing
const binaryData = $input.item.binary?.data || $input.item.binary?.audio;

if (!binaryData) {
  throw new Error('No binary data found');
}

// Get binary data as Buffer
let buffer;
if (Buffer.isBuffer(binaryData.data)) {
  buffer = binaryData.data;
} else if (typeof binaryData.data === 'string') {
  // If it's base64, decode it
  buffer = Buffer.from(binaryData.data, 'base64');
} else if (binaryData.data instanceof Uint8Array) {
  buffer = Buffer.from(binaryData.data);
} else {
  throw new Error('Invalid binary data format');
}

// Convert to base64 for passing to command
const base64Data = buffer.toString('base64');

// Get chunk index
const chunkIndex = $input.item.json.chunkIndex || 0;
const timestamp = Date.now();
const fileName = `audio_chunk_${chunkIndex}_${timestamp}.mp3`;

return {
  json: {
    ...$input.item.json,
    fileName: fileName,
    base64Data: base64Data,
    filePath: `/home/node/output/${fileName}`,
    fileSize: buffer.length
  }
};
```

Sau đó sửa command trong "Execute Command":

```bash
cd /home/node/output && echo "{{ $json.base64Data }}" | base64 -d > "{{ $json.fileName }}" && echo "Saved: {{ $json.fileName }} ({{ $json.fileSize }} bytes)"
```

### Cách 3: Kiểm tra và fix file list format

Kiểm tra file list có đúng format không:

```bash
docker exec -it n8n-data-n8n-1 cat /home/node/output/audio_list_*.txt
```

Phải có format:
```
file '/home/node/output/audio_chunk_0_xxx.mp3'
file '/home/node/output/audio_chunk_1_xxx.mp3'
file '/home/node/output/audio_chunk_2_xxx.mp3'
```

**Lưu ý**: Không có dòng trống ở cuối, mỗi dòng kết thúc bằng `\n`.

## Giải pháp Khuyến nghị: Kiểm tra files trước

### Bước 1: Kiểm tra files đã được lưu đúng chưa

```bash
docker exec -it n8n-data-n8n-1 sh -c "
cd /home/node/output
echo '=== Files ==='
ls -lh audio_chunk_*.mp3
echo ''
echo '=== File sizes ==='
for f in audio_chunk_*.mp3; do
  size=\$(stat -c%s \"\$f\")
  echo \"\$f: \$size bytes\"
done
echo ''
echo '=== Test first file ==='
file audio_chunk_0_*.mp3
echo ''
echo '=== FFmpeg test ==='
ffmpeg -i audio_chunk_0_*.mp3 -f null - 2>&1 | head -10
"
```

### Bước 2: Nếu files bị corrupt, sửa command lưu file

Sửa command trong node "Execute Command" (Save Chunk) - **dùng Python**:

```bash
cd /home/node/output && python3 -c "
import sys, base64, json
try:
    # Read from stdin (n8n might pass as JSON string)
    data = sys.stdin.read()
    if data:
        item = json.loads(data)
        base64_data = item.get('base64Data', '')
        filename = item.get('fileName', 'test.mp3')
    else:
        # Fallback
        base64_data = '{{ $json.base64Data }}'
        filename = '{{ $json.fileName }}'
    
    if base64_data:
        audio_bytes = base64.b64decode(base64_data)
        with open(filename, 'wb') as f:
            f.write(audio_bytes)
        print(f'Saved: {filename} ({len(audio_bytes)} bytes)')
    else:
        print('Error: No base64 data', file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
" <<< '{{ JSON.stringify($json) }}'
```

## Quick Fix: Kiểm tra và Re-save files

Nếu files đã bị corrupt, cần re-save:

1. **Kiểm tra files hiện tại**:
   ```bash
   docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/audio_chunk_*.mp3
   ```

2. **Nếu files có size = 0 hoặc rất nhỏ**:
   - Xóa files cũ
   - Chạy lại node "Execute Command" (Save Chunk) với command đã sửa

3. **Test lại merge**:
   ```bash
   docker exec -it n8n-data-n8n-1 sh -c "
   cd /home/node/output
   cat > test_list.txt << 'EOF'
   file '/home/node/output/audio_chunk_0_1762741622098.mp3'
   file '/home/node/output/audio_chunk_1_1762741622119.mp3'
   file '/home/node/output/audio_chunk_2_1762741622132.mp3'
   EOF
   ffmpeg -f concat -safe 0 -i test_list.txt -c copy test_merged.mp3 -y
   "
   ```

## Lưu ý

1. **Base64 decode**: Đảm bảo decode đúng, không bị corrupt
2. **File size**: Files phải có size > 0 (thường > 1MB cho audio)
3. **File format**: Phải là MP3 hợp lệ
4. **File list format**: Phải đúng format FFmpeg concat

Bạn có thể chạy lệnh kiểm tra files không? Để xem files có tồn tại và có size đúng không.



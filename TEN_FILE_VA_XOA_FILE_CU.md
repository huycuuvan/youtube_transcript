# Tên File và Xóa File Cũ

## Tên File sau khi Merge

### File Merged (Output cuối cùng):
```
merged_audio_[timestamp].mp3
```

Ví dụ: `merged_audio_1762741269465.mp3`

### Files Chunks (Tạm thời):
```
audio_chunk_0_[timestamp].mp3
audio_chunk_1_[timestamp].mp3
audio_chunk_2_[timestamp].mp3
```

## Có cần xóa file cũ không?

### Khuyến nghị: **CÓ** - Xóa các chunks sau khi merge thành công

**Lý do:**
- ✅ Tiết kiệm dung lượng (mỗi chunk ~5MB, 3 chunks = ~15MB)
- ✅ Tránh đầy disk sau nhiều lần chạy
- ✅ Chunks chỉ là file tạm, không cần sau khi merge

### Khi nào xóa:
- ✅ **Sau khi merge thành công** (exitCode = 0)
- ❌ **Không xóa** nếu merge thất bại (để debug)

## Giải pháp: Thêm node xóa file cũ

### Cách 1: Xóa trong node "Execute Command" (FFmpeg Merge)

Sửa command merge để xóa chunks sau khi merge thành công:

```bash
cd /home/node/output && \
echo -e "{{ $json.fileList }}" > "{{ $json.listFile }}" && \
ffmpeg -f concat -safe 0 -i "{{ $json.listFile }}" -c copy "{{ $json.outputFile }}" -y && \
rm -f {{ $json.filePaths.join(' ') }} && \
rm -f "{{ $json.listFile }}" && \
echo "Merged: {{ $json.outputFile }}"
```

**Hoặc đơn giản hơn** - xóa tất cả chunks:

```bash
cd /home/node/output && \
echo -e "{{ $json.fileList }}" > "{{ $json.listFile }}" && \
ffmpeg -f concat -safe 0 -i "{{ $json.listFile }}" -c copy "{{ $json.outputFile }}" -y && \
rm -f audio_chunk_*.mp3 audio_list_*.txt && \
echo "Merged: {{ $json.outputFile }}"
```

### Cách 2: Thêm node "Execute Command" riêng để xóa

Sau node merge, thêm node "Execute Command" để xóa:

1. Click node "Execute Command" (FFmpeg Merge)
2. Click dấu "+"
3. Gõ "Execute Command" và chọn
4. **Command**:
   ```bash
   cd /home/node/output && rm -f audio_chunk_*.mp3 audio_list_*.txt && echo "Cleaned up chunks"
   ```

### Cách 3: Dùng Code Node để xóa có điều kiện

Thêm node "Code" sau merge để xóa nếu merge thành công:

```javascript
// Check if merge was successful
const mergeResult = $input.item.json;

if (mergeResult.exitCode === 0) {
  // Merge successful, delete chunks
  const filePaths = $('Create File List for FFmpeg').item.json.filePaths || [];
  const listFile = $('Create File List for FFmpeg').item.json.listFile;
  
  // Return command to delete files
  return {
    json: {
      ...mergeResult,
      deleteCommand: `rm -f ${filePaths.join(' ')} "${listFile}"`,
      filesToDelete: [...filePaths, listFile]
    }
  };
} else {
  // Merge failed, keep chunks for debugging
  return {
    json: {
      ...mergeResult,
      deleteCommand: '',
      filesToDelete: []
    }
  };
}
```

Sau đó thêm "Execute Command" để chạy `deleteCommand`.

## Giải pháp Khuyến nghị: Xóa trong command merge

### Command hoàn chỉnh (Copy-paste):

```bash
cd /home/node/output && \
echo -e "{{ $json.fileList }}" > "{{ $json.listFile }}" && \
ffmpeg -f concat -safe 0 -i "{{ $json.listFile }}" -c copy "{{ $json.outputFile }}" -y && \
if [ $? -eq 0 ]; then \
  rm -f audio_chunk_*.mp3 audio_list_*.txt && \
  echo "Merged and cleaned: {{ $json.outputFile }}"; \
else \
  echo "Merge failed, keeping chunks for debugging"; \
  exit 1; \
fi
```

## Kiểm tra Files

### Trước khi xóa:
```bash
docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/
```

Sẽ thấy:
- `audio_chunk_0_*.mp3`
- `audio_chunk_1_*.mp3`
- `audio_chunk_2_*.mp3`
- `audio_list_*.txt`
- `merged_audio_*.mp3`

### Sau khi xóa:
```bash
docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/
```

Chỉ còn:
- `merged_audio_*.mp3` ✅

## Lưu ý

### 1. **Giữ lại file merged**
- File `merged_audio_*.mp3` là output cuối cùng, **KHÔNG xóa**
- File này sẽ được dùng cho video composition

### 2. **Xóa có điều kiện**
- Chỉ xóa chunks **sau khi merge thành công**
- Nếu merge thất bại, giữ lại để debug

### 3. **Xóa file list**
- File `audio_list_*.txt` cũng nên xóa (chỉ cần khi merge)

### 4. **Cleanup định kỳ**
- Nếu chạy workflow nhiều lần, có thể tích lũy nhiều file merged
- Có thể thêm cleanup định kỳ (xóa files cũ hơn 7 ngày)

## Cleanup Script (Tùy chọn)

Nếu muốn xóa files cũ hơn 7 ngày:

```bash
# Xóa files cũ hơn 7 ngày
find /home/node/output -name "merged_audio_*.mp3" -mtime +7 -delete && \
find /home/node/output -name "audio_chunk_*.mp3" -mtime +7 -delete && \
find /home/node/output -name "audio_list_*.txt" -mtime +7 -delete && \
echo "Cleaned up old files"
```

## Tóm tắt

| File | Giữ lại? | Khi nào xóa? |
|------|----------|--------------|
| `merged_audio_*.mp3` | ✅ **CÓ** | Không xóa (output cuối cùng) |
| `audio_chunk_*.mp3` | ❌ **KHÔNG** | Sau khi merge thành công |
| `audio_list_*.txt` | ❌ **KHÔNG** | Sau khi merge thành công |

## Command Final (Khuyến nghị)

Sửa command trong node "Execute Command" (FFmpeg Merge):

```bash
cd /home/node/output && echo -e "{{ $json.fileList }}" > "{{ $json.listFile }}" && ffmpeg -f concat -safe 0 -i "{{ $json.listFile }}" -c copy "{{ $json.outputFile }}" -y && rm -f audio_chunk_*.mp3 audio_list_*.txt && echo "Merged: {{ $json.outputFile }}"
```

Command này sẽ:
1. ✅ Tạo file list
2. ✅ Merge audio
3. ✅ Xóa chunks và file list
4. ✅ In thông báo thành công

Bạn muốn thêm xóa file cũ vào command merge không?



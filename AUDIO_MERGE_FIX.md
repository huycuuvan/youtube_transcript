# Hướng dẫn Sửa Lỗi Split/Merge Audio trong Workflow

## Vấn đề

Node "Split Out" không hoạt động với binary data từ node "Text to Speech (OpenAI)" vì:
- Binary data không nằm trong JSON field "data"
- Binary data được lưu riêng trong `$binary.audio` hoặc `$binary.data`
- Node "Split Out" chỉ hoạt động với JSON data, không phải binary

## Giải pháp đã áp dụng

### Flow mới:

```
Text to Speech (OpenAI)
    ↓ (trả về binary data trong $binary.audio)
Save Audio Chunk to File
    ↓ (lưu từng chunk vào file, pass through JSON)
Create File List for FFmpeg
    ↓ (tạo file list từ tất cả chunks)
Merge Audio with FFmpeg
    ↓ (merge bằng FFmpeg)
Prepare Video Data
```

### Các thay đổi:

1. **Xóa node "Split Out"** - không cần thiết
2. **Thêm node "Save Audio Chunk to File"**:
   - Type: `Write Binary File`
   - File Name: `audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3`
   - File Path: `/home/node/output`
   - Options: `keepBinaryData: true` (để pass through JSON data)

3. **Sửa node "Create File List for FFmpeg"**:
   - Lấy `fileName` từ output của node "Save Audio Chunk to File"
   - Tạo file list cho FFmpeg concat demuxer

4. **Cập nhật connections**:
   - Text to Speech → Save Audio Chunk to File
   - Save Audio Chunk to File → Create File List for FFmpeg
   - Create File List for FFmpeg → Merge Audio with FFmpeg
   - Merge Audio with FFmpeg → Prepare Video Data

## Cách sử dụng

1. **Import workflow mới** vào n8n
2. **Kiểm tra thư mục output**:
   ```bash
   docker exec -it n8n-data-n8n-1 ls -la /home/node/output
   ```
3. **Chạy workflow** và kiểm tra:
   - Các file audio chunk được lưu: `audio_chunk_0_*.mp3`, `audio_chunk_1_*.mp3`, ...
   - File list được tạo: `audio_list_*.txt`
   - File merged: `merged_audio_*.mp3`

## Troubleshooting

### Lỗi: "The field 'data' wasn't found"
- **Nguyên nhân**: Đang dùng node "Split Out" với binary data
- **Giải pháp**: Xóa node "Split Out", dùng flow mới như trên

### Lỗi: "File not found" khi merge
- **Nguyên nhân**: File chưa được lưu hoặc path sai
- **Giải pháp**: 
  - Kiểm tra node "Save Audio Chunk to File" có chạy thành công không
  - Kiểm tra quyền ghi vào `/home/node/output`
  - Kiểm tra file list có đúng path không

### Lỗi: "No audio data found"
- **Nguyên nhân**: Binary data không được pass through đúng
- **Giải pháp**:
  - Kiểm tra node "Text to Speech (OpenAI)" có trả về binary data không
  - Kiểm tra `outputPropertyName: "audio"` trong node TTS
  - Đảm bảo `keepBinaryData: true` trong node "Save Audio Chunk to File"

### Audio bị lỗi thứ tự
- **Nguyên nhân**: Chunks không được sort đúng
- **Giải pháp**: Node "Create File List for FFmpeg" đã có sort theo `chunkIndex`

## Kiểm tra kết quả

Sau khi workflow chạy xong, kiểm tra:

```bash
# Xem các file đã tạo
docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/

# Xem nội dung file list
docker exec -it n8n-data-n8n-1 cat /home/node/output/audio_list_*.txt

# Test play merged audio (nếu có ffplay)
docker exec -it n8n-data-n8n-1 ffplay /home/node/output/merged_audio_*.mp3
```

## Lưu ý

- Đảm bảo thư mục `/home/node/output` có quyền ghi
- FFmpeg concat demuxer yêu cầu tất cả files cùng format (MP3 từ OpenAI TTS đều là MP3)
- File list format phải đúng: `file 'path/to/file'\n`
- Path trong file list phải escape single quotes nếu có



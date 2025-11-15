# Các Bước Tiếp Theo: Merge Audio Chunks

## Bước 1: Cấu hình Node "Read/Write Files from Disk" (Đang làm)

### Cấu hình hiện tại:
- ✅ **Operation**: "Write File to Disk"
- ✅ **File Path and Name**: `/home/node/output`
- ✅ **Input Binary Field**: `data`

### Cần sửa:
1. **File Path and Name** cần có tên file động:
   - Click vào icon `fx` bên cạnh field "File Path and Name"
   - Nhập: `/home/node/output/audio_chunk_{{ $json.chunkIndex }}_{{ Date.now() }}.mp3`
   - Hoặc dùng expression: `={{ '/home/node/output/audio_chunk_' + $json.chunkIndex + '_' + Date.now() + '.mp3' }}`

2. **Kiểm tra Input Binary Field**:
   - Từ hình ảnh, input có field `data` → Đúng rồi!
   - Nếu không có `data`, thử `audio`

3. **Test node**:
   - Click "Execute step" để test
   - Kiểm tra xem file có được tạo trong `/home/node/output` không

## Bước 2: Thêm Node "Code" để Tạo File List

Sau node "Read/Write Files from Disk", cần thêm node "Code" để:
- Collect tất cả các file đã lưu
- Tạo file list cho FFmpeg

### Cách thêm:
1. Quay lại canvas
2. Click node "Read/Write Files from Disk"
3. Click dấu "+" ở output
4. Gõ "Code" và chọn

### Code cho node này:
```javascript
// Prepare file list and paths for FFmpeg merge
// This node collects all audio chunks and prepares data for FFmpeg
const items = $input.all();

// Sort by chunkIndex to ensure correct order
items.sort((a, b) => (a.json.chunkIndex || 0) - (b.json.chunkIndex || 0));

// Get base data from first item
const firstItem = items[0].json;
const outputDir = '/home/node/output';
const timestamp = Date.now();

// Create file list for FFmpeg concat demuxer
// Format: file 'path/to/file1'
//         file 'path/to/file2'
let fileList = '';
const filePaths = [];

items.forEach((item, index) => {
  // Get the saved file name from Read/Write Files node output
  // The node returns fileName in json.fileName
  const savedFileName = item.json.fileName || `audio_chunk_${item.json.chunkIndex}_${timestamp}.mp3`;
  const filePath = `${outputDir}/${savedFileName}`;
  filePaths.push(filePath);
  // FFmpeg concat format - escape single quotes in path
  const escapedPath = filePath.replace(/'/g, "'\\''");
  fileList += `file '${escapedPath}'\n`;
});

const listFilePath = `${outputDir}/audio_list_${timestamp}.txt`;
const outputFilePath = `${outputDir}/merged_audio_${timestamp}.mp3`;

return {
  json: {
    videoId: firstItem.videoId,
    title: firstItem.title,
    translatedText: firstItem.translatedText,
    fileList: fileList,
    listFile: listFilePath,
    outputFile: outputFilePath,
    filePaths: filePaths,
    totalChunks: items.length,
    timestamp: new Date().toISOString()
  }
};
```

## Bước 3: Thêm Node "Execute Command" để Merge bằng FFmpeg

Sau node "Code", thêm node "Execute Command":

### Cách thêm:
1. Click node "Code" vừa tạo
2. Click dấu "+" ở output
3. Gõ "Execute Command" và chọn

### Command:
```bash
cd /home/node/output && echo -e "{{ $json.fileList }}" > "{{ $json.listFile }}" && ffmpeg -f concat -safe 0 -i "{{ $json.listFile }}" -c copy "{{ $json.outputFile }}" -y && echo "Merged audio saved to: {{ $json.outputFile }}"
```

## Bước 4: Kiểm tra Kết quả

Sau khi workflow chạy xong, kiểm tra:

```bash
# SSH vào server
ssh user@your-server

# Vào container n8n
docker exec -it n8n-data-n8n-1 sh

# Kiểm tra các file đã tạo
ls -lh /home/node/output/

# Xem nội dung file list
cat /home/node/output/audio_list_*.txt

# Kiểm tra file merged
ls -lh /home/node/output/merged_audio_*.mp3
```

## Checklist Hoàn chỉnh

- [ ] Node "Read/Write Files from Disk" đã cấu hình đúng File Path với tên động
- [ ] Node "Read/Write Files from Disk" đã test thành công (3 files được tạo)
- [ ] Node "Code" đã được thêm và cấu hình
- [ ] Node "Code" đã test thành công (có output với fileList, listFile, outputFile)
- [ ] Node "Execute Command" đã được thêm và cấu hình
- [ ] Node "Execute Command" đã test thành công (file merged được tạo)
- [ ] Kết nối các nodes đúng thứ tự

## Flow Hoàn chỉnh

```
Text to Speech (OpenAI)
    ↓ (3 items, mỗi item có binary.data)
Read/Write Files from Disk
    ↓ (Lưu 3 files: audio_chunk_0_*.mp3, audio_chunk_1_*.mp3, audio_chunk_2_*.mp3)
Code (Create File List)
    ↓ (Tạo file list cho FFmpeg)
Execute Command (FFmpeg Merge)
    ↓ (Merge thành merged_audio_*.mp3)
Prepare Video Data
    ↓ (Chuẩn bị data cho video composition)
```

## Troubleshooting

### Lỗi: File không được tạo
- **Kiểm tra**: Quyền ghi vào `/home/node/output`
- **Giải pháp**: 
  ```bash
  docker exec -it n8n-data-n8n-1 chmod 777 /home/node/output
  ```

### Lỗi: "File not found" khi merge
- **Kiểm tra**: File list có đúng path không
- **Giải pháp**: Xem nội dung file list: `cat /home/node/output/audio_list_*.txt`

### Lỗi: "No such file or directory"
- **Kiểm tra**: File Path trong node "Read/Write Files" có đúng không
- **Giải pháp**: Đảm bảo dùng expression `fx` để tạo tên file động

### Audio bị lỗi thứ tự
- **Kiểm tra**: Code node có sort theo `chunkIndex` không
- **Giải pháp**: Đảm bảo code có dòng `items.sort((a, b) => (a.json.chunkIndex || 0) - (b.json.chunkIndex || 0));`

## Lưu ý Quan trọng

1. **File Name phải động**: Mỗi chunk cần tên file khác nhau để tránh overwrite
2. **ChunkIndex phải có**: Đảm bảo node "Chunk Text for TTS" pass through `chunkIndex`
3. **FFmpeg format**: File list phải đúng format: `file 'path'\n`
4. **Path escaping**: Escape single quotes trong path nếu có

## Next Steps Sau Khi Merge Audio

Sau khi merge audio thành công:
1. ✅ Audio merged: `merged_audio_*.mp3`
2. ⬜ Kết nối với node "Prepare Video Data"
3. ⬜ Compose video với NCA Toolkit
4. ⬜ Save video metadata

Bạn đang ở bước nào? Cần tôi giải thích thêm phần nào không?



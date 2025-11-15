# Bước Tiếp Theo: Merge Audio Chunks

## ✅ Trạng thái hiện tại

Node "Execute Command" đã chạy thành công:
- ✅ File đã được lưu: `audio_chunk_0_1762741269465.mp3`
- ✅ exitCode: 0 (thành công)
- ✅ Không có lỗi

## Bước tiếp theo: Merge các audio chunks

Bạn có **3 audio chunks** cần merge thành 1 file. Cần:

1. **Collect tất cả chunks** (đảm bảo có đủ 3 files)
2. **Tạo file list** cho FFmpeg
3. **Merge bằng FFmpeg**

## Các bước thực hiện

### Bước 1: Thêm node "Code" để tạo file list

Sau node "Execute Command" (Merge Audio with FFmpeg1), thêm node "Code":

1. Click node "Execute Command"
2. Click dấu "+" ở output
3. Gõ "Code" và chọn

#### Code:
```javascript
// Collect all audio chunks and create file list for FFmpeg
const items = $input.all();

// Sort by chunkIndex to ensure correct order
items.sort((a, b) => {
  const idxA = a.json.chunkIndex || 0;
  const idxB = b.json.chunkIndex || 0;
  return idxA - idxB;
});

// Get base data from first item
const firstItem = items[0].json;
const outputDir = '/home/node/output';
const timestamp = Date.now();

// Extract file names from stdout
// stdout format: "Saved: audio_chunk_0_1762741269465.mp3"
const fileNames = items.map(item => {
  const stdout = item.json.stdout || '';
  // Extract filename from "Saved: audio_chunk_X_timestamp.mp3"
  const match = stdout.match(/Saved: (audio_chunk_\d+_\d+\.mp3)/);
  if (match) {
    return match[1];
  }
  // Fallback: construct filename from chunkIndex
  return `audio_chunk_${item.json.chunkIndex || 0}_${timestamp}.mp3`;
});

// Create file list for FFmpeg concat demuxer
// Format: file 'path/to/file1'
//         file 'path/to/file2'
let fileList = '';
const filePaths = [];

fileNames.forEach((fileName) => {
  const filePath = `${outputDir}/${fileName}`;
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
    fileNames: fileNames,
    totalChunks: items.length,
    timestamp: new Date().toISOString()
  }
};
```

### Bước 2: Thêm node "Execute Command" để merge bằng FFmpeg

Sau node "Code", thêm node "Execute Command":

1. Click node "Code"
2. Click dấu "+" ở output
3. Gõ "Execute Command" và chọn

#### Command:
```bash
cd /home/node/output && echo -e "{{ $json.fileList }}" > "{{ $json.listFile }}" && ffmpeg -f concat -safe 0 -i "{{ $json.listFile }}" -c copy "{{ $json.outputFile }}" -y && echo "Merged audio saved to: {{ $json.outputFile }}"
```

### Bước 3: Test và kiểm tra

1. Click "Execute step" trên node "Code" → Kiểm tra có `fileList`, `listFile`, `outputFile`
2. Click "Execute step" trên node "Execute Command" (FFmpeg) → Kiểm tra file merged

## Flow hoàn chỉnh

```
Text to Speech (OpenAI)
    ↓ (3 items)
Execute Command (Save Audio Chunk)
    ↓ (3 files: audio_chunk_0_*.mp3, audio_chunk_1_*.mp3, audio_chunk_2_*.mp3)
Code (Create File List)
    ↓ (fileList, listFile, outputFile)
Execute Command (FFmpeg Merge)
    ↓ (merged_audio_*.mp3)
Prepare Video Data
```

## Kiểm tra kết quả

Sau khi merge, kiểm tra:

```bash
# Vào container
docker exec -it n8n-data-n8n-1 sh

# Kiểm tra files
ls -lh /home/node/output/

# Xem file list
cat /home/node/output/audio_list_*.txt

# Kiểm tra file merged
ls -lh /home/node/output/merged_audio_*.mp3
```

## Troubleshooting

### Lỗi: "No such file or directory" khi merge
- **Kiểm tra**: Files có được tạo đúng không
- **Giải pháp**: 
  ```bash
  docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/audio_chunk_*.mp3
  ```

### Lỗi: "Invalid data found when processing input"
- **Nguyên nhân**: File list format sai
- **Giải pháp**: Kiểm tra file list:
  ```bash
  cat /home/node/output/audio_list_*.txt
  ```
  Phải có format:
  ```
  file '/home/node/output/audio_chunk_0_xxx.mp3'
  file '/home/node/output/audio_chunk_1_xxx.mp3'
  ```

### Audio bị lỗi thứ tự
- **Nguyên nhân**: Chunks không được sort đúng
- **Giải pháp**: Đảm bảo code có sort theo `chunkIndex`

## Lưu ý

1. **Đảm bảo có đủ 3 chunks**: Node "Code" cần collect tất cả items từ node "Execute Command"
2. **File list format**: Phải đúng format FFmpeg concat demuxer
3. **Path escaping**: Escape single quotes trong path nếu có
4. **FFmpeg flags**: `-safe 0` cho phép absolute paths, `-c copy` để copy nhanh không re-encode

## Next Steps

Sau khi merge audio thành công:
1. ✅ Audio merged: `merged_audio_*.mp3`
2. ⬜ Kết nối với node "Prepare Video Data"
3. ⬜ Compose video với NCA Toolkit
4. ⬜ Save video metadata

Bạn đã thêm node "Code" để tạo file list chưa?



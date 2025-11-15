# Hướng dẫn Merge 3 File MP3 trong n8n

## Cách 1: Dùng Execute Command với FFmpeg (Đơn giản nhất)

### Bước 1: Thêm node "Merge Audio with FFmpeg"

1. Thêm một **Execute Command** node sau node "Text to Speech (OpenAI)"
2. Đặt tên: **"Merge Audio with FFmpeg"**

### Bước 2: Cấu hình node

**Command:**
```bash
cd /home/node/output && ffmpeg -i "concat:{{ $('Text to Speech (OpenAI)').item.json.file1 }}|{{ $('Text to Speech (OpenAI)').item.json.file2 }}|{{ $('Text to Speech (OpenAI)').item.json.file3 }}" -c copy merged_audio_$(date +%s).mp3
```

**Hoặc cách tốt hơn - dùng file list:**

1. Thêm một **Code** node trước "Merge Audio with FFmpeg" để tạo file list:

```javascript
// Create file list for FFmpeg concat
const items = $input.all();
items.sort((a, b) => (a.json.chunkIndex || 0) - (b.json.chunkIndex || 0));

const timestamp = Date.now();
const outputDir = '/home/node/output';
let fileList = '';

items.forEach((item, index) => {
  // Assume audio files are saved with names like audio_chunk_0.mp3, audio_chunk_1.mp3, etc.
  const fileName = `audio_chunk_${index}.mp3`;
  const filePath = `${outputDir}/${fileName}`;
  fileList += `file '${filePath}'\n`;
});

const listFile = `${outputDir}/audio_list_${timestamp}.txt`;
const outputFile = `${outputDir}/merged_audio_${timestamp}.mp3`;

return {
  json: {
    listFile: listFile,
    outputFile: outputFile,
    fileList: fileList,
    totalChunks: items.length
  }
};
```

2. Trong node "Merge Audio with FFmpeg", dùng command:

```bash
cd /home/node/output && echo -e "{{ $json.fileList }}" > "{{ $json.listFile }}" && ffmpeg -f concat -safe 0 -i "{{ $json.listFile }}" -c copy "{{ $json.outputFile }}" -y
```

## Cách 2: Dùng NCA Toolkit (Nếu có endpoint merge audio)

Nếu NCA Toolkit có endpoint merge audio, dùng HTTP Request node:

**URL:** `http://nca:8080/v1/audio/merge` (hoặc endpoint tương ứng)

**Method:** `POST`

**Body:**
```json
{
  "audio_files": [
    "{{ $json.audioFile1 }}",
    "{{ $json.audioFile2 }}",
    "{{ $json.audioFile3 }}"
  ],
  "output_format": "mp3"
}
```

## Cách 3: Merge Binary Data Trực tiếp (Nếu format giống nhau)

Dùng Code node để concatenate binary data:

```javascript
const items = $input.all();
items.sort((a, b) => (a.json.chunkIndex || 0) - (b.json.chunkIndex || 0));

// Get all audio binary data
const audioBuffers = items.map(item => {
  const audioData = item.binary?.audio || item.binary?.data;
  if (audioData && audioData.data) {
    return Buffer.from(audioData.data);
  }
  return null;
}).filter(Buffer => Buffer !== null);

// Concatenate all buffers
const mergedBuffer = Buffer.concat(audioBuffers);

return {
  json: {
    videoId: items[0].json.videoId,
    title: items[0].json.title,
    translatedText: items[0].json.translatedText,
    audioSize: mergedBuffer.length,
    timestamp: new Date().toISOString()
  },
  binary: {
    audio: {
      data: mergedBuffer,
      mimeType: 'audio/mpeg',
      fileName: 'merged_audio.mp3'
    }
  }
};
```

## Khuyến nghị

**Dùng Cách 1 (FFmpeg)** vì:
- Đơn giản, không cần thêm service
- FFmpeg đã có sẵn trong n8n container
- Đảm bảo chất lượng audio tốt
- Hỗ trợ nhiều format

## Lưu ý

- Đảm bảo các audio chunks đã được lưu vào `/home/node/output` trước khi merge
- Kiểm tra quyền ghi vào thư mục `/home/node/output`
- File merged sẽ được lưu tại `/home/node/output/merged_audio_[timestamp].mp3`


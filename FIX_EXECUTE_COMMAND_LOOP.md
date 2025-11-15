# Fix: Execute Command chỉ xử lý 1 item thay vì 3

## Vấn đề

Node "Execute Command" chỉ lưu được **1 file** trong khi có **3 items** từ node "Text to Speech (OpenAI)".

Nguyên nhân: Node "Execute Command" có option **"Execute Once"** đang bật, khiến nó chỉ xử lý item đầu tiên.

## Giải pháp: Tắt "Execute Once"

### Cách 1: Tắt "Execute Once" trong node hiện tại

1. Click vào node **"Execute Command"** (Merge Audio with FFmpeg1)
2. Tìm toggle **"Execute Once"** (thường ở trên cùng hoặc trong Settings)
3. **Tắt** toggle này (chuyển từ ON → OFF)
4. Click **"Execute step"** lại
5. Sẽ thấy **3 items** trong output, mỗi item là một file đã được lưu

### Cách 2: Thêm node "Loop Over Items" trước Execute Command

Nếu không có option "Execute Once", thêm node "Loop Over Items":

1. **Xóa connection** giữa "Text to Speech" và "Execute Command"
2. **Thêm node "Loop Over Items"**:
   - Click node "Text to Speech"
   - Click dấu "+"
   - Gõ "Loop Over Items" và chọn
3. **Kết nối**:
   - Text to Speech → Loop Over Items → Execute Command

### Cách 3: Kiểm tra Settings của node

1. Click node "Execute Command"
2. Click tab **"Settings"**
3. Tìm option **"Execute Once"** hoặc **"Continue on Fail"**
4. Đảm bảo **"Execute Once"** = OFF

## Kiểm tra

Sau khi tắt "Execute Once":

1. Click **"Execute step"** trên node "Execute Command"
2. Xem **OUTPUT**:
   - Sẽ có **3 items** (thay vì 1)
   - Mỗi item có stdout: "Saved: audio_chunk_X_xxx.mp3"
3. Kiểm tra files:
   ```bash
   docker exec -it n8n-data-n8n-1 ls -lh /home/node/output/audio_chunk_*.mp3
   ```
   Sẽ thấy 3 files:
   - `audio_chunk_0_xxx.mp3`
   - `audio_chunk_1_xxx.mp3`
   - `audio_chunk_2_xxx.mp3`

## Hướng dẫn chi tiết: Tắt "Execute Once"

### Bước 1: Mở node configuration
- Click node "Execute Command" (Merge Audio with FFmpeg1)

### Bước 2: Tìm toggle "Execute Once"
- Ở trên cùng của node, có toggle **"Execute Once"**
- Hiện tại đang **ON** (màu xanh/green)
- Click để **tắt** (chuyển sang OFF/grey)

### Bước 3: Execute lại
- Click **"Execute step"**
- Kiểm tra output → Sẽ có 3 items

## Alternative: Dùng "Split Out" Node

Nếu "Execute Once" không có, dùng node "Split Out":

1. **Thêm node "Split Out"** sau "Text to Speech":
   - Click node "Text to Speech"
   - Click dấu "+"
   - Gõ "Split Out" và chọn

2. **Cấu hình**:
   - **Fields To Split Out**: Để trống (sẽ split tất cả items)
   - **Options**: Bật "Include Binary"

3. **Kết nối**:
   - Text to Speech → Split Out → Execute Command

## Troubleshooting

### Vẫn chỉ có 1 item sau khi tắt "Execute Once"
- **Kiểm tra**: Input có đủ 3 items không
- **Giải pháp**: Click node "Text to Speech" → Xem OUTPUT → Có 3 items không?

### Lỗi: "Execute Once" không có trong Settings
- **Giải pháp**: Dùng node "Loop Over Items" hoặc "Split Out"

### Files không được tạo đủ
- **Kiểm tra**: Command có chạy thành công cho tất cả items không
- **Giải pháp**: Xem stderr trong output của từng item

## Quick Fix (Copy-paste)

Nếu không tìm thấy toggle "Execute Once":

1. **Thêm node "Loop Over Items"**:
   - Text to Speech → Loop Over Items → Execute Command

2. **Hoặc thêm node "Split Out"**:
   - Text to Speech → Split Out → Execute Command

## Lưu ý

- **"Execute Once" = ON**: Node chỉ chạy 1 lần với item đầu tiên
- **"Execute Once" = OFF**: Node sẽ loop qua tất cả items
- **"Loop Over Items"**: Node chuyên dụng để loop, đảm bảo xử lý tất cả items

## Sau khi fix

Sau khi tắt "Execute Once" hoặc thêm "Loop Over Items":

1. ✅ Node sẽ xử lý cả 3 items
2. ✅ 3 files sẽ được tạo: `audio_chunk_0_*.mp3`, `audio_chunk_1_*.mp3`, `audio_chunk_2_*.mp3`
3. ⬜ Tiếp tục với node "Code" để tạo file list và merge

Bạn có thấy toggle "Execute Once" trong node "Execute Command" không? Nếu có, hãy tắt nó đi!



# Fix Lỗi: "The file or directory does not exist"

## Vấn đề
Node "Read/Write Files from Disk" báo lỗi: **"The file or directory does not exist"**

Nguyên nhân: Thư mục `/home/node/output` chưa tồn tại hoặc ch8n không có quyền ghi.

## Giải pháp

### Bước 1: Tạo thư mục trong container n8n

SSH vào server và chạy:

```bash
# Vào container n8n
docker exec -it n8n-data-n8n-1 sh

# Tạo thư mục output
mkdir -p /home/node/output

# Đảm bảo quyền ghi
chmod 777 /home/node/output

# Kiểm tra
ls -la /home/node/output
```

### Bước 2: Kiểm tra Docker Volume Mount

Đảm bảo trong `docker-compose.yml` có mount volume:

```yaml
services:
  n8n:
    volumes:
      - ./n8n-data:/home/node/.n8n
      - ./scripts:/home/node/scripts
      - ./outputs:/home/node/output  # ← Đảm bảo có dòng này
```

Nếu chưa có, thêm vào và restart:

```bash
# Sửa docker-compose.yml
nano docker-compose.yml

# Thêm volume mount cho outputs
# Tìm section volumes của n8n service, thêm:
# - ./outputs:/home/node/output

# Tạo thư mục trên host
mkdir -p ./outputs

# Restart container
docker-compose restart n8n
```

### Bước 3: Tạo thư mục trên Host (nếu dùng volume mount)

```bash
# Tạo thư mục
mkdir -p ./outputs

# Đảm bảo quyền
chmod 777 ./outputs
```

### Bước 4: Test lại

1. Quay lại n8n
2. Click "Execute step" trên node "Read/Write Files from Disk"
3. Kiểm tra xem còn lỗi không

## Kiểm tra nhanh

Chạy lệnh này để kiểm tra:

```bash
# Kiểm tra thư mục có tồn tại không
docker exec -it n8n-data-n8n-1 test -d /home/node/output && echo "OK" || echo "NOT EXISTS"

# Kiểm tra quyền ghi
docker exec -it n8n-data-n8n-1 test -w /home/node/output && echo "WRITABLE" || echo "NOT WRITABLE"

# Tạo thư mục nếu chưa có
docker exec -it n8n-data-n8n-1 mkdir -p /home/node/output && chmod 777 /home/node/output && echo "CREATED"
```

## Giải pháp nhanh nhất (Copy-paste)

```bash
# Tạo thư mục và set quyền
docker exec -it n8n-data-n8n-1 sh -c "mkdir -p /home/node/output && chmod 777 /home/node/output && ls -la /home/node/output"
```

## Lưu ý

1. **Không cần clear gì cả** - chỉ cần tạo thư mục
2. **Quyền 777** cho phép n8n ghi file (trong môi trường dev/test)
3. **Volume mount** giúp bạn truy cập files từ host machine
4. **Persistent storage**: Nếu dùng volume mount, files sẽ tồn tại sau khi restart container

## Sau khi fix

Sau khi tạo thư mục, test lại node:
1. Click "Execute step" trên node "Read/Write Files from Disk"
2. Nếu thành công, bạn sẽ thấy 3 files được tạo:
   - `audio_chunk_0_*.mp3`
   - `audio_chunk_1_*.mp3`
   - `audio_chunk_2_*.mp3`

## Troubleshooting

### Vẫn báo lỗi sau khi tạo thư mục
- Kiểm tra user của n8n: `docker exec -it n8n-data-n8n-1 whoami`
- Nếu là `node`, đảm bảo thư mục thuộc về user `node`:
  ```bash
  docker exec -it n8n-data-n8n-1 chown -R node:node /home/node/output
  ```

### Files không xuất hiện trên host
- Kiểm tra volume mount trong docker-compose.yml
- Kiểm tra thư mục `./outputs` trên host có tồn tại không

### Permission denied
- Thử với quyền cao hơn:
  ```bash
  docker exec -it --user root n8n-data-n8n-1 mkdir -p /home/node/output && chmod 777 /home/node/output
  ```



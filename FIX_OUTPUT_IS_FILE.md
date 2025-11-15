# Fix: /home/node/output là File, không phải Directory

## Vấn đề

Từ output của `ls -la`:
```
-rwxrwxrwx    1 node     node       3655680 Nov 10 02:03 /home/node/output
```

Dấu `-` ở đầu cho thấy `/home/node/output` là **file**, không phải **directory**.

## Giải pháp

### Bước 1: Xóa file cũ

Trong container n8n, chạy:

```bash
# Vào container (nếu chưa vào)
docker exec -it n8n-data-n8n-1 sh

# Xóa file
rm /home/node/output

# Kiểm tra đã xóa chưa
ls -la /home/node/output
# Sẽ báo: No such file or directory
```

### Bước 2: Tạo lại thành directory

```bash
# Tạo directory
mkdir -p /home/node/output

# Set quyền
chmod 777 /home/node/output

# Kiểm tra
ls -la /home/node/
# Sẽ thấy:
# drwxrwxrwx    1 node     node        ... /home/node/output
# (dấu 'd' ở đầu = directory)
```

### Bước 3: Verify

```bash
# Kiểm tra là directory
test -d /home/node/output && echo "OK: Is directory" || echo "ERROR: Not directory"

# Kiểm tra quyền ghi
test -w /home/node/output && echo "OK: Writable" || echo "ERROR: Not writable"
```

## Command đầy đủ (Copy-paste)

```bash
docker exec -it n8n-data-n8n-1 sh -c "rm -f /home/node/output && mkdir -p /home/node/output && chmod 777 /home/node/output && ls -ld /home/node/output"
```

## Sau khi fix

1. Quay lại n8n
2. Click "Execute step" lại trên node "Execute Command"
3. Lỗi sẽ hết và file sẽ được tạo

## Kiểm tra kết quả

Sau khi chạy command, kiểm tra:

```bash
docker exec -it n8n-data-n8n-1 ls -ld /home/node/output
```

Output mong đợi:
```
drwxrwxrwx    1 node     node        ... /home/node/output
```

**Lưu ý**: Dấu `d` ở đầu = directory ✅

## Lưu ý

- File `/home/node/output` có thể được tạo do lỗi trước đó
- Sau khi xóa và tạo lại thành directory, workflow sẽ hoạt động bình thường
- Đảm bảo quyền 777 để n8n có thể ghi file



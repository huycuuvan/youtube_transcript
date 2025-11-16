# ⚙️ FIX: Git Identity Configuration

## ❌ VẤN ĐỀ

Git báo lỗi: `Committer identity unknown` và `fatal: unable to auto-detect email address`

**Nguyên nhân:** Git chưa được cấu hình user email và name trên server.

---

## 🔧 GIẢI PHÁP

### Cấu hình Git Identity

```bash
# Cấu hình cho repository này (không ảnh hưởng global)
git config user.email "huycuuvan@example.com"
git config user.name "huycuuvan"

# Hoặc cấu hình global (cho tất cả repositories)
git config --global user.email "huycuuvan@example.com"
git config --global user.name "huycuuvan"
```

### Sau đó pull lại

```bash
git pull origin main
```

---

## 🚀 QUICK FIX (Copy-paste)

```bash
# Cấu hình Git identity
git config --global user.email "huycuuvan@github.com"
git config --global user.name "huycuuvan"

# Pull từ main
git pull origin main
```

---

## 📋 KIỂM TRA CẤU HÌNH

```bash
# Xem cấu hình hiện tại
git config user.email
git config user.name

# Xem tất cả cấu hình
git config --list
```

---

## ⚠️ LƯU Ý

1. **Email không cần phải là email thật** - chỉ cần format hợp lệ
2. **Có thể dùng GitHub email** hoặc bất kỳ email nào
3. **Global config** sẽ áp dụng cho tất cả repositories
4. **Local config** chỉ áp dụng cho repository hiện tại

---

## 🎯 KHUYẾN NGHỊ

**Trên server, dùng:**

```bash
git config --global user.email "huycuuvan@github.com"
git config --global user.name "huycuuvan"
```

Sau đó pull lại sẽ thành công!



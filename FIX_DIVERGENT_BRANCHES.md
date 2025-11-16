# 🔀 FIX: Divergent Branches - Reconcile Branches

## ❌ VẤN ĐỀ

Git báo lỗi: `fatal: Need to specify how to reconcile divergent branches`

**Nguyên nhân:** Branch `main` và `develop` đã phân nhánh (có commits khác nhau).

---

## 🔧 GIẢI PHÁP

### Cách 1: Merge (Khuyến nghị - Giữ nguyên lịch sử)

```bash
# Cấu hình merge strategy
git config pull.rebase false

# Pull từ main với merge
git pull origin main --no-rebase

# Hoặc merge trực tiếp
git merge origin/main
```

### Cách 2: Rebase (Lịch sử sạch hơn)

```bash
# Cấu hình rebase strategy
git config pull.rebase true

# Pull từ main với rebase
git pull origin main --rebase

# Hoặc rebase trực tiếp
git rebase origin/main
```

### Cách 3: Fast-forward only (An toàn nhất)

```bash
# Chỉ pull nếu có thể fast-forward
git config pull.ff only

# Pull từ main
git pull origin main
```

---

## 🚀 QUICK FIX (Trên server)

### Nếu bạn đang ở branch `develop` và muốn pull từ `main`:

```bash
# Option 1: Merge (giữ cả 2 histories)
git config pull.rebase false
git pull origin main

# Option 2: Rebase (linear history)
git config pull.rebase true
git pull origin main

# Option 3: Chỉ xem code từ main (không merge)
git fetch origin main
git checkout main
# Xem code, sau đó quay lại develop
git checkout develop
```

---

## 📋 TÌNH HUỐNG CỤ THỂ

### Tình huống 1: Muốn merge code từ main vào develop

```bash
# Đảm bảo đang ở develop
git checkout develop

# Merge main vào develop
git config pull.rebase false
git pull origin main

# Nếu có conflict, giải quyết và commit
# git add .
# git commit -m "Merge main into develop"
```

### Tình huống 2: Muốn rebase develop lên main (linear history)

```bash
# Đảm bảo đang ở develop
git checkout develop

# Rebase lên main
git config pull.rebase true
git pull origin main

# Nếu có conflict, giải quyết và continue
# git add .
# git rebase --continue
```

### Tình huống 3: Chỉ cần code mới từ main (không merge)

```bash
# Fetch code mới
git fetch origin main

# Xem code từ main
git checkout -b main-temp origin/main

# Hoặc merge vào develop sau
git checkout develop
git merge origin/main
```

---

## ⚠️ LƯU Ý

1. **Merge vs Rebase:**
   - **Merge:** Giữ nguyên lịch sử, tạo merge commit
   - **Rebase:** Lịch sử linear, rewrite commits
   - **Fast-forward:** Chỉ pull nếu không có conflict

2. **Nếu có conflict:**
   ```bash
   # Giải quyết conflict trong files
   # Sau đó:
   git add .
   git commit -m "Resolve merge conflicts"
   # Hoặc nếu rebase:
   git rebase --continue
   ```

3. **Nếu muốn hủy:**
   ```bash
   # Hủy merge
   git merge --abort
   
   # Hủy rebase
   git rebase --abort
   ```

---

## 🎯 KHUYẾN NGHỊ

**Cho server (pull code mới):**

```bash
# Dùng merge để an toàn
git config pull.rebase false
git pull origin main
```

**Cho development (clean history):**

```bash
# Dùng rebase để lịch sử sạch
git config pull.rebase true
git pull origin main
```

---

## 📌 TÓM TẮT

**Trên server, chạy:**

```bash
git config pull.rebase false
git pull origin main
```

Sau đó giải quyết conflict (nếu có) và push lại.



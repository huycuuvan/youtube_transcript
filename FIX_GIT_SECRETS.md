# 🔒 HƯỚNG DẪN: Fix lỗi GitHub Push Protection - Secrets

## ❌ VẤN ĐỀ

GitHub đã chặn push vì phát hiện secrets trong code:
- ✅ Google Cloud Service Account Credentials: `lateral-booking-477813-g7-cb6a798f4a1f.json`
- ✅ OpenAI API Key: `n8n_workflow_youtube_to_video.json` (nhiều vị trí)

---

## 🔧 GIẢI PHÁP

### Bước 1: Xóa file secrets khỏi Git history

```powershell
# Xóa file credentials khỏi Git
git rm --cached lateral-booking-477813-g7-cb6a798f4a1f.json

# Xóa n8n workflow file (có API keys)
git rm --cached n8n_workflow_youtube_to_video.json

# Commit việc xóa
git commit -m "Remove secrets from repository"
```

### Bước 2: Tạo file workflow template (không có API keys)

Tạo file `n8n_workflow_youtube_to_video.template.json` với API keys được thay bằng placeholders:

```json
{
  "parameters": {
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization",
          "value": "Bearer {{OPENAI_API_KEY}}"
        }
      ]
    }
  }
}
```

### Bước 3: Commit .gitignore và push

```powershell
# Add .gitignore
git add .gitignore

# Commit
git commit -m "Add .gitignore to exclude secrets"

# Push
git push origin main
```

---

## 📋 CÁC FILE ĐÃ ĐƯỢC THÊM VÀO .GITIGNORE

- ✅ `token.json` - Google OAuth tokens
- ✅ `credentials.json` - Google credentials
- ✅ `lateral-*.json` - Google Cloud credentials
- ✅ `*-booking-*.json` - Google Cloud credentials
- ✅ `n8n_workflow_*.json` - n8n workflows (chứa API keys)
- ✅ `*.env` - Environment files
- ✅ `*credentials*.json` - Tất cả credential files

---

## 🔄 CÁCH XỬ LÝ WORKFLOW FILES

### Option 1: Không commit workflow files (Khuyến nghị)

- Workflow files chỉ dùng local
- Export/import workflow từ n8n UI khi cần

### Option 2: Tạo template workflow (không có secrets)

1. Tạo file `n8n_workflow_youtube_to_video.template.json`
2. Thay tất cả API keys bằng placeholders: `{{OPENAI_API_KEY}}`
3. Commit template file
4. Trên server, thay thế placeholders bằng API keys thật

---

## 🚀 QUICK FIX COMMANDS

```powershell
# 1. Xóa secrets khỏi Git
git rm --cached lateral-booking-477813-g7-cb6a798f4a1f.json
git rm --cached n8n_workflow_youtube_to_video.json

# 2. Commit .gitignore
git add .gitignore
git commit -m "Add .gitignore and remove secrets"

# 3. Push
git push origin main
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

1. **API Keys đã bị lộ:** Nếu đã push lên GitHub, API keys có thể đã bị lộ
   - ✅ **Ngay lập tức:** Revoke và tạo API keys mới
   - ✅ **OpenAI:** https://platform.openai.com/api-keys
   - ✅ **Google Cloud:** Tạo service account mới

2. **Git History:** File vẫn còn trong Git history
   - Nếu cần xóa hoàn toàn: Dùng `git filter-branch` hoặc `git filter-repo`
   - Hoặc tạo repo mới và copy code (không copy secrets)

3. **Local files:** File vẫn còn trên máy local, chỉ bị xóa khỏi Git tracking

---

## 📝 CHECKLIST

- [ ] ✅ Đã thêm secrets vào .gitignore
- [ ] ✅ Đã xóa secrets khỏi Git tracking (`git rm --cached`)
- [ ] ✅ Đã commit .gitignore
- [ ] ✅ Đã revoke API keys cũ (nếu đã lộ)
- [ ] ✅ Đã tạo API keys mới
- [ ] ✅ Đã push thành công

---

## 🔐 BEST PRACTICES

1. **Không bao giờ commit:**
   - API keys
   - Passwords
   - Private keys
   - Credentials files

2. **Dùng environment variables:**
   - Trong n8n: Dùng `{{ $env.OPENAI_API_KEY }}`
   - Trong code: Dùng `os.environ.get('API_KEY')`

3. **Dùng .env files:**
   - Tạo `.env.example` (template)
   - Thêm `.env` vào .gitignore
   - Copy `.env.example` thành `.env` và điền secrets

---

**Sau khi fix xong, push lại sẽ thành công!** ✅



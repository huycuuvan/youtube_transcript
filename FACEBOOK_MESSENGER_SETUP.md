# Hướng dẫn Setup Facebook Messenger Auto Reply với n8n

## Tổng quan

Workflow này tự động trả lời tin nhắn Facebook Messenger:
- **Câu hỏi đơn giản**: Tự động trả lời bằng AI (OpenAI)
- **Câu hỏi phức tạp**: Gửi thông báo cho người phụ trách, gửi tin nhắn xác nhận cho khách hàng

## Các bước Setup

### 1. Tạo Facebook App và Page

1. Truy cập [Facebook Developers](https://developers.facebook.com/)
2. Tạo App mới → Chọn "Business" → "Messenger"
3. Thêm Messenger product vào App
4. Kết nối với Facebook Page của bạn
5. Lấy **Page Access Token**:
   - Vào Messenger → Settings → Access Tokens
   - Copy Page Access Token

### 2. Setup Webhook trong Facebook

1. Vào **Webhooks** trong Facebook App
2. Subscribe to fields: `messages`, `messaging_postbacks`
3. Callback URL: `https://your-n8n-domain.com/webhook/facebook-messenger`
4. Verify Token: Tạo một token bất kỳ (ví dụ: `my_verify_token_123`)
5. Lưu Verify Token để dùng trong n8n

### 3. Cấu hình Environment Variables trong n8n

Thêm các biến môi trường sau vào n8n:

```bash
# Facebook
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_VERIFY_TOKEN=my_verify_token_123

# OpenAI
OPENAI_API_KEY=sk-proj-your-openai-key

# Company Data (có thể lưu trong database thay vì env)
COMPANY_NAME=Công ty của bạn
COMPANY_SERVICES=Dịch vụ A, Dịch vụ B, Dịch vụ C
COMPANY_PRODUCTS=Sản phẩm 1, Sản phẩm 2
COMPANY_ADDRESS=123 Đường ABC, Quận XYZ, TP.HCM
COMPANY_PHONE=0123456789
COMPANY_EMAIL=contact@company.com
COMPANY_WEBSITE=https://company.com
COMPANY_HOURS=Thứ 2 - Thứ 6: 8:00 - 17:00
COMPANY_PRICE_1=Dịch vụ A
COMPANY_PRICE_1_VALUE=1,000,000 VNĐ
COMPANY_PRICE_2=Dịch vụ B
COMPANY_PRICE_2_VALUE=2,000,000 VNĐ

# Notification (Optional - cho Slack/Email)
NOTIFICATION_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 4. Import Workflow vào n8n

1. Mở n8n
2. Click **Workflows** → **Import from File**
3. Chọn file `n8n_workflow_facebook_messenger_auto_reply.json`
4. Workflow sẽ được import với tất cả các nodes

### 5. Cấu hình các Nodes

#### Node: "Facebook Messenger Webhook"
- URL sẽ tự động tạo: `https://your-n8n-domain.com/webhook/facebook-messenger`
- Copy URL này và paste vào Facebook Webhook Callback URL

#### Node: "Parse Facebook Webhook"
- Đã được cấu hình sẵn để parse webhook payload
- Tự động verify webhook khi Facebook gửi GET request

#### Node: "Classify Message Type"
- Tự động phân loại câu hỏi đơn giản vs phức tạp
- Dựa trên keywords và độ dài tin nhắn
- Có thể tùy chỉnh keywords trong code

#### Node: "AI Agent (OpenAI)"
- Sử dụng OpenAI GPT-4o-mini để trả lời
- Có thể thay bằng NCA Toolkit LLM nếu muốn

#### Node: "Send Facebook Reply"
- Gửi tin nhắn trả lời qua Facebook Graph API
- Cần `FACEBOOK_PAGE_ACCESS_TOKEN` trong env

#### Node: "Notify Human (Slack/Email)"
- Gửi thông báo khi có câu hỏi phức tạp
- Có thể cấu hình Slack webhook hoặc Email

### 6. Test Workflow

1. **Test Webhook Verification**:
   - Facebook sẽ gửi GET request để verify
   - Workflow sẽ tự động trả về challenge token

2. **Test với tin nhắn thật**:
   - Gửi tin nhắn đến Facebook Page
   - Kiểm tra workflow execution trong n8n
   - Xem log để debug nếu có lỗi

## Cấu trúc Workflow

```
Facebook Messenger Webhook
    ↓
Parse Facebook Webhook
    ↓
Check Has Message
    ↓
Classify Message Type
    ↓
Check Question Type (IF)
    ├─→ Simple Question
    │   ↓
    │   Prepare AI Prompt
    │   ↓
    │   AI Agent (OpenAI)
    │   ↓
    │   Extract AI Response
    │   ↓
    │   Send Facebook Reply ✅
    │
    └─→ Complex Question
        ↓
        Send Acknowledgment
        ↓
        Notify Human
        ↓
        Log Conversation
```

## Tùy chỉnh

### Thay đổi Keywords cho Simple Questions

Sửa node "Classify Message Type", thêm/bớt keywords trong mảng `simpleKeywords`:

```javascript
const simpleKeywords = [
  'dịch vụ', 'sản phẩm', 'giá', 'địa chỉ',
  // Thêm keywords của bạn ở đây
];
```

### Thay đổi Company Data

Có 3 cách:

1. **Environment Variables** (hiện tại): Dễ setup, khó quản lý nhiều data
2. **Database**: Lưu trong PostgreSQL/MySQL, query trong node
3. **Google Sheets**: Lưu trong Sheets, đọc bằng Google Sheets node

### Thay đổi AI Model

Trong node "AI Agent (OpenAI)", có thể:
- Đổi sang NCA Toolkit: `http://nca:8080/v1/llm/chat/completions`
- Đổi model: `gpt-4o`, `gpt-3.5-turbo`, etc.
- Điều chỉnh `temperature`, `max_tokens`

### Thêm tính năng

- **Lưu lịch sử chat**: Thêm node để lưu vào database
- **Phân tích sentiment**: Thêm node để phân tích cảm xúc khách hàng
- **Auto tag**: Tự động tag khách hàng dựa trên câu hỏi
- **Rich messages**: Gửi buttons, quick replies, images

## Troubleshooting

### Lỗi: Webhook verification failed
- Kiểm tra `FACEBOOK_VERIFY_TOKEN` trong env
- Đảm bảo token khớp với Facebook App settings

### Lỗi: Invalid Page Access Token
- Kiểm tra `FACEBOOK_PAGE_ACCESS_TOKEN` trong env
- Đảm bảo token chưa hết hạn
- Kiểm tra quyền: `pages_messaging`, `pages_manage_messaging`

### Lỗi: Message not sent
- Kiểm tra sender ID có đúng không
- Kiểm tra rate limits của Facebook
- Xem error response từ Facebook Graph API

### Workflow không trigger
- Kiểm tra webhook URL có đúng không
- Kiểm tra n8n có public URL không (HTTPS required)
- Kiểm tra Facebook App có subscribe đúng fields không

## Security

1. **Bảo mật Access Token**: Không commit token vào Git
2. **HTTPS**: Webhook URL phải dùng HTTPS
3. **Verify Token**: Dùng token mạnh, không dễ đoán
4. **Rate Limiting**: Facebook có giới hạn, cần handle gracefully

## Next Steps

1. ✅ Import workflow
2. ✅ Setup Facebook App và Webhook
3. ✅ Cấu hình Environment Variables
4. ✅ Test với tin nhắn thật
5. ⬜ Tùy chỉnh company data
6. ⬜ Thêm tính năng logging/analytics
7. ⬜ Setup monitoring và alerts

## Resources

- [Facebook Messenger Platform Docs](https://developers.facebook.com/docs/messenger-platform)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [n8n Documentation](https://docs.n8n.io)
- [OpenAI API Docs](https://platform.openai.com/docs)


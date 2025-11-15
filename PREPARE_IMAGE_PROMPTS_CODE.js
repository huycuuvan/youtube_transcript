// Code cho node "Prepare Image Prompts" trong n8n
// Mục đích: Tạo nhiều items (mỗi item = 1 prompt) để n8n có thể loop qua

const items = $input.all();

function safeParse(maybeJsonString) {
  if (typeof maybeJsonString !== 'string') return maybeJsonString ?? {};
  const cleaned = maybeJsonString.replace(/```json|```/g, '').trim();
  try { return JSON.parse(cleaned); } catch { return {}; }
}

// Lấy mảng imagePrompts từ input
let imagePromptsArray = [];

// Trường hợp 1: Input đã có mảng imagePrompts (từ node trước)
if (items[0]?.json?.imagePrompts && Array.isArray(items[0].json.imagePrompts)) {
  imagePromptsArray = items[0].json.imagePrompts;
}
// Trường hợp 2: Parse từ OpenAI response
else {
  const parsed = items.map(({ json }) => {
    const raw = json?.choices?.[0]?.message?.content ?? json?.content ?? '';
    const data = safeParse(raw);
    return Array.isArray(data.image_prompts) ? data.image_prompts : [];
  });
  imagePromptsArray = parsed.flatMap(p => p).slice(0, 5);
}

// Đảm bảo có ít nhất 3 prompts
if (imagePromptsArray.length === 0) {
  imagePromptsArray.push('Cinematic scene related to the video topic');
  imagePromptsArray.push('Abstract visual representation of the main theme');
  imagePromptsArray.push('Professional thumbnail image for the content');
}

// Giới hạn tối đa 5 prompts
const finalPrompts = imagePromptsArray.slice(0, 5);

// Lấy base data từ item đầu tiên
const firstItem = items[0].json;
const baseData = {
  videoId: firstItem.videoId || $('merge-translations').item.json.videoId,
  title: firstItem.title || $('merge-translations').item.json.title,
  translatedText: $('merge-translations').item.json.translatedText,
  summary: firstItem.summary || [],
  totalPrompts: finalPrompts.length
};

// QUAN TRỌNG: Trả về nhiều items (mỗi item = 1 prompt)
// n8n sẽ tự động loop qua từng item này
return finalPrompts.map((prompt, index) => ({
  json: {
    ...baseData,
    promptIndex: index + 1,
    imagePrompt: prompt  // Field này là STRING, không phải mảng
  }
}));


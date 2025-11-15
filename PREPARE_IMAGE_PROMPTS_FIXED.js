// Code FIXED cho node "Prepare Image Prompts" - KHÔNG tham chiếu node khác
// Mục đích: Parse response từ OpenAI và tạo nhiều items (mỗi item = 1 prompt)

const items = $input.all();

function safeParse(maybeJsonString) {
  if (typeof maybeJsonString !== 'string') return maybeJsonString ?? {};
  const cleaned = maybeJsonString.replace(/```json|```/g, '').trim();
  try { return JSON.parse(cleaned); } catch { return {}; }
}

// Extract data from OpenAI response
const parsed = items.map(({ json }) => {
  const raw = json?.choices?.[0]?.message?.content ?? json?.content ?? '';
  const data = safeParse(raw);
  return {
    summary: Array.isArray(data.summary) ? data.summary : [],
    imagePrompts: Array.isArray(data.image_prompts) ? data.image_prompts : []
  };
});

// Merge all summaries and prompts
const mergedSummary = parsed.flatMap(p => p.summary);
const mergedPrompts = parsed.flatMap(p => p.imagePrompts).slice(0, 5);

// Ensure we have 3-5 prompts
if (mergedPrompts.length === 0) {
  mergedPrompts.push('Cinematic scene related to the video topic');
  mergedPrompts.push('Abstract visual representation of the main theme');
  mergedPrompts.push('Professional thumbnail image for the content');
}

// Base data - không cần videoId, title, translatedText để generate images
// Chỉ cần prompts và summary
const baseData = {
  summary: mergedSummary,
  totalPrompts: mergedPrompts.length
};

// QUAN TRỌNG: Trả về nhiều items (mỗi item = 1 prompt)
// n8n sẽ tự động loop qua từng item này
return mergedPrompts.map((prompt, index) => ({
  json: {
    ...baseData,
    promptIndex: index + 1,
    imagePrompt: prompt  // Field này là STRING, không phải mảng
  }
}));


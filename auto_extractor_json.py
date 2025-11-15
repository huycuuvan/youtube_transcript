import sys
import re
import os.path
import json
import argparse
from datetime import datetime

# Các thư viện bên ngoài
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi

YOUTUBE_CHANNEL_URL = "https://www.youtube.com/c/Ph%C3%AAPhim" # THAY LINK KÊNH CỦA BẠN
# ==============================================================================

def log_message(message, output_json=False):
    """In thông báo ra màn hình kèm theo thời gian."""
    timestamp = datetime.now().isoformat()
    if not output_json:
        print(f"[{timestamp}] {message}", file=sys.stderr)

def get_latest_video_info(channel_url, output_json=False):
    """Lấy thông tin video mới nhất từ kênh YouTube."""
    log_message(f"Đang tìm video mới nhất từ kênh...", output_json)
    try:
        videos_generator = scrapetube.get_channel(channel_url=channel_url, sort_by="newest", limit=1)
        latest_video = next(videos_generator, None)
        if latest_video:
            title = latest_video['title']['runs'][0]['text']
            video_id = latest_video['videoId']
            log_message(f"Tìm thấy video mới nhất: '{title}' (ID: {video_id})", output_json)
            return {'id': video_id, 'title': title, 'url': f"https://www.youtube.com/watch?v={video_id}"}
        return None
    except Exception as e:
        log_message(f"Lỗi khi lấy video: {e}", output_json)
        return None

def get_video_transcript(video_id, output_json=False):
    """Lấy transcript từ video YouTube."""
    log_message(f"Đang trích xuất phụ đề cho video ID: {video_id}...", output_json)
    try:
        ytt_api = YouTubeTranscriptApi()
        
        # Thử lấy transcript với nhiều ngôn ngữ
        # Thứ tự ưu tiên: vi, en, auto-generated, và các ngôn ngữ khác
        languages_to_try = ['vi', 'en', 'vi-VN', 'en-US', 'en-GB']
        
        transcript_list = None
        used_language = None
        
        # Thử từng ngôn ngữ
        for lang in languages_to_try:
            try:
                transcript_list = ytt_api.fetch(video_id, languages=[lang])
                used_language = lang
                log_message(f"Tìm thấy transcript bằng ngôn ngữ: {lang}", output_json)
                break
            except:
                continue
        
        # Nếu không tìm thấy, thử lấy bất kỳ transcript nào có sẵn
        if not transcript_list:
            try:
                transcript_list = ytt_api.list_transcripts(video_id)
                # Lấy transcript đầu tiên có sẵn (có thể là auto-generated)
                transcript = transcript_list.find_transcript(['vi', 'en'])
                transcript_list = transcript.fetch()
                used_language = transcript.language_code
                log_message(f"Tìm thấy transcript tự động với ngôn ngữ: {used_language}", output_json)
            except Exception as e2:
                log_message(f"Không tìm thấy transcript nào. Lỗi: {str(e2)}", output_json)
                return {'error': str(e2), 'text': None, 'segments': [], 'word_count': 0, 'language': None}
        
        # Tạo full transcript text
        full_transcript = "\n".join([item.text for item in transcript_list])
        
        # Tạo segments với timestamps (cho subtitle generation sau này)
        segments = []
        for item in transcript_list:
            segments.append({
                'start': item.start,
                'duration': item.duration,
                'text': item.text
            })
        
        log_message("Trích xuất phụ đề thành công!", output_json)
        return {
            'text': full_transcript,
            'segments': segments,
            'word_count': len(full_transcript.split()),
            'language': used_language or (transcript_list[0].language if transcript_list else 'unknown')
        }
    except Exception as e:
        error_msg = str(e)
        log_message(f"Lỗi khi trích xuất phụ đề: {error_msg}", output_json)
        return {'error': error_msg, 'text': None, 'segments': [], 'word_count': 0, 'language': None}

def extract_video_id_from_url(url_or_id):
    """Trích xuất video ID từ YouTube URL hoặc trả về ID nếu đã là ID."""
    if not url_or_id:
        return None
    
    # Nếu đã là video ID (chỉ chứa ký tự hợp lệ)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Các pattern YouTube URL phổ biến
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None

def main():
    """Hàm logic chính của script."""
    parser = argparse.ArgumentParser(description='Extract YouTube transcript')
    parser.add_argument('--output-json', action='store_true', help='Output JSON format for n8n')
    parser.add_argument('--channel-url', type=str, help='YouTube channel URL (overrides config)')
    parser.add_argument('--video-id', type=str, help='Specific video ID or URL to extract (skips latest video)')
    # Hỗ trợ environment variable
    video_id_from_env = os.environ.get('YOUTUBE_VIDEO_ID') or os.environ.get('YOUTUBE_VIDEO_URL')
    
    args = parser.parse_args()
    output_json = args.output_json
    channel_url = args.channel_url or YOUTUBE_CHANNEL_URL
    
    log_message("--- Bắt đầu phiên làm việc ---", output_json)
    
    # Lấy video ID từ argument hoặc environment variable
    video_input = args.video_id or video_id_from_env
    video_id = None
    is_channel_url = False
    
    if video_input:
        # Kiểm tra xem có phải channel URL không
        channel_patterns = [
            r'youtube\.com\/c\/',
            r'youtube\.com\/channel\/',
            r'youtube\.com\/user\/',
            r'youtube\.com\/@',
        ]
        
        is_channel_url = any(re.search(pattern, video_input) for pattern in channel_patterns)
        
        if is_channel_url:
            # Nếu là channel URL, dùng nó để lấy video mới nhất
            log_message(f"Phát hiện channel URL, sẽ lấy video mới nhất từ channel: {video_input}", output_json)
            channel_url = video_input
        else:
            # Thử trích xuất video ID từ URL
            video_id = extract_video_id_from_url(video_input)
            if not video_id:
                log_message(f"Không thể trích xuất video ID từ: {video_input}", output_json)
                if output_json:
                    print(json.dumps({
                        'success': False,
                        'error': f'URL hoặc Video ID không hợp lệ: {video_input}',
                        'timestamp': datetime.now().isoformat()
                    }))
                return
    
    # Lấy thông tin video
    if video_id:
        video_info = {'id': video_id, 'title': 'Unknown', 'url': f"https://www.youtube.com/watch?v={video_id}"}
        log_message(f"Sử dụng video ID được chỉ định: {video_id}", output_json)
    else:
        # Lấy video mới nhất từ channel (từ channel_url đã được set ở trên hoặc default)
        video_info = get_latest_video_info(channel_url, output_json)
        if not video_info:
            if output_json:
                print(json.dumps({
                    'success': False,
                    'error': 'Không lấy được thông tin video từ YouTube',
                    'timestamp': datetime.now().isoformat()
                }))
            else:
                log_message("Không lấy được thông tin video từ YouTube. Kết thúc.", output_json)
            return
    
    # Lấy transcript
    transcript_data = get_video_transcript(video_info['id'], output_json)
    
    if not transcript_data or not transcript_data.get('text'):
        error_detail = transcript_data.get('error', 'Video có thể không có phụ đề hoặc phụ đề bị tắt.')
        error_msg = f'Không thể lấy transcript cho video này. {error_detail}'
        if output_json:
            print(json.dumps({
                'success': False,
                'error': error_msg,
                'errorDetail': transcript_data.get('error') if transcript_data else None,
                'videoId': video_info['id'],
                'videoTitle': video_info['title'],
                'videoUrl': video_info['url'],
                'timestamp': datetime.now().isoformat()
            }))
        else:
            log_message(f"Không thể lấy transcript cho video này. Kết thúc.", output_json)
        return
    
    # Output kết quả
    result = {
        'success': True,
        'videoId': video_info['id'],
        'title': video_info['title'],
        'url': video_info['url'],
        'transcript': transcript_data['text'],
        'transcriptSegments': transcript_data['segments'],
        'wordCount': transcript_data['word_count'],
        'language': transcript_data['language'],
        'channelUrl': channel_url,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if output_json:
        # Output JSON cho n8n
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Output text format (backward compatible)
        log_message(f'Video: {video_info["title"]}', output_json)
        log_message(f'Video ID: {video_info["id"]}', output_json)
        log_message(f'Transcript length: {transcript_data["word_count"]} words', output_json)
        log_message(f'Transcript preview: {transcript_data["text"][:200]}...', output_json)
    
    log_message("--- Kết thúc phiên làm việc ---", output_json)

if __name__ == "__main__":
    main()


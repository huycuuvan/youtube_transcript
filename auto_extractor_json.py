import sys
import re
import os.path
import json
import argparse
from datetime import datetime

# Các thư viện bên ngoài
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi

# Thư viện để lấy metadata đầy đủ
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

# ==============================================================================
# --- CẤU HÌNH ---
# Vui lòng điền các thông tin mặc định của bạn vào đây
# ==============================================================================
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

def get_video_metadata(video_id, output_json=False):
    """Lấy đầy đủ metadata từ YouTube video bằng yt-dlp."""
    if not YT_DLP_AVAILABLE:
        if not output_json:
            print("Warning: yt-dlp not installed. Some metadata may not be available. Install with: pip install yt-dlp", file=sys.stderr)
        return {}
    
    log_message(f"Đang lấy metadata cho video ID: {video_id}...", output_json)
    metadata = {}
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(url, download=False)
            
            # Lấy tất cả thông tin có thể
            metadata = {
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'tags': info.get('tags', []),
                'keywords': info.get('tags', []),  # Alias cho tags
                'hashtags': [],  # Sẽ extract từ description
                'playlist': info.get('playlist', ''),
                'playlist_id': info.get('playlist_id', ''),
                'playlist_title': info.get('playlist_title', ''),
                'thumbnail': info.get('thumbnail', ''),
                'thumbnails': info.get('thumbnails', []),
                'category': info.get('categories', [''])[0] if info.get('categories') else '',
                'category_id': info.get('category', ''),
                'visibility': info.get('availability', ''),
                'age_restricted': info.get('age_limit', 0) > 0,
                'audience': 'restricted' if info.get('age_limit', 0) > 0 else 'public',  # Suy ra từ age_limit
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'comment_count': info.get('comment_count', 0),
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', ''),
                'channel': info.get('channel', ''),
                'channel_id': info.get('channel_id', ''),
                'channel_url': info.get('channel_url', ''),
                'uploader': info.get('uploader', ''),
                'uploader_id': info.get('uploader_id', ''),
                'location': info.get('location', ''),
                'language': info.get('language', ''),
                'license': info.get('license', ''),
            }
            
            # Extract hashtags từ description
            if metadata.get('description'):
                hashtags = re.findall(r'#\w+', metadata['description'])
                metadata['hashtags'] = list(set(hashtags))  # Remove duplicates
            
            # Extract timestamps từ description (format: HH:MM:SS hoặc MM:SS)
            timestamps = []
            if metadata.get('description'):
                # Pattern: 00:12:34 hoặc 12:34
                timestamp_pattern = r'(\d{1,2}):(\d{2})(?::(\d{2}))?'
                matches = re.findall(timestamp_pattern, metadata['description'])
                for match in matches[:3]:  # Lấy tối đa 3 timestamps đầu tiên
                    if len(match) == 3 and match[2]:
                        # HH:MM:SS
                        hours, minutes, seconds = int(match[0]), int(match[1]), int(match[2])
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                    else:
                        # MM:SS
                        minutes, seconds = int(match[0]), int(match[1])
                        total_seconds = minutes * 60 + seconds
                    timestamps.append(total_seconds)
            
            metadata['timestamp1'] = timestamps[0] if len(timestamps) > 0 else None
            metadata['timestamp2'] = timestamps[1] if len(timestamps) > 1 else None
            metadata['timestamp3'] = timestamps[2] if len(timestamps) > 2 else None
            
            # Thumbnail text (có thể extract từ title hoặc description)
            metadata['thumbnail_text'] = metadata.get('title', '')
            
            log_message("Lấy metadata thành công!", output_json)
            
    except Exception as e:
        log_message(f"Lỗi khi lấy metadata: {str(e)}", output_json)
        # Trả về dict rỗng nếu lỗi, không fail toàn bộ script
    
    return metadata

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
    
    # Lấy metadata đầy đủ
    metadata = get_video_metadata(video_info['id'], output_json)
    
    # Cập nhật title từ metadata nếu có
    if metadata.get('title'):
        video_info['title'] = metadata['title']
    
    # Lấy transcript
    transcript_data = get_video_transcript(video_info['id'], output_json)
    
    # Nếu không có transcript, vẫn trả về metadata (không fail)
    transcript_text = transcript_data.get('text', '') if transcript_data else ''
    transcript_segments = transcript_data.get('segments', []) if transcript_data else []
    transcript_word_count = transcript_data.get('word_count', 0) if transcript_data else 0
    transcript_language = transcript_data.get('language', '') if transcript_data else ''
    
    # Output kết quả với tất cả metadata
    result = {
        'success': True,
        'videoId': video_info['id'],
        'title': video_info['title'],
        'url': video_info['url'],
        
        # Transcript
        'transcript': transcript_text,
        'transcriptSegments': transcript_segments,
        'wordCount': transcript_word_count,
        'transcriptLanguage': transcript_language,
        
        # Metadata từ yt-dlp
        'description': metadata.get('description', ''),
        'tags': metadata.get('tags', []),
        'keywords': metadata.get('keywords', []),
        'hashtags': metadata.get('hashtags', []),
        'playlist': metadata.get('playlist_title', '') or metadata.get('playlist', ''),
        'playlistId': metadata.get('playlist_id', ''),
        'thumbnail': metadata.get('thumbnail', ''),
        'thumbnails': metadata.get('thumbnails', []),
        'thumbnailText': metadata.get('thumbnail_text', ''),
        'timestamp1': metadata.get('timestamp1'),
        'timestamp2': metadata.get('timestamp2'),
        'timestamp3': metadata.get('timestamp3'),
        'category': metadata.get('category', ''),
        'categoryId': metadata.get('category_id', ''),
        'visibility': metadata.get('visibility', ''),
        'ageRestricted': metadata.get('age_restricted', False),
        'audience': metadata.get('audience', 'public'),
        'viewCount': metadata.get('view_count', 0),
        'likeCount': metadata.get('like_count', 0),
        'commentCount': metadata.get('comment_count', 0),
        'duration': metadata.get('duration', 0),
        'uploadDate': metadata.get('upload_date', ''),
        'channel': metadata.get('channel', ''),
        'channelId': metadata.get('channel_id', ''),
        'channelUrl': metadata.get('channel_url', '') or channel_url,
        'uploader': metadata.get('uploader', ''),
        'uploaderId': metadata.get('uploader_id', ''),
        'location': metadata.get('location', ''),
        'language': metadata.get('language', ''),
        'license': metadata.get('license', ''),
        
        # Timestamp
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


# auto_extractor_json.py
# Version cải tiến để output JSON cho n8n workflow

import sys
import re
import os.path
import json
import argparse
from datetime import datetime

# Các thư viện bên ngoài
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi

# ==============================================================================
# --- CẤU HÌNH ---
# Vui lòng điền các thông tin mặc định của bạn vào đây
# ==============================================================================
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/c/Ph%C3%AAPhim" # THAY LINK KÊNH CỦA BẠN
# ==============================================================================

def log_message(message, output_json=False):
    """In thông báo ra màn hình kèm theo thời gian."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
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
        transcript_list = ytt_api.fetch(video_id, languages=['vi', 'en'])
        
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
            'language': transcript_list[0].language if transcript_list else 'unknown'
        }
    except Exception as e:
        log_message(f"Lỗi khi trích xuất phụ đề: {str(e)}", output_json)
        return None

def main():
    """Hàm logic chính của script."""
    parser = argparse.ArgumentParser(description='Extract YouTube transcript')
    parser.add_argument('--output-json', action='store_true', help='Output JSON format for n8n')
    parser.add_argument('--channel-url', type=str, help='YouTube channel URL (overrides config)')
    parser.add_argument('--video-id', type=str, help='Specific video ID to extract (skips latest video)')
    
    args = parser.parse_args()
    output_json = args.output_json
    channel_url = args.channel_url or YOUTUBE_CHANNEL_URL
    
    log_message("--- Bắt đầu phiên làm việc ---", output_json)
    
    # Lấy thông tin video
    if args.video_id:
        video_info = {'id': args.video_id, 'title': 'Unknown', 'url': f"https://www.youtube.com/watch?v={args.video_id}"}
        log_message(f"Sử dụng video ID được chỉ định: {args.video_id}", output_json)
    else:
        video_info = get_latest_video_info(channel_url, output_json)
        if not video_info:
            if output_json:
                print(json.dumps({
                    'success': False,
                    'error': 'Không lấy được thông tin video từ YouTube',
                    'timestamp': datetime.utcnow().isoformat()
                }))
            else:
                log_message("Không lấy được thông tin video từ YouTube. Kết thúc.", output_json)
            return
    
    # Lấy transcript
    transcript_data = get_video_transcript(video_info['id'], output_json)
    
    if not transcript_data or not transcript_data.get('text'):
        if output_json:
            print(json.dumps({
                'success': False,
                'error': 'Không thể lấy transcript cho video này',
                'videoId': video_info['id'],
                'timestamp': datetime.utcnow().isoformat()
            }))
        else:
            log_message("Không thể lấy transcript cho video này. Kết thúc.", output_json)
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
        log_message(f"Video: {video_info['title']}", output_json)
        log_message(f"Video ID: {video_info['id']}", output_json)
        log_message(f"Transcript length: {transcript_data['word_count']} words", output_json)
        log_message(f"Transcript preview: {transcript_data['text'][:200]}...", output_json)
    
    log_message("--- Kết thúc phiên làm việc ---", output_json)

if __name__ == "__main__":
    main()


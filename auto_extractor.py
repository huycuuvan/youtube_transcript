# auto_extractor.py

import sys
import re
import os.path
from datetime import datetime

# Các thư viện bên ngoài
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi

# Các thư viện của Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ==============================================================================
# --- CẤU HÌNH ---
# Vui lòng điền các thông tin mặc định của bạn vào đây
# ==============================================================================
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/c/Ph%C3%AAPhim" # THAY LINK KÊNH CỦA BẠN
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1EodXAsOBbjNnLY8_-K-eZE2sDp4VfOZg3GrfS79EZlY/edit?usp=sharing" # THAY LINK SHEET CỦA BẠN
SHEET_NAME = "Trang tính1" # THAY TÊN TRANG TÍNH (SHEET NAME)
TITLE_COLUMN = "B"        # Cột chứa tiêu đề
TRANSCRIPT_COLUMN = "D"   # Cột chứa transcript
# ==============================================================================

def log_message(message):
    """In thông báo ra màn hình kèm theo thời gian."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"[{timestamp}] {message}")

def get_latest_video_info(channel_url):
    # (Hàm này giữ nguyên như cũ)
    log_message(f"Đang tìm video mới nhất từ kênh...")
    videos_generator = scrapetube.get_channel(channel_url=channel_url, sort_by="newest", limit=1)
    latest_video = next(videos_generator, None)
    if latest_video:
        title = latest_video['title']['runs'][0]['text']
        log_message(f"Tìm thấy video mới nhất: '{title}'")
        return {'id': latest_video['videoId'], 'title': title}
    return None

def get_video_transcript(video_id):
    # (Hàm này giữ nguyên như cũ)
    log_message(f"Đang trích xuất phụ đề cho video ID: {video_id}...")
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.fetch(video_id, languages=['vi', 'en'])
    full_transcript = "\n".join([item.text for item in transcript_list])
    log_message("Trích xuất phụ đề thành công!")
    return full_transcript

def chunk_text(text, limit=49999):
    # (Hàm này giữ nguyên như cũ)
    return [text[i:i+limit] for i in range(0, len(text), limit)]
    
def get_google_sheets_service():
    """Hàm xử lý xác thực và trả về đối tượng service của Google Sheets."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def perform_sheet_update(service, spreadsheet_id, sheet_name, title_column, transcript_column, video_title, transcript_data):
    """Hàm thực hiện xóa và ghi đè dữ liệu mới."""
    try:
        log_message("Đang xóa nội dung cũ...")
        clear_ranges = [
            f"'{sheet_name}'!{title_column}2:{title_column}",
            f"'{sheet_name}'!{transcript_column}2:{transcript_column}"
        ]
        body = {'ranges': clear_ranges}
        service.spreadsheets().values().batchClear(spreadsheetId=spreadsheet_id, body=body).execute()

        log_message("Đang ghi nội dung mới...")
        chunks = chunk_text(transcript_data)
        title_col_index = ord(title_column) - 65
        transcript_col_index = ord(transcript_column) - 65
        max_col_index = max(title_col_index, transcript_col_index)
        
        first_row_values = [''] * (max_col_index + 1)
        first_row_values[title_col_index] = video_title
        first_row_values[transcript_col_index] = chunks[0] if chunks else ''
        
        other_rows_values = []
        if len(chunks) > 1:
            for chunk in chunks[1:]:
                row = [''] * (max_col_index + 1)
                row[transcript_col_index] = chunk
                other_rows_values.append(row)
        
        update_body = {'values': [first_row_values] + other_rows_values}
        update_range = f"'{sheet_name}'!A2"
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=update_range, valueInputOption='USER_ENTERED', body=update_body).execute()
        
        log_message("Ghi đè dữ liệu mới thành công!")
    except HttpError as err:
        log_message(f"Lỗi khi cập nhật sheet: {err.reason}")
    except Exception as e:
        log_message(f"Lỗi không xác định khi cập nhật sheet: {e}")


def main():
    """Hàm logic chính của script."""
    log_message("--- Bắt đầu phiên làm việc ---")
    
    # Lấy thông tin video mới nhất từ YouTube
    video_info = get_latest_video_info(YOUTUBE_CHANNEL_URL)
    if not video_info:
        log_message("Không lấy được thông tin video từ YouTube. Kết thúc.")
        return

    new_video_title = video_info['title']
    
    # Lấy service để tương tác với Google Sheets
    try:
        service = get_google_sheets_service()
        
        # Trích xuất spreadsheet ID từ URL
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', GOOGLE_SHEET_URL)
        if not match:
            log_message("URL của Google Sheet không hợp lệ. Kết thúc.")
            return
        spreadsheet_id = match.group(1)
        
        # Đọc tiêu đề hiện tại từ Sheet (ô B2)
        current_title_range = f"'{SHEET_NAME}'!{TITLE_COLUMN}2"
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=current_title_range).execute()
        current_title_in_sheet = result.get('values', [['']])[0][0]

        # LOGIC MỚI: So sánh tiêu đề
        if new_video_title.strip() == current_title_in_sheet.strip():
            log_message("Tiêu đề video mới giống với tiêu đề đã có trong sheet. Không cần cập nhật. Bỏ qua.")
        else:
            log_message("Phát hiện video mới. Tiến hành lấy transcript và cập nhật sheet.")
            transcript = get_video_transcript(video_info['id'])
            if transcript:
                perform_sheet_update(service, spreadsheet_id, SHEET_NAME, TITLE_COLUMN, TRANSCRIPT_COLUMN, new_video_title, transcript)

    except HttpError as err:
        log_message(f"Lỗi Google API: {err.reason}")
    except Exception as e:
        log_message(f"Lỗi không xác định: {e}")

    log_message("--- Kết thúc phiên làm việc ---")

if __name__ == "__main__":
    main()
# app_gui.py

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import sys
import re
import os.path

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
# PHẦN LOGIC CỐT LÕI (Không thay đổi)
# ==============================================================================
def get_latest_video_info(channel_url: str) -> dict:
    try:
        print(f"🔍 Đang tìm video mới nhất từ kênh...")
        videos_generator = scrapetube.get_channel(channel_url=channel_url, sort_by="newest", limit=1)
        latest_video = next(videos_generator, None)
        if latest_video:
            video_id = latest_video['videoId']
            title = latest_video['title']['runs'][0]['text']
            print(f"✅ Tìm thấy video: '{title}' (ID: {video_id})")
            return {'id': video_id, 'title': title}
        return None
    except Exception as e:
        print(f"❗️ Lỗi khi lấy video: {e}", file=sys.stderr)
        return None

def get_video_transcript(video_id: str) -> str:
    try:
        print(f"📄 Đang trích xuất phụ đề cho video ID: {video_id}...")
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id, languages=['vi', 'en'])
        full_transcript = "\n".join([item.text for item in transcript_list])
        print("✅ Trích xuất phụ đề thành công!")
        return full_transcript
    except Exception as e:
        print(f"❗️ Lỗi khi trích xuất phụ đề: {str(e)}", file=sys.stderr)
        return ""

def chunk_text(text, limit=49999):
    return [text[i:i+limit] for i in range(0, len(text), limit)]

# ==============================================================================
# CẬP NHẬT: HÀM GHI ĐÈ ĐƠN GIẢN
# ==============================================================================
def write_to_google_sheet(sheet_url, sheet_name, title_column, transcript_column, video_title, transcript_data):
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

    try:
        service = build('sheets', 'v4', credentials=creds)
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not match:
            print("❗️ URL của Google Sheet không hợp lệ.")
            return
        spreadsheet_id = match.group(1)

        # BƯỚC 1: Xóa nội dung cũ trong cả hai cột (từ dòng 2 trở đi)
        print("🧹 Đang xóa nội dung cũ...")
        clear_ranges = [
            f"'{sheet_name}'!{title_column.upper()}2:{title_column.upper()}",
            f"'{sheet_name}'!{transcript_column.upper()}2:{transcript_column.upper()}"
        ]
        body = {'ranges': clear_ranges}
        service.spreadsheets().values().batchClear(spreadsheetId=spreadsheet_id, body=body).execute()
        print("✅ Đã xóa nội dung cũ thành công.")

        # BƯỚC 2: Ghi dữ liệu mới vào
        print(f"✍️ Đang ghi nội dung mới...")
        chunks = chunk_text(transcript_data)
        
        # Dòng đầu tiên chứa tiêu đề và phần đầu transcript
        first_row_values = []
        # Các dòng tiếp theo chỉ chứa các phần transcript còn lại
        other_rows_values = []

        # Ghi tiêu đề vào đúng vị trí
        title_col_index = ord(title_column.upper()) - 65
        transcript_col_index = ord(transcript_column.upper()) - 65
        max_col_index = max(title_col_index, transcript_col_index)
        
        first_row_values = [''] * (max_col_index + 1)
        first_row_values[title_col_index] = video_title
        first_row_values[transcript_col_index] = chunks[0] if chunks else ''
        
        if len(chunks) > 1:
            for chunk in chunks[1:]:
                row = [''] * (max_col_index + 1)
                row[transcript_col_index] = chunk
                other_rows_values.append(row)
        
        update_body = {'values': [first_row_values] + other_rows_values}
        update_range = f"'{sheet_name}'!A2" # Bắt đầu ghi từ A2 để căn chỉnh các cột
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=update_range, valueInputOption='USER_ENTERED', body=update_body).execute()
        
        print(f"✅ Đã ghi đè dữ liệu mới thành công!")

    except HttpError as err:
        print(f"❗️ Lỗi khi ghi vào Google Sheet: {err.reason}", file=sys.stderr)
        print(f"❗️ Details: {err.error_details}", file=sys.stderr)
    except Exception as e:
        print(f"❗️ Lỗi không xác định với Google Sheet: {e}", file=sys.stderr)

# ==============================================================================
# GIAO DIỆN (Không thay đổi)
# ==============================================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Extractor")
        self.root.geometry("700x600")

        extract_frame = tk.Frame(root, padx=10, pady=10)
        extract_frame.pack(fill='x')
        tk.Label(extract_frame, text="Link Kênh YouTube:").pack(side='left')
        self.url_entry = tk.Entry(extract_frame)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=5)

        sheets_frame = tk.Frame(root, padx=10, pady=5)
        sheets_frame.pack(fill='x')
        tk.Label(sheets_frame, text="Link Google Sheet:").pack(side='left')
        self.sheet_url_entry = tk.Entry(sheets_frame)
        self.sheet_url_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        config_frame = tk.Frame(root, padx=10, pady=5)
        config_frame.pack(fill='x')
        tk.Label(config_frame, text="Tên trang tính:").pack(side='left')
        self.sheet_name_entry = tk.Entry(config_frame, width=15)
        self.sheet_name_entry.insert(0, "Trang tính1")
        self.sheet_name_entry.pack(side='left', padx=(5,10))
        
        tk.Label(config_frame, text="Cột Tiêu đề:").pack(side='left')
        self.title_col_entry = tk.Entry(config_frame, width=5)
        self.title_col_entry.insert(0, "B")
        self.title_col_entry.pack(side='left', padx=(5,10))
        
        tk.Label(config_frame, text="Cột Transcript:").pack(side='left')
        self.transcript_col_entry = tk.Entry(config_frame, width=5)
        self.transcript_col_entry.insert(0, "D")
        self.transcript_col_entry.pack(side='left', padx=5)

        self.extract_button = tk.Button(root, text="Lấy Transcript và Ghi đè", command=self.start_extraction_thread, padx=10, pady=5)
        self.extract_button.pack(pady=10)
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.log_area.pack(padx=10, pady=10, fill='both', expand=True)

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def extraction_logic(self):
        self.log_area.configure(state='normal'); self.log_area.delete(1.0, tk.END); self.log_area.configure(state='disabled')
        original_stdout, original_stderr = sys.stdout, sys.stderr
        sys.stdout.write = lambda msg: self.log(msg.strip()); sys.stderr.write = lambda msg: self.log(msg.strip())
        try:
            channel_url = self.url_entry.get()
            if not channel_url: return messagebox.showerror("Lỗi", "Vui lòng nhập link kênh YouTube.")
            video_info = get_latest_video_info(channel_url)
            if video_info and video_info['id']:
                transcript = get_video_transcript(video_info['id'])
                if transcript:
                    messagebox.showinfo("Thành công", "Đã trích xuất transcript thành công!")
                    sheet_url = self.sheet_url_entry.get()
                    sheet_name = self.sheet_name_entry.get()
                    title_column = self.title_col_entry.get()
                    transcript_column = self.transcript_col_entry.get()
                    if all([sheet_url, sheet_name, title_column, transcript_column]):
                        print("\n▶️ Bắt đầu quá trình ghi vào Google Sheets...")
                        write_to_google_sheet(sheet_url, sheet_name, title_column, transcript_column, video_info['title'], transcript)
                    else:
                        print("\nℹ️ Bỏ qua việc ghi vào Google Sheets vì thiếu thông tin.")
                else:
                    messagebox.showerror("Lỗi", "Không thể lấy transcript cho video này.")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy video nào.")
        except Exception as e:
            self.log(f"❗️ Lỗi không xác định: {e}"); messagebox.showerror("Lỗi nghiêm trọng", f"Đã xảy ra lỗi không xác định:\n{e}")
        finally:
            sys.stdout, sys.stderr = original_stdout, original_stderr
            self.extract_button.config(state='normal')

    def start_extraction_thread(self):
        self.extract_button.config(state='disabled')
        threading.Thread(target=self.extraction_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
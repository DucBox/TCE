#!/usr/bin/env python3
import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from init_firebase import FirebaseManager

class GoogleSheetsExtractor:
    def __init__(self):
        self.service = None
        self.firebase = FirebaseManager()
        self._init_sheets_api()
    
    def _init_sheets_api(self):
        try:
            firebase_config = os.getenv('FIREBASE_CONFIG')
            if not firebase_config:
                raise ValueError("Biến môi trường FIREBASE_CONFIG không tồn tại")
            
            config_dict = json.loads(firebase_config)
            
            credentials = service_account.Credentials.from_service_account_info(
                config_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            
        except Exception as e:
            raise Exception(f"Lỗi khởi tạo Google Sheets API: {e}")
    
    def _normalize_email(self, email):
        """Normalize email: chỉ xóa spaces"""
        if not email:
            return ''
        return email.replace(' ', '')
    
    def test_connection(self, sheet_id):
        try:
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheet_title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
            print(f"Kết nối thành công với sheet: '{sheet_title}'")
            
            sheets = sheet_metadata.get('sheets', [])
            print(f"Số lượng tabs: {len(sheets)}")
            for sheet in sheets:
                tab_name = sheet.get('properties', {}).get('title', 'Unknown')
                print(f"   - Tab: {tab_name}")
            
            return True
            
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            return False
    
    def extract_and_update_firebase(self, sheet_id):
        try:
            # Lấy tên tab đầu tiên
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            first_sheet_name = sheet_metadata['sheets'][0]['properties']['title']
            range_name = f"'{first_sheet_name}'!A:H"
            
            print(f"Đang đọc từ tab: {first_sheet_name}")
            
            # Đọc dữ liệu
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print("Không có dữ liệu trong sheet")
                return
            
            headers = values[0]
            data_rows = values[1:]
            
            print(f"Headers: {headers}")
            print(f"Số dòng dữ liệu: {len(data_rows)}")
            
            updated_count = 0
            failed_count = 0
            
            for i, row in enumerate(data_rows, 1):
                try:
                    # Đảm bảo row có đủ cột (8 cột)
                    while len(row) < 8:
                        row.append('')
                    
                    original_email = row[4]
                    normalized_email = self._normalize_email(original_email)
                    
                    row_data = {
                        'dau_thoi_gian': row[0],
                        'ho_ten': row[1],
                        'lop': row[2],
                        'sdt': row[3],
                        'email': normalized_email,
                        'link_bai_lam': row[5],
                        'status': row[6],
                        'feedback': row[7]
                    }
                    
                    # Log nếu có spaces bị xóa
                    if original_email != normalized_email:
                        print(f"   Email normalized: '{original_email}' → '{normalized_email}'")
                    
                    # Update vào Firebase
                    if self._update_user_data(row_data):
                        updated_count += 1
                        print(f"✅ [{i}/{len(data_rows)}] {row_data['email']}")
                    else:
                        failed_count += 1
                        print(f"❌ [{i}/{len(data_rows)}] {row_data['email']} - FAILED")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"❌ [{i}/{len(data_rows)}] Lỗi parse dòng: {e}")
            
            print(f"\n📊 Kết quả: {updated_count} thành công, {failed_count} thất bại")
            
        except Exception as e:
            print(f"Lỗi extract data: {e}")
    
    def _update_user_data(self, row_data):
        try:
            email = row_data['email']
            sdt = row_data['sdt']
            
            if not email and not sdt:
                print(f"   ⚠️  Thiếu cả email và SĐT, skip")
                return False
            
            user_ref = None
            user_doc = None
            search_method = ""
            
            # Bước 1: Thử tìm bằng email (username trước @)
            if email:
                user_id = email.split('@')[0]
                user_ref = self.firebase.db.collection('users').document(user_id)
                user_doc = user_ref.get()
                
                if user_doc.exists:
                    search_method = f"email (user_id: {user_id})"
                else:
                    print(f"   ⚠️  Không tìm thấy bằng email: {user_id}")
            
            # Bước 2: Nếu không tìm thấy bằng email, thử tìm bằng SĐT
            if not user_doc or not user_doc.exists:
                if sdt:
                    # Normalize SĐT (xóa spaces)
                    normalized_sdt = sdt.replace(' ', '')
                    
                    # Query tìm user có profile.phone = sdt
                    users_query = self.firebase.db.collection('users').where('profile.phone', '==', normalized_sdt).limit(1).stream()
                    
                    users_list = list(users_query)
                    if users_list:
                        user_doc = users_list[0]
                        user_ref = self.firebase.db.collection('users').document(user_doc.id)
                        search_method = f"SĐT ({normalized_sdt})"
                    else:
                        print(f"   ⚠️  Không tìm thấy bằng SĐT: {normalized_sdt}")
            
            # Bước 3: Nếu cả 2 cách đều không tìm thấy → skip
            if not user_doc or not user_doc.exists:
                print(f"   ❌ Không tìm thấy user - Email: {email}, SĐT: {sdt} → SKIP")
                return False
            
            # Tìm thấy user, tiếp tục update
            print(f"   🔍 Tìm thấy bằng: {search_method}")
            
            user_data = user_doc.to_dict()
            
            # Update profile nếu chưa có
            if not user_data.get('profile', {}).get('ho_ten'):
                user_ref.update({
                    'profile.ho_ten': row_data['ho_ten'],
                    'profile.lop': row_data['lop']
                })
            
            # Tạo feedback object
            feedback = {
                'thoi_gian': row_data['dau_thoi_gian'],
                'noi_dung': row_data['feedback'],
                'link_bai_lam': row_data['link_bai_lam']
            }
            
            # Thêm feedback vào array (chỉ với user role)
            if user_data.get('role') == 'user' and row_data['feedback']:
                user_ref.update({
                    'feedbacks': user_data.get('feedbacks', []) + [feedback]
                })
            
            return True
            
        except Exception as e:
            print(f"   ❌ Lỗi update user - Email: {row_data.get('email', 'N/A')}, SĐT: {row_data.get('sdt', 'N/A')}: {e}")
            return False
    
# Test script
if __name__ == "__main__":
    SHEET_ID = "1k6cy4Gb0VT7UtNYujRupP16V8MJF03bphoi-JIWPpqE"
    
    try:
        extractor = GoogleSheetsExtractor()
        
        if extractor.test_connection(SHEET_ID):
            print("="*50)
            extractor.extract_and_update_firebase(SHEET_ID)
        
    except Exception as e:
        print(f"Lỗi: {e}")
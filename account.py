#!/usr/bin/env python3
import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

class AccountCreator:
    def __init__(self):
        self.db = None
        self._init_firebase()
    
    def _init_firebase(self):
        try:
            if firebase_admin._apps:
                self.db = firestore.client()
                return
            
            firebase_config = os.getenv('FIREBASE_CONFIG')
            if not firebase_config:
                raise ValueError("Biến môi trường FIREBASE_CONFIG không tồn tại")
            
            config_dict = json.loads(firebase_config)
            cred = credentials.Certificate(config_dict)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            
        except Exception as e:
            raise Exception(f"Lỗi khởi tạo Firebase: {e}")
    
    def create_accounts_from_data(self):
        # Data từ bạn cung cấp
        phones = [
            "0945513426", "0826785488", "0329391581", "0865 597 229", "0862457811",
            "0949846569", "0986736382", "0868110492", "0328181208", "0389341912",
            "0911125209", "0986472737", "037 9438658", "0942405985", "0973748443",
            "0812533222", "0325106387", "0325106387"
        ]
        
        emails = [
            "vietthanh.tce@gmail.com", "nguyenthiyenchi241@gmail.com", 
            "jenniethu12345@gmail.com", "uyennguyenphuong280409@gmail.com", "hel",
            "llinhchile734@gmail.com", "thucquyenvu0520@gmail.com", 
            "ngvietchinh0503@gmail.com", "thquynh2008@gmail.com", "duychien226@gmail.com",
            "thiloan862005@gmail.com", "havy18092009@gmail.com", "tocduong2k10@gmail.com",
            "chillzy14iu11@gmail.com", "hngthaor@gmail.com", "quyendoduc2005ls@gmail.com",
            "khanhlinh86840@gmail.com"
        ]
        
        roles = ["admin"] + ["user"] * (len(emails) - 1)
        
        # Clean phone numbers (remove spaces)
        phones = [phone.replace(" ", "") for phone in phones]
        
        created_count = 0
        failed_count = 0
        
        for i, (email, phone, role) in enumerate(zip(emails, phones, roles)):
            try:
                self._create_single_account(email, phone, role)
                created_count += 1
                print(f"✅ [{i+1}/{len(emails)}] {email} ({role})")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ [{i+1}/{len(emails)}] {email}: {e}")
        
        print(f"\n📊 Kết quả: {created_count} thành công, {failed_count} thất bại")
    
    def _create_single_account(self, email, phone, role):
        # Tạo user_id từ email
        user_id = email.replace('@', '_').replace('.', '_').replace(' ', '_')
        
        account_data = {
            'email': email,
            'password': phone,
            'role': role,
            'created_at': datetime.now().isoformat(),
            'active': True,
            'profile': {
                'ho_ten': '',
                'lop': '',
                'phone': phone
            }
        }
        
        if role == 'user':
            account_data['feedbacks'] = []
        
        # Lưu vào Firestore
        doc_ref = self.db.collection('users').document(user_id)
        doc_ref.set(account_data)

if __name__ == "__main__":
    try:
        creator = AccountCreator()
        creator.create_accounts_from_data()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
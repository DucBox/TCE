#!/usr/bin/env python3
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseManager:
    def __init__(self):
        self.db = None
        self._init_firebase()
    
    def _init_firebase(self):
        """Initialize Firebase từ biến môi trường"""
        try:
            if firebase_admin._apps:
                self.db = firestore.client()
                return
            
            # Đọc từ biến môi trường FIREBASE_CONFIG
            firebase_config = os.getenv('FIREBASE_CONFIG')
            if not firebase_config:
                raise ValueError("Biến môi trường FIREBASE_CONFIG không tồn tại")
            
            config_dict = json.loads(firebase_config)
            cred = credentials.Certificate(config_dict)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            
        except Exception as e:
            raise Exception(f"Lỗi khởi tạo Firebase: {e}")
    
    def test_connection(self):
        """Test kết nối Firebase"""
        try:
            # Thử đọc một collection để test
            test_ref = self.db.collection('test').limit(1)
            list(test_ref.stream())
            return True
        except Exception as e:
            raise Exception(f"Không thể kết nối Firebase: {e}")

# Test script
if __name__ == "__main__":
    try:
        firebase_manager = FirebaseManager()
        firebase_manager.test_connection()
        print("✅ Firebase kết nối thành công!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
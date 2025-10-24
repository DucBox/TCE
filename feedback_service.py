#!/usr/bin/env python3
import os
import json
from datetime import datetime
from init_firebase import FirebaseManager

class UserFeedbackService:
    def __init__(self):
        self.firebase = FirebaseManager()
    
    def authenticate_user(self, email, password):
        """
        Xác thực user bằng email và password (SĐT)
        Returns: user_data nếu thành công, None nếu thất bại
        """
        try:
            # Normalize email
            normalized_email = email.replace(' ', '')
            user_id = normalized_email.replace('@', '_').replace('.', '_').replace(' ', '_')
            
            # Lấy user document
            user_ref = self.firebase.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return None
            
            user_data = user_doc.to_dict()
            
            # Check password (SĐT)
            if user_data.get('password') == password.replace(' ', ''):
                return user_data
            
            return None
            
        except Exception as e:
            print(f"Lỗi authenticate: {e}")
            return None
    
    def get_user_feedbacks(self, email):
        """
        Lấy tất cả feedbacks của user theo email
        Returns: List feedbacks sorted by thời gian mới nhất
        """
        try:
            # Normalize email
            normalized_email = email.replace(' ', '')
            user_id = normalized_email.replace('@', '_').replace('.', '_').replace(' ', '_')
            
            # Lấy user document
            user_ref = self.firebase.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return []
            
            user_data = user_doc.to_dict()
            feedbacks = user_data.get('feedbacks', [])
            
            # Sort theo thời gian mới nhất (giả sử format: DD/MM/YYYY HH:MM:SS)
            feedbacks_sorted = sorted(
                feedbacks, 
                key=lambda x: self._parse_datetime(x.get('thoi_gian', '')), 
                reverse=True
            )
            
            return feedbacks_sorted
            
        except Exception as e:
            print(f"Lỗi get feedbacks: {e}")
            return []
    
    def _parse_datetime(self, time_str):
        """Parse thời gian từ string sang datetime để sort"""
        try:
            if not time_str:
                return datetime.min
            
            # Format: "17/10/2025 22:39:05"
            return datetime.strptime(time_str, "%d/%m/%Y %H:%M:%S")
        except:
            return datetime.min
    
    def get_user_profile(self, email):
        """Lấy thông tin profile của user"""
        try:
            normalized_email = email.replace(' ', '')
            user_id = normalized_email.replace('@', '_').replace('.', '_').replace(' ', '_')
            
            user_ref = self.firebase.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return None
            
            user_data = user_doc.to_dict()
            return {
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'profile': user_data.get('profile', {})
            }
            
        except Exception as e:
            print(f"Lỗi get profile: {e}")
            return None

# Test script
if __name__ == "__main__":
    service = UserFeedbackService()
    
    # Test authenticate
    test_email = "nguyenthiyenchi241@gmail.com"
    test_password = "0826785488"
    
    user = service.authenticate_user(test_email, test_password)
    if user:
        print(f"Login thành công: {user['email']}")
        
        # Get feedbacks
        feedbacks = service.get_user_feedbacks(test_email)
        print(f"Số feedbacks: {len(feedbacks)}")
        
        for i, feedback in enumerate(feedbacks, 1):
            print(f"\nFeedback {i}:")
            print(f"  Thời gian: {feedback.get('thoi_gian')}")
            print(f"  Nội dung: {feedback.get('noi_dung')[:50]}...")
            print(f"  Link: {feedback.get('link_bai_lam')}")
    else:
        print("Login thất bại")
#!/usr/bin/env python3
import streamlit as st
from feedback_service import UserFeedbackService
from ggsheet_extract import GoogleSheetsExtractor

def main():
    st.set_page_config(page_title="TCE Feedback System", layout="wide")
    
    # Initialize services
    if 'feedback_service' not in st.session_state:
        st.session_state.feedback_service = UserFeedbackService()
    
    if 'ggsheet_extractor' not in st.session_state:
        st.session_state.ggsheet_extractor = GoogleSheetsExtractor()
    
    # Check login status
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_data = None
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # Route based on user role
        if st.session_state.user_data['role'] == 'admin':
            show_admin_dashboard()
        else:
            show_user_dashboard()

def show_login_page():
    st.title("TCE Feedback System - Login")
    
    with st.form("login_form"):
        st.subheader("Đăng nhập")
        email = st.text_input("Email")
        password = st.text_input("Số điện thoại", type="password")
        submit = st.form_submit_button("Đăng nhập")
        
        if submit:
            if email and password:
                user_data = st.session_state.feedback_service.authenticate_user(email, password)
                
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user_data
                    st.success(f"Đăng nhập thành công! Chào {user_data.get('profile', {}).get('ho_ten', email)}")
                    st.rerun()
                else:
                    st.error("Email hoặc số điện thoại không đúng!")
            else:
                st.error("Vui lòng nhập đầy đủ thông tin!")

def show_user_dashboard():
    # Header (giữ nguyên)
    
    profile = st.session_state.user_data.get('profile', {})
    st.title(f"Hi {profile.get('ho_ten', 'bạn')}! - Class: {profile.get('lop', 'N/A')}")

    if st.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.rerun()
    
    st.divider()
    
    # Get and display feedbacks
    email = st.session_state.user_data['email']
    feedbacks = st.session_state.feedback_service.get_user_feedbacks(email)
    
    if feedbacks:
        st.subheader(f"Feedback của bạn ({len(feedbacks)} bài)")
        
        for i, feedback in enumerate(feedbacks):
            with st.container():
                st.markdown(f"### Bài {i+1}")
                
                # Thời gian
                st.write(f"**Thời gian:** {feedback.get('thoi_gian', 'N/A')}")
                
                # Feedback content
                feedback_content = feedback.get('noi_dung', '')
                if feedback_content:
                    st.markdown("**Feedback từ giáo viên:**")
                    st.info(feedback_content)
                else:
                    st.warning("Chưa có feedback")
                
                # Xem bài làm section
                link = feedback.get('link_bai_lam', '')
                if link:
                    st.markdown("**Xem bài làm:**")
                    st.text(link)
                
                st.divider()
    else:
        st.info("Bạn chưa có feedback nào. Hãy nộp bài để nhận feedback từ giáo viên!")

def show_admin_dashboard():
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("Admin Dashboard")
        st.write(f"Chào {st.session_state.user_data['email']}")
    
    with col2:
        if st.button("Đăng xuất"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()
    
    st.divider()
    
    # Google Sheets Import Section
    st.subheader("Import dữ liệu từ Google Sheets")
    
    with st.form("import_form"):
        sheet_url = st.text_input(
            "URL Google Sheets", 
            placeholder="https://docs.google.com/spreadsheets/d/SHEET_ID/edit"
        )
        
        submit = st.form_submit_button("Import dữ liệu")
        
        if submit and sheet_url:
            try:
                # Extract sheet ID from URL
                if '/d/' in sheet_url:
                    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                else:
                    st.error("URL không hợp lệ!")
                    return
                
                with st.spinner("Đang kiểm tra kết nối..."):
                    # Test connection
                    if st.session_state.ggsheet_extractor.test_connection(sheet_id):
                        st.success("Kết nối thành công!")
                        
                        with st.spinner("Đang import dữ liệu..."):
                            # Extract and update
                            st.session_state.ggsheet_extractor.extract_and_update_firebase(sheet_id)
                            st.success("Import thành công!")
                    else:
                        st.error("Không thể kết nối đến Google Sheets!")
                        
            except Exception as e:
                st.error(f"Lỗi: {e}")
    
    # Stats section
    st.divider()
    st.subheader("Thống kê hệ thống")
    
    # Simple stats (you can expand this)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tổng số học sinh", "16")  # You can make this dynamic
    
    with col2:
        st.metric("Số bài đã chấm", "45")  # You can make this dynamic
    
    with col3:
        st.metric("Hoạt động hôm nay", "12")  # You can make this dynamic

if __name__ == "__main__":
    main()
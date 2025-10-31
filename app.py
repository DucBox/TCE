#!/usr/bin/env python3
import streamlit as st
import pandas as pd
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
        st.session_state.username = None
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # Route based on user role
        if st.session_state.user_data['role'] == 'admin':
            show_admin_dashboard()
        else:
            show_user_dashboard()

def show_login_page():
    st.title("🎓 TCE Feedback System")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Đăng nhập")
        
        with st.form("login_form"):
            username = st.text_input(
                "Tài khoản", 
                placeholder="Nhập username (là phần trước @ trong email - Ví Dụ: ducngo)",
                help="Username là phần trước @ trong email của bạn"
            )
            password = st.text_input(
                "Mật khẩu", 
                type="password",
                placeholder="Nhập số điện thoại",
                help="Mật khẩu là số điện thoại của bạn"
            )
            
            submit = st.form_submit_button("Đăng nhập", width='stretch')
            
            if submit:
                if username and password:
                    with st.spinner("Đang xác thực..."):
                        user_data = st.session_state.feedback_service.authenticate_user(username, password)
                        
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.user_data = user_data
                            st.session_state.username = username
                            st.success(f"✅ Đăng nhập thành công! Chào {user_data.get('profile', {}).get('ho_ten', username)}")
                            st.rerun()
                        else:
                            st.error("❌ Tài khoản hoặc mật khẩu không đúng!")
                else:
                    st.warning("⚠️ Vui lòng nhập đầy đủ thông tin!")

def show_user_dashboard():
    # Header with profile info
    profile = st.session_state.user_data.get('profile', {})
    email = st.session_state.user_data.get('email', '')
    
    # Top bar
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title(f"👋 Xin chào, {profile.get('ho_ten', 'bạn')}!")
        if profile.get('lop'):
            st.markdown(f"**Lớp:** {profile.get('lop')}")
        st.markdown(f"**Email:** {email}")
    
    with col2:
        st.write("")  # spacing
        if st.button("🚪 Đăng xuất", width='stretch'):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.username = None
            st.rerun()
    
    st.divider()
    
    # Get and display feedbacks using username
    username = st.session_state.username
    feedbacks = st.session_state.feedback_service.get_user_feedbacks(username)
    
    if feedbacks:
        st.subheader(f"📝 Feedback của bạn ({len(feedbacks)} bài)")
        
        for i, feedback in enumerate(feedbacks, 1):
            with st.expander(f"Bài {i} - {feedback.get('thoi_gian', 'N/A')}", expanded=(i==1)):
                # Thời gian
                st.write(f"**⏰ Thời gian nộp:** {feedback.get('thoi_gian', 'N/A')}")
                
                # Link bài làm
                link = feedback.get('link_bai_lam', '')
                if link:
                    st.write("**📄 Bài làm:**")
                    st.code(link, language=None)  # Hiển thị trong code block
                else:
                    st.write("**📄 Bài làm:** Chưa có link")
                
                # Feedback content
                feedback_content = feedback.get('noi_dung', '').strip()
                if feedback_content:
                    st.markdown("**💬 Feedback từ giáo viên:**")
                    st.success(feedback_content)
                else:
                    st.info("⏳ Chưa có feedback từ giáo viên")
    else:
        st.info("📭 Bạn chưa có feedback nào. Hãy nộp bài để nhận feedback từ giáo viên!")
        st.markdown("""
        **Hướng dẫn:**
        1. Hoàn thành bài tập của bạn
        2. Upload lên Google Docs 
        3. Đợi feedback xuất hiện tại đây!
        """)

def show_admin_dashboard():
    # Header
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("🔧 Admin Dashboard - Đào Việt Thanh")
        st.write(f"Quản trị viên: **{st.session_state.user_data['email']}**")
    
    with col2:
        st.write("")  # spacing
        if st.button("🚪 Đăng xuất", width='stretch'):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.username = None
            st.rerun()
    
    st.divider()
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["📊 Import Dữ liệu", "📈 Thống kê", "👥 Quản lý Users"])
    
    with tab1:
        show_import_section()
    
    with tab2:
        show_stats_section()
    
    with tab3:
        show_users_management()

def show_import_section():
    
    st.subheader("📥 Import dữ liệu từ Google Sheets")
    
    st.markdown("""
    **Hướng dẫn:**
    1. Chuẩn bị Google Sheet với các cột: Thời gian, Họ tên, Lớp, SĐT, Email, Link bài làm, Status, Feedback
    2. Share Google Sheet với service account (đã có quyền)
    3. Copy URL của Google Sheet
    4. Paste URL vào ô bên dưới và nhấn Import
    5. Lưu ý: mỗi lần nhập dữ liệu thì sẽ chỉ đọc thông tin từ tab đầu tiên trong sheet
    """)
    
    with st.form("import_form"):
        sheet_url = st.text_input(
            "🔗 URL Google Sheets", 
            placeholder="https://docs.google.com/spreadsheets/d/SHEET_ID/edit",
            help="Paste URL đầy đủ của Google Sheet"
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            submit = st.form_submit_button("🚀 Import dữ liệu", width='stretch')
        
        if submit and sheet_url:
            try:
                # Extract sheet ID from URL
                if '/d/' in sheet_url:
                    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
                else:
                    st.error("❌ URL không hợp lệ! Vui lòng kiểm tra lại.")
                    return
                
                with st.spinner("🔍 Đang kiểm tra kết nối..."):
                    # Test connection
                    if st.session_state.ggsheet_extractor.test_connection(sheet_id):
                        st.success("✅ Kết nối thành công!")
                        
                        with st.spinner("⏳ Đang import dữ liệu..."):
                            # Extract and update
                            st.session_state.ggsheet_extractor.extract_and_update_firebase(sheet_id)
                            st.success("🎉 Import thành công!")
                            st.balloons()
                    else:
                        st.error("❌ Không thể kết nối đến Google Sheets! Kiểm tra quyền truy cập.")
                        
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")

def show_stats_section():
    st.subheader("📊 Thống kê hệ thống")
    
    try:
        # Get all users from Firebase
        users_ref = st.session_state.feedback_service.firebase.db.collection('users')
        all_users = list(users_ref.stream())
        
        total_users = len(all_users)
        total_students = len([u for u in all_users if u.to_dict().get('role') == 'user'])
        total_feedbacks = sum([len(u.to_dict().get('feedbacks', [])) for u in all_users])
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👥 Tổng số người dùng", total_users)
        
        with col2:
            st.metric("🎓 Số học sinh", total_students)
        
        with col3:
            st.metric("📝 Tổng số feedback", total_feedbacks)
        
        st.divider()
            
    except Exception as e:
        st.error(f"Lỗi khi lấy thống kê: {e}")

def show_users_management():
    st.subheader("👥 Danh sách học sinh")
    
    try:
        # Get all users from Firebase
        users_ref = st.session_state.feedback_service.firebase.db.collection('users')
        all_users = list(users_ref.stream())
        
        # Filter only students (role = 'user')
        students = []
        for user_doc in all_users:
            user_data = user_doc.to_dict()
            if user_data.get('role') == 'user':
                profile = user_data.get('profile', {})
                students.append({
                    'Họ và tên': profile.get('ho_ten', 'Chưa cập nhật'),
                    'Email': user_data.get('email', 'N/A'),
                    'Số điện thoại': profile.get('phone', 'N/A'),
                    'Lớp': profile.get('lop', 'Chưa cập nhật'),
                    'Số feedback': len(user_data.get('feedbacks', []))
                })
        
        if students:
            # Convert to DataFrame
            df = pd.DataFrame(students)
            
            # Display count
            st.info(f"📋 Tổng số: **{len(students)}** học sinh")
            
            # Add search box
            search = st.text_input("🔍 Tìm kiếm", placeholder="Nhập tên, email, hoặc lớp...")
            
            # Filter dataframe based on search
            if search:
                mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                df_filtered = df[mask]
            else:
                df_filtered = df
            
            # Display dataframe
            st.dataframe(
                df_filtered,
                width='stretch',
                hide_index=True,
                column_config={
                    "Họ và tên": st.column_config.TextColumn("Họ và tên", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "Số điện thoại": st.column_config.TextColumn("SĐT", width="small"),
                    "Lớp": st.column_config.TextColumn("Lớp", width="medium"),
                    "Số feedback": st.column_config.NumberColumn("Số feedback", width="small")
                }
            )
            
            # Export to CSV option
            st.download_button(
                label="📥 Tải xuống CSV",
                data=df.to_csv(index=False).encode('utf-8-sig'),
                file_name=f"danh_sach_hoc_sinh_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        else:
            st.warning("⚠️ Chưa có học sinh nào trong hệ thống.")
            
    except Exception as e:
        st.error(f"❌ Lỗi khi tải danh sách: {e}")

if __name__ == "__main__":
    main()
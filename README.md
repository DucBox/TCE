# TCE Feedback System

Hệ thống quản lý feedback cho học sinh TCE, tích hợp Firebase và Google Sheets.

## Tính năng

- **Admin**: Import dữ liệu từ Google Sheets, quản lý feedback
- **Học sinh**: Xem feedback cá nhân, sắp xếp theo thời gian mới nhất
- **Authentication**: Đăng nhập bằng email + SĐT

## Cài đặt

### Local Development

1. **Setup môi trường**
```bash
export FIREBASE_CONFIG='{"type":"service_account",...}'
pip install -r requirements.txt
```

2. **Chạy ứng dụng**
```bash
streamlit run app.py
```

### Docker
```bash
docker build -t tce-feedback .
docker run -p 8501:8501 -e FIREBASE_CONFIG='...' tce-feedback
```
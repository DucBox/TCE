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
        emails = [
            "vietthanh.tce@gmail.com",
            "jenniethu12345@gmail.com",
            "anhthanhvip459@gmail.com",
            "nguyentruongmanh170203@gmail.com",
            "uyennguyenphuong280409@gmail.com",
            "xchautran@gmail.com",
            "ngvietchinh0503@gmail.com",
            "chillzy14iu11@gmail.com",
            "ngtanquilong@gmail.com",
            "hngthaor@gmail.com",
            "maianhdangiu1212008@gmail.com",
            "nguyenthiyenchi@gmail.com",
            "thiloan862005@gmail.com",
            "helium150209@gmail.com",
            "toanledng2019@gmail.com",
            "thquynh2008@gmail.com",
            "thucquyenvu0520@gmail.com",
            "nguyenpl20082008@gmail.com",
            "nguyenthibichnguyet08061979@gmail.com",
            "nguyenngochongphuong92@gmail.com",
            "yokai.learning@gmail.com",
            "quyendoduc2005ls@gmail.com",
            "quynhanhchristina@gmail.com",
            "thiennhi05062005@gmail.com",
            "llinhchile734@gmail.com",
            "nngocmaikhanh3008@gmail.com",
            "tocduong2k10@gmail.com",
            "truongngocanh.20.12.2008@gmail.com",
            "duychien226@gmail.com",
            "lanhkhoa267@gmail.com",
            "triduclee09@gmail.com",
            "doviet2000las@gmail.com",
            "thuhuongcutentg@gmail.com",
            "nguyenmanhbang714@gmail.com",
            "duahau.02.10.2004@gmail.com",
            "lethilananhqn@gmail.com",
            "ngocloveke115@gmail.com",
            "tranphantumy@gmail.com",
            "truhotboy12@gmail.com",
            "tranminhphuong020610@gmail.com",
            "trngocdiep129@gmail.com",
            "trnhai@gmail.com",
            "thanhhoatrinhthi@gmail.com",
            "daothixuan5505@gmail.com",
            "nghuyenn17@gmail.com",
            "capduongso1@gmail.com",
            "phamhuonggiang918@gmail.com",
            "phamthaihoa2k6@gmail.com",
            "phamlephuonglinh12345@gmail.com",
            "havy18092009@gmail.com",
            "trangcherry9903@gmail.com",
            "thuphuong12.3.1998@gmail.com",
            "vietdung8a13009@gmail.com",
            "khanhlinh86840@gmail.com",
            "truonglamgiahuy29042013@gmail.com",
            "minhphuong9631@gmail.com"
        ]

        phones = [
            "0945513426",
            "0329391581",
            "0766507383",
            "0971884627",
            "0865597229",
            "0942387699",
            "0868110492",
            "0942405985",
            "0352605493",
            "0973748443",
            "0374605910",
            "0826785488",
            "0911125209",
            "0862457811",
            "0356770624",
            "0328181208",
            "0986736382",
            "0981567781",
            "0373579209",
            "0974249642",
            "0385480246",
            "0812533222",
            "0852598527",
            "0329577330",
            "0949846569",
            "0941801866",
            "0393865840",
            "0814765879",
            "0389341912",
            "0869157480",
            "0942621034",
            "0339316605",
            "0982035205",
            "0987871209",
            "395389586",
            "0937966629",
            "0949856183",
            "0908907628",
            "0328259562",
            "0816023181",
            "0837158688",
            "0123456789",
            "0971629004",
            "0387185505",
            "0832950866",
            "0379438658",
            "0969319805",
            "0385583236",
            "0392684757",
            "0986472737",
            "0967678510",
            "0975538468",
            "0347833484",
            "0325106387",
            "0847433266",
            "0912371764",
        ]
        print(f"Debug: Tổng số email ban đầu: {len(emails)}")
        print(f"Debug: Tổng số phone ban đầu: {len(phones)}")
        
        # Track duplicates
        seen_emails = set()
        seen_phones = set()
        duplicate_emails = []
        duplicate_phones = []
        
        filtered_emails = []
        filtered_phones = []
        
        print("\n=== KIỂM TRA DUPLICATE ===")
        
        for i, (email, phone) in enumerate(zip(emails, phones), 1):
            is_dup_email = email in seen_emails
            is_dup_phone = phone in seen_phones
            
            # Print duplicate info
            if is_dup_email or is_dup_phone:
                reason = []
                if is_dup_email:
                    reason.append(f"Email trùng")
                    duplicate_emails.append(email)
                if is_dup_phone:
                    reason.append(f"Phone trùng")
                    duplicate_phones.append(phone)
                
                print(f"❌ [{i}] {email} | {phone} - {' & '.join(reason)}")
            
            # Only add if both are unique
            if not is_dup_email and not is_dup_phone:
                filtered_emails.append(email)
                filtered_phones.append(phone)
                seen_emails.add(email)
                seen_phones.add(phone)
        
        print(f"\n=== TỔNG KẾT DUPLICATE ===")
        print(f"Số email trùng: {len(duplicate_emails)}")
        print(f"Số phone trùng: {len(duplicate_phones)}")
        
        # Check for emails without phones
        if len(emails) > len(phones):
            print(f"\n⚠️  CÓ {len(emails) - len(phones)} EMAIL KHÔNG CÓ PHONE:")
            for i in range(len(phones), len(emails)):
                print(f"   - {emails[i]}")
        
        emails = filtered_emails
        phones = filtered_phones
        
        print(f"\nDebug: Tổng số phone sau khi lọc duplicate: {len(phones)}")
        print(f"Debug: Tổng số email sau khi lọc duplicate: {len(emails)}")
        
        roles = ["admin"] + ["user"] * (len(emails) - 1)
        phones = [phone.replace(" ", "") for phone in phones]
        
        created_count = 0
        failed_count = 0
        
        print("\n=== BẮT ĐẦU TẠO TÀI KHOẢN ===")
        for i, (email, phone, role) in enumerate(zip(emails, phones, roles)):
            try:
                self._create_single_account(email, phone, role)
                created_count += 1
                print(f"✅ [{i+1}/{len(emails)}] {email} ({role})")
            except Exception as e:
                failed_count += 1
                print(f"❌ [{i+1}/{len(emails)}] {email}: {e}")
        
        print(f"\nDebug: Số tài khoản tạo thành công: {created_count}")
        print(f"📊 Kết quả: {created_count} thành công, {failed_count} thất bại")
        
    def _create_single_account(self, email, phone, role):
        # Tạo user_id: chỉ lấy phần trước @ cho tất cả user
        user_id = email.split('@')[0]
        
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
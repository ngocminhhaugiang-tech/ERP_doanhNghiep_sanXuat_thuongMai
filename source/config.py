# -*- coding: utf-8 -*-
"""
config.py — Cau hinh chung cho toan bo du an sinh du lieu HPT.
"""
import random
import numpy as np
from datetime import datetime
from faker import Faker

# ==============================================================================
# 0. SEED - de chay lai ra dung bo cu (yeu cau nghiem thu: seed co dinh)
# ==============================================================================
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("vi_VN")
Faker.seed(SEED)

OUTPUT_DIR = "output"
CLEAN_SUBDIR = "00_ban_sach"     # ban SACH truoc khi gieo loi (giu lai de doi chieu tuan 8)
DIRTY_SUBDIR = "01_ban_gieo_loi"  # ban da gieo loi - dung cho cac tuan sau

# ==============================================================================
# 1. QUY MO (theo dung khung goi y PHAN 4 cua de bai, chon gia tri giua khung)
# ==============================================================================
N_KHACHHANG      = 450   # goi y 300 - 600
N_SANPHAM        = 220   # goi y 150 - 300
N_DONHANG        = 12_000  # goi y 8.000 - 15.000
N_NHANVIEN_SALES = 30    # goi y 20 - 40
N_NHACUNGCAP     = 45    # goi y 30 - 60  (gia dinh bo sung - xem ASSUMPTIONS.md)
SO_THANG_LICHSU  = 24    # dung theo goi y "24 thang"

# Cac bang phu thuoc Fact_DonHang / Fact_DonMuaHang -> quy mo suy ra hop ly
N_CHITIET_MOI_DON_MIN, N_CHITIET_MOI_DON_MAX = 1, 4   # so dong chi tiet / 1 don hang
N_DONMUAHANG     = 3_500       
# ==============================================================================
# SỐ LƯỢNG & CẤU TRÚC ĐƠN HÀNG THEO LOẠI KHÁCH (MỚI BỔ SUNG FIX BUG)
# ==============================================================================
# Khách Sỉ: Mua nhiều dòng hàng (3-8 dòng), mỗi dòng số lượng lớn (50-300 thùng/hộp)
# Khách Lẻ: Mua ít dòng hàng (1-3 dòng), mỗi dòng số lượng nhỏ (1-10 cái/hộp)
HE_SO_DON_HANG_THEO_LOAIKHACH = {
    "Sỉ": {
        "so_dong_min_max": (3, 8),
        "soluong_min_max": (50, 300)
    },
    "Lẻ": {
        "so_dong_min_max": (1, 3),
        "soluong_min_max": (1, 10)
    }
}

# ==============================================================================
# 2. KHOANG THOI GIAN DU LIEU (24 thang lich su, ket thuc gan thoi diem hien tai)
# ==============================================================================
DATE_END   = datetime(2026, 7, 31)
DATE_START = datetime(2024, 8, 1)   # DATE_END - 24 thang

# ==============================================================================
# 3. TY LE GIEO LOI (theo dung PHAN 2 cua de bai)
# ==============================================================================
# 1) Ma lech dinh dang giua he thong -> gieo o PHAN LON ban ghi (khong phai vai %)
RATE_ID_FORMAT_MISMATCH = (0.70, 0.95)
# 2) Ten khach hang viet khac nhau -> 15-20% khach hang
RATE_TEN_KHACH_LECH = (0.15, 0.20)
# 3) Ngay lech dinh dang -> vai % (dac biet o file Excel nhap tay cao hon)
RATE_NGAY_LECH          = (0.03, 0.06)
RATE_NGAY_LECH_EXCEL    = (0.10, 0.15)
# 4) Gia tri thieu (ma khach, ma san pham, ngay) -> 3-5%
RATE_MISSING = (0.03, 0.05)
# 5) Ma tham chieu khong ton tai (orphan FK) -> 2-3%
RATE_ORPHAN_FK = (0.02, 0.03)
# 6) Hai nguon gia khac nhau (gia niem yet kho vs gia ban thuc te don hang) -> 20-25% don co chenh
RATE_GIA_CHENH_LECH = (0.20, 0.25)
# 7) Don vi tinh khong thong nhat -> ap dung cho toan bo danh muc san pham (bien the)
RATE_DONVI_KHONGDONG = (0.20, 0.30)
# 8) Ban ghi trung (cung don hang nhap 2 lan, ma khac nhau) -> 1-2%
RATE_TRUNG_BAN_GHI = (0.01, 0.02)

# ==============================================================================
# 4. MA KHOA CHUAN (CLEAN KEYS) - nen cho toan bo quan he FK trong ban SACH
# ==============================================================================
KH_IDS = [f"KH{i:04d}" for i in range(1, N_KHACHHANG + 1)]
SP_IDS = [f"SP{i:04d}" for i in range(1, N_SANPHAM + 1)]
NV_IDS = [f"NV{i:02d}" for i in range(1, N_NHANVIEN_SALES + 1)]
NCC_IDS = [f"NCC{i:03d}" for i in range(1, N_NHACUNGCAP + 1)]

# ==============================================================================
# 5. DANH MUC DUNG CHUNG
# ==============================================================================
VUNG_CHUAN = ["Miền Bắc", "Miền Trung", "Miền Nam"]
VUNG_BIENTHE = {
    "Miền Bắc": ["MB", "M.Bắc", "Bắc", "North"],
    "Miền Trung": ["MT", "M.Trung", "Trung", "Central"],
    "Miền Nam": ["MN", "M.Nam", "HCM", "SG", "South"],
}

LOAI_KHACH_CHUAN = ["Sỉ", "Lẻ"]   # dung DUNG theo de bai: "loai khach: si hoac le"

KENH_BAN_CHUAN = ["TMĐT - Shopee", "TMĐT - Lazada", "TMĐT - Tiki", "Đại lý", "Bán lẻ trực tiếp", "Showroom"]
KENH_BAN_BIENTHE = {
    "TMĐT - Shopee": ["Shopee", "Sàn Shopee"],
    "TMĐT - Lazada": ["Lazada", "Sàn Lazada"],
    "Bán lẻ trực tiếp": ["Ban le", "Bán lẻ"],
}

TRANGTHAI_DONHANG_CHUAN = ["Mới", "Đang xử lý", "Đã giao", "Đã hủy", "Trả hàng"]

# --- Nhom hang & san pham (co bien thien BIEN LOI NHUAN theo nhom - PHAN 3 de bai) ---
SP_THEO_NHOM = {
    "Nguyên liệu đầu vào": ["Bột mì", "Đường tinh luyện", "Dầu ăn công nghiệp", "Muối tinh", "Hương liệu thực phẩm"],
    "Thực phẩm chế biến": ["Snack khoai tây", "Bánh quy hộp", "Mì ăn liền cao cấp", "Xúc xích tiệt trùng", "Nước sốt đóng chai"],
    "Đồ uống": ["Nước ngọt có ga", "Trà đóng chai", "Nước tăng lực", "Cà phê hòa tan"],
    "Gia dụng": ["Nồi cơm điện", "Bếp từ", "Máy xay sinh tố", "Ấm siêu tốc"],
}
# Khoang GIA NIEM YET RIENG theo tung nhom hang (VND) — KHONG dung chung 1 khoang
# cho moi san pham, vi "Bep tu" (thiet bi dien) va "Snack khoai tay" (thuc pham
# ban theo thung) co mat bang gia hoan toan khac nhau trong thuc te.
GIA_NIEMYET_THEO_NHOM = {
    "Nguyên liệu đầu vào": (15_000, 60_000),      # gia/kg nguyen lieu tho, tuong doi re
    "Thực phẩm chế biến": (80_000, 350_000),      # gia/thung snack, banh, mi, xuc xich
    "Đồ uống": (90_000, 300_000),                 # gia/thung nuoc ngot, tra, cafe
    "Gia dụng": (250_000, 1_500_000),             # gia/cai thiet bi dien gia dung
}
# Don vi tinh CHUAN rieng theo nhom (hop ly voi cach ban thuc te cua nhom do)
DONVITINH_THEO_NHOM = {
    "Nguyên liệu đầu vào": ["Kg", "Tấn"],
    "Thực phẩm chế biến": ["Thùng", "Hộp"],
    "Đồ uống": ["Thùng", "Hộp"],
    "Gia dụng": ["Cái"],
}
# Bien do BIEN LOI NHUAN theo nhom: (ty le GiaVon/GiaNiemYet thap = bien cao)
BIEN_LOINHUAN_THEO_NHOM = {
    "Nguyên liệu đầu vào": (0.82, 0.92),     # bien THAP
    "Thực phẩm chế biến": (0.45, 0.65),      # bien CAO
    "Đồ uống": (0.50, 0.68),
    "Gia dụng": (0.55, 0.72),
}
# He so mua vu THEO THANG (1-12), dung chung cho doanh thu Fact_DonHang
# Cao diem cuoi nam & dip Tet (thang 11,12,1), thap diem sau Tet (thang 2,3)
HESO_MUAVU_THEOTHANG = {
    1: 1.35, 2: 0.70, 3: 0.80, 4: 0.90, 5: 0.95, 6: 1.00,
    7: 1.00, 8: 0.95, 9: 1.00, 10: 1.10, 11: 1.30, 12: 1.55,
}

# ==============================================================================
# 5b. MO RONG THEM NGOAI DE BAI — lay cam hung tu thuc te nganh ERP thuc pham
# VN (Catch Weight, FEFO, Landed Cost, han muc cong no theo kenh...). CHI lay
# cac quy tac phu hop voi danh muc san pham HIEN TAI (hang dong goi san: bot,
# duong, dau an, snack, banh, mi, nuoc ngot, do gia dung — KHONG phai hang
# tuoi song can can truc tiep), KHONG them bang moi, chi them field/logic
# tren 13 bang da co. Xem ASSUMPTIONS.md muc 9 de biet chi tiet ly do & pham
# vi ap dung. Bo qua hoan toan Catch Weight / FEFO / Landed Cost vi khong hop
# voi danh muc san pham dang dung (hang dong goi, khong phai hang tuoi ban ky).
# ==============================================================================

# Han su dung (ngay) theo nhom hang — chi Thuc pham che bien / Do uong / Nguyen
# lieu moi co y nghia; Gia dung (thiet bi dien) khong co HSD thuc pham -> None
HANSUDUNG_NGAY_THEO_NHOM = {
    "Nguyên liệu đầu vào": (365, 730),
    "Thực phẩm chế biến": (180, 365),
    "Đồ uống": (270, 540),
    "Gia dụng": None,
}

# Han muc cong no toi da theo Loai khach (dua tinh than credit_limit cua MT/GT
# trong tai lieu, nhung ha xuong phu hop quy mo DN vua dang mo phong)
HANMUCCONGNO_THEO_LOAIKHACH = {
    "Sỉ": (200_000_000, 800_000_000),
    "Lẻ": (5_000_000, 30_000_000),
}

# Ty le hao hut kho theo thang (% tren luong NHAP trong ky) — ap cho nhom hang
# co tinh chat thuc pham/do uong (de hu, het han), Gia dung/Nguyen lieu it hao hut hon
TYLE_HAOHUT_THEO_NHOM = {
    "Nguyên liệu đầu vào": (0.002, 0.010),
    "Thực phẩm chế biến": (0.005, 0.020),
    "Đồ uống": (0.003, 0.015),
    "Gia dụng": (0.000, 0.005),
}

# He so mua vu RIENG theo nhom hang (nhan them vao he so mua vu chung theo
# thang, ap dung o muc SO LUONG tung dong chi tiet) — thuc pham che bien/do
# uong bien dong manh hon dip Tet & mua he, gia dung/nguyen lieu on dinh hon
HESO_MUAVU_THEONHOM_BONUS = {
    "Thực phẩm chế biến": {1: 1.30, 2: 0.85, 12: 1.35},   # Tet tang manh
    "Đồ uống": {5: 1.15, 6: 1.20, 7: 1.20, 8: 1.15, 1: 1.20, 12: 1.25},  # he + Tet
    "Nguyên liệu đầu vào": {},   # san xuat lien tuc quanh nam, it bien dong mua vu
    "Gia dụng": {1: 1.15, 12: 1.20},  # sam do moi dip Tet, nhe hon thuc pham
}

# Tuoi no khac nhau theo Loai khach (dua tinh than MT tra cham/GT tra nhanh)
# "Si" mua nhieu, thuong duoc goi dau cong no dai hon, de tre han hon.
# "Le" thanh toan nhanh, it tre han.
TUOI_NO_THEO_LOAIKHACH = {
    "Sỉ": {"xacsuat": [0.45, 0.20, 0.15, 0.12, 0.08], "han_ngay": (45, 90)},
    "Lẻ": {"xacsuat": [0.85, 0.08, 0.04, 0.02, 0.01], "han_ngay": (7, 15)},
}

DONVITINH_CHUAN = ["Thùng", "Hộp", "Kg", "Tấn", "Cái"]
# Bien the don vi khong thong nhat theo dung vi du de bai: thung/hop, kg/tan lan lon
DONVITINH_BIENTHE = {
    "Thùng": ["Hộp", "thùng"],
    "Kg": ["Tấn", "kg"],
    "Cái": ["cái", "Chiếc"],
}

KHOANMUC_CHIPHI = ["Lương nhân viên", "Thuê mặt bằng", "Marketing", "Vận chuyển",
                    "Điện nước văn phòng", "Khấu hao thiết bị", "Chi phí khác"]

NHOM_KHACH_EXCEL = ["VIP", "Thân thiết", "Thường", "Mới", "Tiềm năng"]

# --- Ho / ten cho nguoi Viet (dung sinh ten khach le, nhan vien...) ----------
VN_HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Ngô", "Dương", "Lý"]
VN_TENDEM_NAM = ["Văn", "Hữu", "Đức", "Công", "Quốc", "Ngọc", "Xuân", "Minh"]
VN_TENDEM_NU = ["Thị", "Ngọc", "Thu", "Kim", "Bích", "Diễm"]
VN_TEN_NAM = ["An", "Bình", "Cường", "Dũng", "Hùng", "Khánh", "Long", "Nam", "Phong", "Sơn", "Tuấn", "Việt", "Hải", "Đạt"]
VN_TEN_NU = ["Anh", "Hoa", "Hương", "Lan", "Linh", "Mai", "Nga", "Nhung", "Phương", "Thảo", "Trang", "Yến", "Huyền"]

VN_COMPANY_SUFFIX = ["Công ty TNHH", "Công ty Cổ phần", "Công ty TNHH MTV", "Doanh nghiệp tư nhân"]
VN_COMPANY_BRAND = ["Thành Đạt", "Phú Gia", "Hưng Thịnh", "Minh Phát", "Đại Dương", "Việt Phát",
                     "An Khang", "Kim Long", "Sao Việt", "Tân Á", "Hoàng Gia", "Thiên Phú",
                     "Đông Á", "Toàn Cầu", "Việt Thắng", "Tân Phát"]
VN_COMPANY_NGANH = ["Thương mại", "Xây dựng", "Dịch vụ", "Xuất nhập khẩu", "Thực phẩm", "Phân phối"]

CHUCVU_SALES_CHUAN = ["Nhân viên Kinh doanh", "Trưởng nhóm Kinh doanh", "Giám sát Kinh doanh", "Senior Sales"]

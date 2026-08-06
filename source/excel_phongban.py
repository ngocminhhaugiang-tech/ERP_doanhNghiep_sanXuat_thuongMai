# -*- coding: utf-8 -*-
"""
excel_phongban.py — PHAN 4: File Excel do phong ban tu nhap
Bang: Fact_ChiTieuKeHoach, Dim_NhanVienSales, Dim_PhanNhomKhachHang
"""
import random
import numpy as np
import pandas as pd

import config as cfg
import utils as u

RATE_EXCEL_ID_MISS = (0.80, 0.98)   # gan nhu toan bo ban ghi (Excel nhap tay)
RATE_EXCEL_TEN_LECH = (0.30, 0.45)  # "ban" hon nhieu so voi Dim_KhachHang goc


# ==============================================================================
# Dim_NhanVienSales
# ==============================================================================
def gen_dim_nhanviensales_clean():
    n = cfg.N_NHANVIEN_SALES
    ten = [u.gen_vn_person_name() for _ in range(n)]
    khuvuc = [random.choice(cfg.VUNG_CHUAN) for _ in range(n)]
    chucvu = [random.choice(cfg.CHUCVU_SALES_CHUAN) for _ in range(n)]
    ngayvao = [u.random_date(cfg.DATE_START - pd.Timedelta(days=1000), cfg.DATE_START) for _ in range(n)]

    df = pd.DataFrame({
        "MaNhanVien": cfg.NV_IDS.copy(), "TenNhanVien": ten,
        "KhuVucPhuTrach": khuvuc, "ChucVu": chucvu, "NgayVaoLam": ngayvao,
    })
    return df


def gen_dim_nhanviensales_dirty(df_clean):
    df = df_clean.copy()
    df["MaNhanVien"] = u.inject_id_format_mismatch(df["MaNhanVien"], "excel", "Dim_NhanVienSales", "MaNhanVien",
                                                     rng=RATE_EXCEL_ID_MISS)
    df["TenNhanVien"] = u.inject_ten_khach_lech(df["TenNhanVien"], bang="Dim_NhanVienSales", cot="TenNhanVien",
                                                 rng=RATE_EXCEL_TEN_LECH)
    df["KhuVucPhuTrach"] = u.inject_categorical_variants(
        df["KhuVucPhuTrach"], cfg.VUNG_BIENTHE, "Dim_NhanVienSales", "KhuVucPhuTrach",
        "Ma vung viet tat khong dong nhat", rng=(0.20, 0.30))
    df["ChucVu"] = u.inject_missing(df["ChucVu"], "Dim_NhanVienSales", "ChucVu")
    df["NgayVaoLam"] = u.messy_date_series(df["NgayVaoLam"], "Dim_NhanVienSales", "NgayVaoLam",
                                            rng=cfg.RATE_NGAY_LECH_EXCEL)
    return df


# ==============================================================================
# Fact_ChiTieuKeHoach (theo thang, vung, nhan vien — PHAN 3: thuc hien vs ke hoach phai co chenh)
# ==============================================================================
def _doanh_thu_thuc_te_theo_vung_thang(fact_donhang_clean, fact_chitiet_clean, dim_khachhang_clean):
    ct = fact_chitiet_clean.copy()
    ct["ThanhTien"] = ct["SoLuong"] * ct["GiaBanThucTe"] * (1 - ct["ChietKhau"])
    dt_don = ct.groupby("MaDonHang")["ThanhTien"].sum().rename("ThanhTien")
    dh = fact_donhang_clean.merge(dt_don, on="MaDonHang", how="inner")
    dh = dh.merge(dim_khachhang_clean[["MaKhachHang", "Vung"]], on="MaKhachHang", how="left")
    dh["Thang"] = pd.to_datetime(dh["NgayDatHang"]).dt.to_period("M").dt.to_timestamp()
    return dh.groupby(["Thang", "Vung"])["ThanhTien"].sum().rename("DoanhThuThucTe").reset_index()


def gen_fact_chitieukehoach_clean(fact_donhang_clean, fact_chitiet_clean, dim_khachhang_clean,
                                   dim_nhanviensales_clean):
    dt_vung_thang = _doanh_thu_thuc_te_theo_vung_thang(fact_donhang_clean, fact_chitiet_clean, dim_khachhang_clean)

    # PHAN 3 de bai: "co vung vuot ke hoach, co vung khong dat" -> he so co dinh theo vung
    he_so_vung = {"Miền Bắc": 0.85, "Miền Trung": 1.20, "Miền Nam": 0.95}  # <1 = de vuot, >1 = kho dat

    # Thuc te KHONG chia deu chi tieu cho moi nhan vien trong cung vung/thang:
    # nhan vien Giam sat/Truong nhom thuong duoc giao chi tieu cao hon Nhan vien
    # thuong, va nang luc/tham nien tung ca nhan cung khac nhau. Sinh 1 "he so
    # nang luc ca nhan" ON DINH cho tung nhan vien (dung xuyen suot 24 thang,
    # giong nhu 1 nguoi gioi thi thang nao cung duoc giao chi tieu cao hon).
    HE_SO_CHUCVU = {
        "Nhân viên Kinh doanh": 1.00,
        "Senior Sales": 1.15,
        "Trưởng nhóm Kinh doanh": 1.35,
        "Giám sát Kinh doanh": 1.50,
    }
    he_so_ca_nhan = {}
    for _, r in dim_nhanviensales_clean.iterrows():
        base = HE_SO_CHUCVU.get(r["ChucVu"], 1.00)
        he_so_ca_nhan[r["MaNhanVien"]] = base * random.uniform(0.85, 1.15)

    rows = []
    for _, r in dt_vung_thang.iterrows():
        vung, thang, dtt = r["Vung"], r["Thang"], r["DoanhThuThucTe"]
        if pd.isna(vung):
            continue
        nv_vung = dim_nhanviensales_clean[dim_nhanviensales_clean["KhuVucPhuTrach"] == vung]["MaNhanVien"].tolist()
        if not nv_vung:
            continue
        target_vung = dtt * he_so_vung.get(vung, 1.0) * random.uniform(0.92, 1.08)

        # Phan bo target_vung cho tung nhan vien THEO TY LE he so nang luc ca
        # nhan (khong chia deu), cong them chut nhieu rieng theo thang de
        # khong "dong cung" tuyet doi qua 24 thang.
        trong_so = {nv: he_so_ca_nhan[nv] * random.uniform(0.95, 1.05) for nv in nv_vung}
        tong_trong_so = sum(trong_so.values())
        for nv in nv_vung:
            target_moi_nv = target_vung * (trong_so[nv] / tong_trong_so)
            rows.append({
                "Thang": thang, "Vung": vung, "MaNhanVien": nv,
                "ChiTieuDoanhThu": round(target_moi_nv, -3),
            })
    return pd.DataFrame(rows)


def gen_fact_chitieukehoach_dirty(df_clean):
    df = df_clean.copy()
    df["MaNhanVien"] = u.inject_id_format_mismatch(df["MaNhanVien"], "excel", "Fact_ChiTieuKeHoach", "MaNhanVien",
                                                     rng=RATE_EXCEL_ID_MISS)
    df["MaNhanVien"] = u.inject_orphan_fk(
        df["MaNhanVien"], u.make_orphan_pool("NV", n=8, start=90),
        "Fact_ChiTieuKeHoach", "MaNhanVien")
    df["Vung"] = u.inject_categorical_variants(
        df["Vung"], cfg.VUNG_BIENTHE, "Fact_ChiTieuKeHoach", "Vung",
        "Ma vung viet tat khong dong nhat", rng=(0.25, 0.35))
    # Thang: "rat hay loi" o file Excel -> nhieu bien the dinh dang, ty le cao
    n = len(df)
    mask, ty_le = u.rate_mask(n, cfg.RATE_NGAY_LECH_EXCEL)
    idx = np.where(mask)[0]
    thang_moi = df["Thang"].astype(object).copy()
    for i in idx:
        d = df["Thang"].iat[i]
        fmt = random.choice(["%m/%Y", "Tháng %m/%Y", "%b-%y"])
        thang_moi.iat[i] = pd.Timestamp(d).strftime(fmt)
    thang_moi.loc[~thang_moi.index.isin(idx)] = df["Thang"].loc[~thang_moi.index.isin(idx)].apply(
        lambda d: pd.Timestamp(d).strftime("%Y-%m"))
    df["Thang"] = thang_moi
    u.log_error("Ngay lech dinh dang", "Fact_ChiTieuKeHoach", "Thang", ty_le,
                f"{len(idx)}/{n} dong bi doi dinh dang thang (m/yyyy, 'Tháng m/yyyy', mon-yy).",
                so_dong_anh_huong=len(idx))
    df["ChiTieuDoanhThu"] = u.inject_missing(df["ChiTieuDoanhThu"], "Fact_ChiTieuKeHoach", "ChiTieuDoanhThu",
                                              rng=(0.02, 0.04))
    return df


# ==============================================================================
# Dim_PhanNhomKhachHang — bang phong kinh doanh TU DUY TRI, nguon "ban" nhat
# ==============================================================================
def gen_dim_phannhomkhachhang_clean(dim_khachhang_clean):
    # phong KD chi cap nhat MOT PHAN khach hang (khong day du 100%), khoang 70-90%
    n_full = len(dim_khachhang_clean)
    ty_le_bao_phu = random.uniform(0.70, 0.90)
    df = dim_khachhang_clean.sample(frac=ty_le_bao_phu, random_state=cfg.SEED)[
        ["MaKhachHang", "TenKhachHang"]].copy().reset_index(drop=True)
    df["NhomKH"] = [random.choice(cfg.NHOM_KHACH_EXCEL) for _ in range(len(df))]
    u.log_error("Danh muc khong day du (do nguoi nhap tay bo sot)", "Dim_PhanNhomKhachHang",
                "MaKhachHang", 1 - ty_le_bao_phu,
                f"Bang chi bao phu {ty_le_bao_phu:.0%} tong so khach hang trong Dim_KhachHang "
                f"vi phong kinh doanh tu cap nhat tay, khong dong bo tu dong.",
                so_dong_anh_huong=n_full - len(df))
    return df


def gen_dim_phannhomkhachhang_dirty(df_clean):
    df = df_clean.copy()
    # Excel tu nhap -> gan nhu toan bo ma bi doi dinh dang (dau gach ngang, khoang trang, thuong)
    df["MaKhachHang"] = u.inject_id_format_mismatch(df["MaKhachHang"], "excel",
                                                      "Dim_PhanNhomKhachHang", "MaKhachHang",
                                                      rng=RATE_EXCEL_ID_MISS)
    # Ten ghi tay lai tu dau -> lech nhieu hon ban goc (30-45%)
    df["TenKhachHang"] = u.inject_ten_khach_lech(df["TenKhachHang"], bang="Dim_PhanNhomKhachHang",
                                                  cot="TenKhachHang", rng=RATE_EXCEL_TEN_LECH)
    df["NhomKH"] = u.inject_missing(df["NhomKH"], "Dim_PhanNhomKhachHang", "NhomKH", rng=(0.05, 0.08))
    df = u.inject_duplicate_rows(df, "MaKhachHang", "Dim_PhanNhomKhachHang",
                                  rate_rng=(0.02, 0.04), sinh_ma_moi=False)
    return df

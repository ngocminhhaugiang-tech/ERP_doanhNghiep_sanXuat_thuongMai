# -*- coding: utf-8 -*-
"""
hethong_ketoan.py — PHAN 2: He thong ke toan
Bang: Fact_HoaDonCongNoPhaiThu, Fact_CongNoPhaiTra, Fact_ChiPhi, Dim_GiaVon
"""
import random
import numpy as np
import pandas as pd

import config as cfg
import utils as u

# PHAN 3 de bai: "Cong no phai co tuoi no da dang" -> 5 nhom tuoi no
TUOI_NO_BUCKETS = ["dung_han", "qua_han_30", "qua_han_60", "qua_han_90", "no_kho_doi_180"]
TUOI_NO_XACSUAT = [0.55, 0.18, 0.12, 0.08, 0.07]
TUOI_NO_DATHU_RANGE = {
    "dung_han": (1.0, 1.0),
    "qua_han_30": (0.60, 1.00),
    "qua_han_60": (0.30, 0.80),
    "qua_han_90": (0.10, 0.50),
    "no_kho_doi_180": (0.0, 0.20),
}
TUOI_NO_SOHAN_NGAY = {
    "dung_han": 30, "qua_han_30": 30, "qua_han_60": 60, "qua_han_90": 90, "no_kho_doi_180": 180,
}


def _tinh_doanh_thu_theo_don(fact_donhang_clean, fact_chitiet_clean):
    ct = fact_chitiet_clean.copy()
    ct["ThanhTien"] = ct["SoLuong"] * ct["GiaBanThucTe"] * (1 - ct["ChietKhau"])
    doanh_thu = ct.groupby("MaDonHang")["ThanhTien"].sum().rename("SoTien")
    df = fact_donhang_clean.merge(doanh_thu, on="MaDonHang", how="inner")
    return df[df["TrangThai"] != "Đã hủy"].reset_index(drop=True)


# ==============================================================================
# Fact_HoaDonCongNoPhaiThu
# ==============================================================================
def gen_fact_congnophaithu_clean(fact_donhang_clean, fact_chitiet_clean, dim_khachhang_clean):
    dh = _tinh_doanh_thu_theo_don(fact_donhang_clean, fact_chitiet_clean)
    # THEM NGOAI DE BAI (xem ASSUMPTIONS.md muc 9): tuoi no + han thanh toan
    # khac nhau ro theo Loai khach thay vi dung chung 1 phan bo cho moi khach
    dh = dh.merge(dim_khachhang_clean[["MaKhachHang", "LoaiKhach"]], on="MaKhachHang", how="left")
    n = len(dh)

    rows = []
    for i, (_, r) in enumerate(dh.iterrows()):
        loai_khach = r["LoaiKhach"] if pd.notna(r["LoaiKhach"]) else "Lẻ"
        cau_hinh = cfg.TUOI_NO_THEO_LOAIKHACH.get(loai_khach, cfg.TUOI_NO_THEO_LOAIKHACH["Lẻ"])
        bucket = np.random.choice(TUOI_NO_BUCKETS, p=cau_hinh["xacsuat"])
        ngay_xuat = pd.Timestamp(r["NgayDatHang"]) + pd.Timedelta(days=random.randint(0, 3))
        so_ngay_han = random.randint(*cau_hinh["han_ngay"])
        han = ngay_xuat + pd.Timedelta(days=so_ngay_han)
        so_tien = round(r["SoTien"], -2)
        lo, hi = TUOI_NO_DATHU_RANGE[bucket]
        da_thu = round(so_tien * random.uniform(lo, hi), -2)
        con_lai = round(so_tien - da_thu, -2)
        rows.append({
            "MaHoaDon": f"HD{str(i + 1).zfill(6)}",
            "MaDonHang": r["MaDonHang"],
            "NgayXuatHoaDon": ngay_xuat,
            "HanThanhToan": han,
            "SoTien": so_tien,
            "DaThu": da_thu,
            "ConLai": con_lai,
        })
    return pd.DataFrame(rows)


def gen_fact_congnophaithu_dirty(df_clean):
    df = df_clean.copy()
    df["MaHoaDon"] = u.inject_id_format_mismatch(df["MaHoaDon"], "ketoan", "Fact_CongNoPhaiThu", "MaHoaDon")
    df["MaDonHang"] = u.inject_id_format_mismatch(df["MaDonHang"], "ketoan", "Fact_CongNoPhaiThu", "MaDonHang")
    df["MaDonHang"] = u.inject_orphan_fk(
        df["MaDonHang"], u.make_orphan_pool("DH", n=10, start=900000),
        "Fact_CongNoPhaiThu", "MaDonHang")
    df["NgayXuatHoaDon"] = u.messy_date_series(df["NgayXuatHoaDon"], "Fact_CongNoPhaiThu", "NgayXuatHoaDon")
    df["HanThanhToan"] = u.messy_date_series(df["HanThanhToan"], "Fact_CongNoPhaiThu", "HanThanhToan")
    df["MaDonHang"] = u.inject_missing(df["MaDonHang"], "Fact_CongNoPhaiThu", "MaDonHang")
    return df


# ==============================================================================
# Fact_CongNoPhaiTra
# ==============================================================================
def gen_fact_congnophaitra_clean(fact_donmuahang_clean):
    n = len(fact_donmuahang_clean)
    buckets = list(np.random.choice(TUOI_NO_BUCKETS, size=n, p=TUOI_NO_XACSUAT))

    rows = []
    for i, (_, r) in enumerate(fact_donmuahang_clean.iterrows()):
        bucket = buckets[i]
        ngay_hd = pd.Timestamp(r["NgayDatHang"]) + pd.Timedelta(days=random.randint(1, 5))
        han = ngay_hd + pd.Timedelta(days=45)
        so_tien = round(r["SoLuong"] * r["DonGiaMua"], -2)
        lo, hi = TUOI_NO_DATHU_RANGE[bucket]
        da_tra = round(so_tien * random.uniform(lo, hi), -2)
        con_lai = round(so_tien - da_tra, -2)
        rows.append({
            "MaCongNoPhaiTra": f"CNT{str(i + 1).zfill(6)}",
            "MaDonMuaHang": r["MaDonMuaHang"],
            "MaNhaCungCap": r["MaNhaCungCap"],
            "NgayHoaDon": ngay_hd,
            "HanThanhToan": han,
            "SoTien": so_tien,
            "DaTra": da_tra,
            "ConLai": con_lai,
        })
    return pd.DataFrame(rows)


def gen_fact_congnophaitra_dirty(df_clean):
    df = df_clean.copy()
    df["MaCongNoPhaiTra"] = u.inject_id_format_mismatch(df["MaCongNoPhaiTra"], "ketoan", "Fact_CongNoPhaiTra", "MaCongNoPhaiTra")
    df["MaDonMuaHang"] = u.inject_id_format_mismatch(df["MaDonMuaHang"], "ketoan", "Fact_CongNoPhaiTra", "MaDonMuaHang")
    df["MaNhaCungCap"] = u.inject_id_format_mismatch(df["MaNhaCungCap"], "ketoan", "Fact_CongNoPhaiTra", "MaNhaCungCap")
    df["MaNhaCungCap"] = u.inject_orphan_fk(
        df["MaNhaCungCap"], u.make_orphan_pool("NCC", n=8, start=900),
        "Fact_CongNoPhaiTra", "MaNhaCungCap")
    df["NgayHoaDon"] = u.messy_date_series(df["NgayHoaDon"], "Fact_CongNoPhaiTra", "NgayHoaDon")
    return df


# ==============================================================================
# Fact_ChiPhi (theo khoan muc va theo thang)
# ==============================================================================
def gen_fact_chiphi_clean(fact_donhang_clean, fact_chitiet_clean):
    """
    QUAN TRONG: Chi phi tinh theo % DOANH THU TRUNG BINH/THANG (khong dung so
    VND tuyet doi co dinh nhu truoc) -> tu dong co gian dung ty le khi quy mo
    cong ty thay doi (vd doi khoang GiaNiemYet), khong bi lech ty le Chi phi/
    Doanh thu moi lan chinh gia san pham nhu truoc day.
    """
    ct = fact_chitiet_clean.copy()
    ct["ThanhTien"] = ct["SoLuong"] * ct["GiaBanThucTe"] * (1 - ct["ChietKhau"])
    doanh_thu_tong = fact_donhang_clean.merge(
        ct.groupby("MaDonHang")["ThanhTien"].sum(), on="MaDonHang", how="inner")["ThanhTien"].sum()
    doanh_thu_tb_thang = doanh_thu_tong / cfg.SO_THANG_LICHSU

    # Ty le % DOANH THU TRUNG BINH/THANG cho tung khoan muc (tong ~15-18% doanh thu,
    # muc hop ly cho chi phi van hanh SG&A cua DN thuong mai vua, CHUA tinh gia von)
    TY_LE_THEO_DOANHTHU = {
        "Lương nhân viên": (0.060, 0.090),
        "Thuê mặt bằng": (0.015, 0.025),
        "Marketing": (0.010, 0.045),         # bien dong theo mua vu ben duoi
        "Vận chuyển": (0.010, 0.035),        # bien dong theo mua vu ben duoi
        "Điện nước văn phòng": (0.0010, 0.0020),
        "Khấu hao thiết bị": (0.0020, 0.0040),
        "Chi phí khác": (0.0005, 0.0030),
    }

    thangs = u.thang_list()
    rows = []
    stt = 1
    for th in thangs:
        for km, (lo, hi) in TY_LE_THEO_DOANHTHU.items():
            so_tien = round(doanh_thu_tb_thang * random.uniform(lo, hi), -3)
            # Marketing/Van chuyen tang theo mua vu cung doanh thu
            if km in ("Marketing", "Vận chuyển"):
                so_tien = round(so_tien * cfg.HESO_MUAVU_THEOTHANG[th.month], -3)
            rows.append({"MaChiPhi": f"CP{str(stt).zfill(5)}", "Thang": th, "KhoanMuc": km, "SoTien": so_tien})
            stt += 1
    return pd.DataFrame(rows)


def gen_fact_chiphi_dirty(df_clean):
    df = df_clean.copy()
    df["Thang"] = u.messy_date_series(df["Thang"], "Fact_ChiPhi", "Thang", rng=cfg.RATE_NGAY_LECH_EXCEL) \
        .apply(lambda x: x[:7] if isinstance(x, str) and len(x) >= 7 and x[4] == "-" else x)
    df["MaChiPhi"] = u.inject_id_format_mismatch(df["MaChiPhi"], "ketoan", "Fact_ChiPhi", "MaChiPhi")
    df["KhoanMuc"] = u.inject_missing(df["KhoanMuc"], "Fact_ChiPhi", "KhoanMuc", rng=(0.01, 0.02))
    return df


# ==============================================================================
# Dim_GiaVon (bien loi nhuan khac nhau theo nhom hang — PHAN 3 de bai)
# ==============================================================================
def gen_dim_giavon_clean(dim_sanpham_clean):
    rows = []
    for _, sp in dim_sanpham_clean.iterrows():
        lo, hi = cfg.BIEN_LOINHUAN_THEO_NHOM[sp["NhomHang"]]
        giavon = round(sp["GiaNiemYet"] * random.uniform(lo, hi), -2)
        rows.append({"MaSanPham": sp["MaSanPham"], "GiaVon": giavon})
    return pd.DataFrame(rows)


def gen_dim_giavon_dirty(df_clean):
    df = df_clean.copy()
    df["MaSanPham"] = u.inject_id_format_mismatch(df["MaSanPham"], "ketoan", "Dim_GiaVon", "MaSanPham")
    df["MaSanPham"] = u.inject_orphan_fk(
        df["MaSanPham"], u.make_orphan_pool("SP", n=8, start=9700),
        "Dim_GiaVon", "MaSanPham")
    return df

# -*- coding: utf-8 -*-
"""
hethong_banhang.py — PHAN 1: He thong ban hang
Bang: Dim_KhachHang, Fact_DonHang, Fact_ChiTietDonHang
(dung DUNG cac truong de bai yeu cau muc C12)
"""
import random
import numpy as np
import pandas as pd

import config as cfg
import utils as u


# ==============================================================================
# Dim_KhachHang
# ==============================================================================
def gen_dim_khachhang_clean():
    n = cfg.N_KHACHHANG
    loai_khach = [random.choice(cfg.LOAI_KHACH_CHUAN) for _ in range(n)]
    ten = [u.gen_vn_person_name() if lk == "Lẻ" else u.gen_vn_company_name() for lk in loai_khach]
    vung = [random.choice(cfg.VUNG_CHUAN) for _ in range(n)]
    ngay_bd = [u.random_date(cfg.DATE_START - pd.Timedelta(days=730), cfg.DATE_START)
               for _ in range(n)]  # co the la khach cu tu truoc ky du lieu

    # THEM NGOAI DE BAI (xem ASSUMPTIONS.md muc 9): Han muc cong no toi da,
    # khac nhau ro theo Loai khach (Si duoc cap han muc cao hon Le nhieu)
    hanmuc = [round(random.uniform(*cfg.HANMUCCONGNO_THEO_LOAIKHACH[lk]), -6) for lk in loai_khach]

    df = pd.DataFrame({
        "MaKhachHang": cfg.KH_IDS.copy(),
        "TenKhachHang": ten,
        "Vung": vung,
        "LoaiKhach": loai_khach,
        "NgayBatDauGiaoDich": ngay_bd,
        "HanMucCongNo": hanmuc,
    })

    # PHAN 3 de bai: "Phan bo khach hang khong deu" -> trong so Pareto cho tung khach
    # (chi dung noi bo de sinh Fact_DonHang, KHONG dua vao bang giao nop)
    weights = np.random.pareto(a=1.4, size=n) + 0.15
    weights = weights / weights.sum()
    return df, weights


def recalibrate_han_muc_congno(dim_khachhang_clean, fact_donhang_clean, fact_chitiet_clean):
    """
    THEM NGOAI DE BAI: hieu chinh lai HanMucCongNo SAU KHI da biet hanh vi mua
    hang THAT SU cua tung khach hang, thay vi random doc lap TRUOC KHI co don
    hang nao (nhu ban dau) -> tranh tinh trang han muc qua thap/cao bat thuong
    so voi quy mo mua that (vd khach Si mua hang trieu/thang nhung han muc chi
    vai tram trieu). HanMucCongNo = 2.5 - 5 thang DOANH THU TRUNG BINH cua
    CHINH khach hang do, dam bao ty le luon nam trong nguong hop ly ~10-20%
    khach vuot han muc (rui ro cong no that su, khong phai loi thiet ke).
    """
    ct = fact_chitiet_clean.copy()
    ct["ThanhTien"] = ct["SoLuong"] * ct["GiaBanThucTe"] * (1 - ct["ChietKhau"])
    doanhthu_theo_don = fact_donhang_clean.merge(
        ct.groupby("MaDonHang")["ThanhTien"].sum(), on="MaDonHang", how="inner")
    doanhthu_tb_thang_theo_kh = (
        doanhthu_theo_don.groupby("MaKhachHang")["ThanhTien"].sum() / cfg.SO_THANG_LICHSU)

    df = dim_khachhang_clean.copy()
    han_muc_moi = []
    for _, r in df.iterrows():
        lo, hi = cfg.HANMUCCONGNO_THEO_LOAIKHACH[r["LoaiKhach"]]
        dtt = doanhthu_tb_thang_theo_kh.get(r["MaKhachHang"], 0)
        if dtt <= 0:
            han_muc_moi.append(round(random.uniform(lo, hi), -6))
        else:
            # Khong thap hon san toi thieu theo Loai khach, tranh lam tron ve 0
            # voi khach doanh thu qua nho (dtt * 2.5-5.0 co the < 1 trieu)
            han_muc_moi.append(round(max(dtt * random.uniform(2.5, 5.0), lo), -6))
    df["HanMucCongNo"] = han_muc_moi
    return df


def gen_dim_khachhang_dirty(df_clean):
    df = df_clean.copy()
    df["MaKhachHang"] = u.inject_id_format_mismatch(df["MaKhachHang"], "sales", "Dim_KhachHang", "MaKhachHang")
    df["TenKhachHang"] = u.inject_ten_khach_lech(df["TenKhachHang"])
    df["Vung"] = u.inject_categorical_variants(
        df["Vung"], cfg.VUNG_BIENTHE, "Dim_KhachHang", "Vung",
        "Ma vung viet tat khong dong nhat", rng=(0.10, 0.15))
    df["NgayBatDauGiaoDich"] = u.messy_date_series(df["NgayBatDauGiaoDich"], "Dim_KhachHang", "NgayBatDauGiaoDich")
    df["MaKhachHang"] = u.inject_missing(df["MaKhachHang"], "Dim_KhachHang", "MaKhachHang", protect=None)
    return df


# ==============================================================================
# Fact_DonHang
# ==============================================================================
def _sample_ngay_theo_muavu(n_thang=cfg.SO_THANG_LICHSU):
    """Sinh 1 ngay dat hang co trong so mua vu theo thang (PHAN 3: tinh mua vu)."""
    thangs = u.thang_list(n_thang)
    ws = np.array([cfg.HESO_MUAVU_THEOTHANG[t.month] for t in thangs], dtype=float)
    ws = ws / ws.sum()
    th = np.random.choice(thangs, p=ws)
    th = pd.Timestamp(th)
    ngay_cuoi_thang = (th + pd.offsets.MonthEnd(0)).day
    ngay = random.randint(1, ngay_cuoi_thang)
    gio = random.randint(0, 23); phut = random.randint(0, 59)
    return th.replace(day=ngay, hour=gio, minute=phut)


def gen_fact_donhang_clean(kh_weights):
    n = cfg.N_DONHANG
    ma = [f"DH{str(i).zfill(6)}" for i in range(1, n + 1)]
    ma_khach = list(np.random.choice(cfg.KH_IDS, size=n, p=kh_weights))  # phan bo Pareto
    ngay = [_sample_ngay_theo_muavu() for _ in range(n)]
    kenh = [random.choice(cfg.KENH_BAN_CHUAN) for _ in range(n)]
    nv = [random.choice(cfg.NV_IDS) for _ in range(n)]
    trang_thai = list(np.random.choice(
        cfg.TRANGTHAI_DONHANG_CHUAN, size=n, p=[0.05, 0.10, 0.75, 0.06, 0.04]))

    df = pd.DataFrame({
        "MaDonHang": ma, "MaKhachHang": ma_khach, "NgayDatHang": ngay,
        "KenhBan": kenh, "NhanVienBanHang": nv, "TrangThai": trang_thai,
    })
    df = df.sort_values("NgayDatHang").reset_index(drop=True)
    return df


def gen_fact_donhang_dirty(df_clean):
    df = df_clean.copy()
    n = len(df)

    # loai lech #8: ban ghi trung (truoc khi gieo cac loi khac de ID goc con nguyen ven)
    df = u.inject_duplicate_rows(df, "MaDonHang", "Fact_DonHang")
    n = len(df)

    df["MaDonHang"] = u.inject_id_format_mismatch(df["MaDonHang"], "sales", "Fact_DonHang", "MaDonHang")
    df["MaKhachHang"] = u.inject_id_format_mismatch(df["MaKhachHang"], "sales", "Fact_DonHang", "MaKhachHang")
    # loai lech #5: 1 phan MaKhachHang tro toi khach khong ton tai
    df["MaKhachHang"] = u.inject_orphan_fk(
        df["MaKhachHang"], u.make_orphan_pool("KH", n=15, start=9000),
        "Fact_DonHang", "MaKhachHang")
    # loai lech #4: gia tri thieu o ma khach / ngay
    df["MaKhachHang"] = u.inject_missing(df["MaKhachHang"], "Fact_DonHang", "MaKhachHang")
    df["NgayDatHang"] = u.messy_date_series(df["NgayDatHang"], "Fact_DonHang", "NgayDatHang", as_datetime=True)
    df["KenhBan"] = u.inject_categorical_variants(
        df["KenhBan"], cfg.KENH_BAN_BIENTHE, "Fact_DonHang", "KenhBan",
        "Ten kenh ban viet tat khong dong nhat", rng=cfg.RATE_ID_FORMAT_MISMATCH)
    df["NhanVienBanHang"] = u.inject_id_format_mismatch(
        df["NhanVienBanHang"], "sales", "Fact_DonHang", "NhanVienBanHang")
    return df


# ==============================================================================
# Fact_ChiTietDonHang
# ==============================================================================
def gen_fact_chitietdonhang_clean(fact_donhang_clean, dim_sanpham_clean, dim_khachhang_clean):
    rows = []
    sp_ids = dim_sanpham_clean["MaSanPham"].tolist()
    gia_niem_yet_map = dict(zip(dim_sanpham_clean["MaSanPham"], dim_sanpham_clean["GiaNiemYet"]))
    nhom_map = dict(zip(dim_sanpham_clean["MaSanPham"], dim_sanpham_clean["NhomHang"]))

    # 1. Tạo dict tra cứu LoaiKhach từ MaKhachHang
    loai_khach_map = dict(zip(dim_khachhang_clean["MaKhachHang"], dim_khachhang_clean["LoaiKhach"]))

    stt = 1
    for _, don in fact_donhang_clean.iterrows():
        thang_don = pd.Timestamp(don["NgayDatHang"]).month
        
        # 2. Lấy loại khách của đơn hàng này (mặc định là "Lẻ" nếu không tìm thấy)
        loai_khach = loai_khach_map.get(don["MaKhachHang"], "Lẻ")
        cfg_khach = cfg.HE_SO_DON_HANG_THEO_LOAIKHACH.get(loai_khach, cfg.HE_SO_DON_HANG_THEO_LOAIKHACH["Lẻ"])

        # 3. Sinh số lượng dòng hàng theo loại khách
        min_dong, max_dong = cfg_khach["so_dong_min_max"]
        so_dong = random.randint(min_dong, max_dong)
        sp_chon = random.sample(sp_ids, min(so_dong, len(sp_ids)))

        for sp in sp_chon:
            heso_nhom = cfg.HESO_MUAVU_THEONHOM_BONUS.get(nhom_map[sp], {}).get(thang_don, 1.0)
            
            # 4. Sinh số lượng sản phẩm theo loại khách
            min_sl, max_sl = cfg_khach["soluong_min_max"]
            base_soluong = random.randint(min_sl, max_sl)
            soluong = max(1, int(round(base_soluong * heso_nhom)))

            gia_ban = gia_niem_yet_map[sp]
            chietkhau = round(random.choice([0, 0, 0, 0.05, 0.10, 0.15]), 2)
            
            rows.append({
                "MaChiTiet": f"CT{str(stt).zfill(7)}",
                "MaDonHang": don["MaDonHang"],
                "MaSanPham": sp,
                "SoLuong": soluong,
                "GiaBanThucTe": gia_ban,
                "ChietKhau": chietkhau,
            })
            stt += 1
            
    return pd.DataFrame(rows)


def gen_fact_chitietdonhang_dirty(df_clean, dim_sanpham_clean):
    df = df_clean.copy()
    gia_niem_yet_map = dict(zip(dim_sanpham_clean["MaSanPham"], dim_sanpham_clean["GiaNiemYet"]))

    # loai lech #6: hai nguon gia khac nhau — 20-25% SO DON HANG co chenh gia
    # (khong phai 20-25% so dong chi tiet — dung sat chu de bai hon)
    df["GiaBanThucTe"] = u.inject_gia_chenh_lech_theo_don(
        df, ma_donhang_col="MaDonHang", ma_sanpham_col="MaSanPham", cot_gia="GiaBanThucTe",
        gia_niem_yet_map=gia_niem_yet_map, bang="Fact_ChiTietDonHang")

    df["MaDonHang"] = u.inject_id_format_mismatch(df["MaDonHang"], "sales", "Fact_ChiTietDonHang", "MaDonHang")
    df["MaSanPham"] = u.inject_id_format_mismatch(df["MaSanPham"], "sales", "Fact_ChiTietDonHang", "MaSanPham")
    # loai lech #5: ma san pham khong ton tai trong danh muc kho
    df["MaSanPham"] = u.inject_orphan_fk(
        df["MaSanPham"], u.make_orphan_pool("SP", n=15, start=9000),
        "Fact_ChiTietDonHang", "MaSanPham")
    df["MaSanPham"] = u.inject_missing(df["MaSanPham"], "Fact_ChiTietDonHang", "MaSanPham")
    return df

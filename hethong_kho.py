# -*- coding: utf-8 -*-
"""
hethong_kho.py — PHAN 3: He thong kho
Bang: Dim_SanPham, Fact_NhapXuatTonKho, Fact_DonMuaHang
+ Dim_NhaCungCap (GIA DINH BO SUNG - can de Fact_DonMuaHang/Fact_CongNoPhaiTra
  co doi tuong tra cuu; de bai khong liet ke ro trong danh sach bang bat buoc,
  xem ASSUMPTIONS.md).
"""
import random
import numpy as np
import pandas as pd

import config as cfg
import utils as u


# ==============================================================================
# Dim_SanPham
# ==============================================================================
def gen_dim_sanpham_clean():
    n = cfg.N_SANPHAM
    nhom = [random.choice(list(cfg.SP_THEO_NHOM.keys())) for _ in range(n)]
    ten = [f"{random.choice(cfg.SP_THEO_NHOM[nh])} {random.choice(['Loại 1', 'Loại 2', 'Cao cấp', 'Thường', ''])}".strip()
           for nh in nhom]
    # DonViTinh va GiaNiemYet PHAI hop ly theo tung nhom hang (khong dung chung
    # 1 khoang cho moi san pham — vd Bep tu phai dat hon Snack khoai tay nhieu)
    donvi = [random.choice(cfg.DONVITINH_THEO_NHOM[nh]) for nh in nhom]
    gia = [round(random.uniform(*cfg.GIA_NIEMYET_THEO_NHOM[nh]), -3) for nh in nhom]

    # THEM NGOAI DE BAI (xem ASSUMPTIONS.md muc 9): Han su dung — chi co y
    # nghia voi Thuc pham che bien/Do uong/Nguyen lieu; Gia dung -> None
    hsd = []
    for nh in nhom:
        rng_hsd = cfg.HANSUDUNG_NGAY_THEO_NHOM.get(nh)
        hsd.append(random.randint(*rng_hsd) if rng_hsd else None)

    # PHAN 3 de bai: toc do luan chuyen khac nhau -> gan noi bo, dung cho Fact_NhapXuatTonKho
    toc_do = list(np.random.choice(
        ["nhanh", "cham", "khong_ban_duoc"], size=n, p=[0.65, 0.25, 0.10]))

    df = pd.DataFrame({
        "MaSanPham": cfg.SP_IDS.copy(), "TenSanPham": ten, "NhomHang": nhom,
        "DonViTinh": donvi, "GiaNiemYet": gia, "HanSuDungNgay": hsd,
    })
    return df, toc_do


def gen_dim_sanpham_dirty(df_clean):
    df = df_clean.copy()
    df["MaSanPham"] = u.inject_id_format_mismatch(df["MaSanPham"], "kho", "Dim_SanPham", "MaSanPham")
    df["TenSanPham"] = u.inject_ten_khach_lech(df["TenSanPham"], bang="Dim_SanPham", cot="TenSanPham",
                                                rng=(0.08, 0.12))
    df["DonViTinh"] = u.inject_categorical_variants(
        df["DonViTinh"], cfg.DONVITINH_BIENTHE, "Dim_SanPham", "DonViTinh",
        "Don vi tinh khong thong nhat", rng=cfg.RATE_DONVI_KHONGDONG,
        mo_ta_them="Cung 1 nhom san pham cho ghi 'Thùng' cho ghi 'Hộp', hoac 'Kg' voi 'Tấn'.")
    mask_gia0, ty_le = u.rate_mask(len(df), cfg.RATE_MISSING)
    idx = np.where(mask_gia0)[0]
    df.loc[idx, "GiaNiemYet"] = 0
    u.log_error("Gia tri bat thuong (GiaNiemYet = 0)", "Dim_SanPham", "GiaNiemYet", ty_le,
                f"{len(idx)}/{len(df)} san pham bi ghi nham GiaNiemYet = 0.", so_dong_anh_huong=len(idx))

    # THEM NGOAI DE BAI: HanSuDungNgay bi bo trong o vai san pham LE RA phai co
    # (Thuc pham/Do uong/Nguyen lieu), mo phong nhan vien kho quen nhap HSD
    co_hsd = df["HanSuDungNgay"].notna()
    df["HanSuDungNgay"] = u.inject_missing(df["HanSuDungNgay"], "Dim_SanPham", "HanSuDungNgay",
                                            rng=(0.03, 0.05), protect=~co_hsd.to_numpy())
    return df


# ==============================================================================
# Dim_NhaCungCap (gia dinh bo sung)
# ==============================================================================
def gen_dim_nhacungcap_clean():
    n = cfg.N_NHACUNGCAP
    ten = [u.gen_vn_company_name() for _ in range(n)]
    vung = [random.choice(cfg.VUNG_CHUAN) for _ in range(n)]
    ngay_hoptac = [u.random_date(cfg.DATE_START - pd.Timedelta(days=900), cfg.DATE_START) for _ in range(n)]
    df = pd.DataFrame({
        "MaNhaCungCap": cfg.NCC_IDS.copy(), "TenNhaCungCap": ten,
        "Vung": vung, "NgayHopTac": ngay_hoptac,
    })
    return df


def gen_dim_nhacungcap_dirty(df_clean):
    df = df_clean.copy()
    df["MaNhaCungCap"] = u.inject_id_format_mismatch(df["MaNhaCungCap"], "kho", "Dim_NhaCungCap", "MaNhaCungCap")
    df["TenNhaCungCap"] = u.inject_ten_khach_lech(df["TenNhaCungCap"], bang="Dim_NhaCungCap", cot="TenNhaCungCap",
                                                   rng=(0.10, 0.15))
    df["NgayHopTac"] = u.messy_date_series(df["NgayHopTac"], "Dim_NhaCungCap", "NgayHopTac")
    return df


# ==============================================================================
# Fact_NhapXuatTonKho (theo thang, cho tung san pham — co luan chuyen ton kho)
# ==============================================================================
def gen_fact_nhapxuatton_clean(dim_sanpham_clean, toc_do_luanchuyen):
    thangs = u.thang_list()
    sp_ids = dim_sanpham_clean["MaSanPham"].tolist()
    toc_do_map = dict(zip(sp_ids, toc_do_luanchuyen))
    nhom_map = dict(zip(dim_sanpham_clean["MaSanPham"], dim_sanpham_clean["NhomHang"]))

    rows = []
    ton_dau_hien_tai = {sp: random.randint(50, 500) for sp in sp_ids}

    for th in thangs:
        heso_mv = cfg.HESO_MUAVU_THEOTHANG[th.month]
        for sp in sp_ids:
            td = toc_do_map[sp]
            ton_dau = ton_dau_hien_tai[sp]
            if td == "nhanh":
                nhap = int(random.uniform(150, 400) * heso_mv)
                xuat = int(nhap * random.uniform(0.85, 1.05))
            elif td == "cham":
                nhap = int(random.uniform(20, 80) * heso_mv)
                xuat = int(nhap * random.uniform(0.3, 0.6))
            else:  # khong_ban_duoc -> ton dong nhieu thang khong xuat
                nhap = int(random.uniform(0, 20))
                xuat = int(nhap * random.uniform(0, 0.15))

            # THEM NGOAI DE BAI (xem ASSUMPTIONS.md muc 9): hao hut kho hang
            # thang, ty le khac nhau theo nhom hang (thuc pham/do uong de hao
            # hut hon gia dung/nguyen lieu). Tinh tren luong NHAP trong ky.
            lo_hh, hi_hh = cfg.TYLE_HAOHUT_THEO_NHOM[nhom_map[sp]]
            hao_hut = int(round(nhap * random.uniform(lo_hh, hi_hh)))

            xuat = min(xuat, ton_dau + nhap - hao_hut) if (ton_dau + nhap - hao_hut) > 0 else 0
            hao_hut = min(hao_hut, ton_dau + nhap)  # khong de am
            ton_cuoi = ton_dau + nhap - xuat - hao_hut
            rows.append({
                "MaSanPham": sp, "Thang": th, "TonDauKy": ton_dau,
                "Nhap": nhap, "Xuat": xuat, "HaoHut": hao_hut, "TonCuoiKy": ton_cuoi,
            })
            ton_dau_hien_tai[sp] = ton_cuoi

    return pd.DataFrame(rows)


def gen_fact_nhapxuatton_dirty(df_clean):
    df = df_clean.copy()
    n = len(df)

    df["Thang"] = df["Thang"].dt.strftime("%Y-%m")
    df["MaSanPham"] = u.inject_id_format_mismatch(df["MaSanPham"], "kho", "Fact_NhapXuatTonKho", "MaSanPham")
    df["MaSanPham"] = u.inject_orphan_fk(
        df["MaSanPham"], u.make_orphan_pool("SP", n=10, start=9500),
        "Fact_NhapXuatTonKho", "MaSanPham")
    df["MaSanPham"] = u.inject_missing(df["MaSanPham"], "Fact_NhapXuatTonKho", "MaSanPham", rng=(0.01, 0.02))

    # loai lech #7: so luong ghi lan lon don vi kg/tan (nhan/chia 1000 cho mot so dong)
    # ep kieu sang float TRUOC khi gieo, vi ket qua nhan/chia 1000 co the ra so thap
    # phan (vd 0.37) khong the gan vao cot dang int64 (pandas moi se bao LossySetitemError)
    for c in ["TonDauKy", "Nhap", "Xuat", "HaoHut", "TonCuoiKy"]:
        df[c] = df[c].astype(float)
    mask, ty_le = u.rate_mask(n, (0.05, 0.10))
    idx = np.where(mask)[0]
    for i in idx:
        h = random.choice([1000, 0.001])
        for c in ["TonDauKy", "Nhap", "Xuat", "HaoHut", "TonCuoiKy"]:
            df.at[i, c] = round(df.at[i, c] * h, 2)
    u.log_error("Don vi tinh khong thong nhat (kg/tan lan lon)", "Fact_NhapXuatTonKho",
                "TonDauKy/Nhap/Xuat/TonCuoiKy", ty_le,
                f"{len(idx)}/{n} dong bi nhan/chia 1000 do nhap lan don vi kg <-> tan.",
                so_dong_anh_huong=len(idx))
    return df


# ==============================================================================
# Fact_DonMuaHang
# ==============================================================================
def gen_fact_donmuahang_clean(dim_sanpham_clean):
    n = cfg.N_DONMUAHANG
    sp_ids = dim_sanpham_clean["MaSanPham"].tolist()
    gia_niem_yet_map = dict(zip(dim_sanpham_clean["MaSanPham"], dim_sanpham_clean["GiaNiemYet"]))
    nhom_map = dict(zip(dim_sanpham_clean["MaSanPham"], dim_sanpham_clean["NhomHang"]))

    ma = [f"PO{str(i).zfill(6)}" for i in range(1, n + 1)]
    ncc = [random.choice(cfg.NCC_IDS) for _ in range(n)]
    sp = [random.choice(sp_ids) for _ in range(n)]
    ngay = [u.random_date() for _ in range(n)]
    soluong = [random.randint(20, 1000) for _ in range(n)]

    # DonGiaMua PHAI dong bo voi BIEN_LOINHUAN_THEO_NHOM (dung config voi Dim_GiaVon
    # ben he thong Ke toan), thay vi 1 ty le phang 0.35-0.70 khong phan biet nhom hang.
    # DonGiaMua (gia mua GOC tu NCC) lay thap hon mot chut so voi GiaVon hach toan,
    # vi GiaVon con cong them cac chi phi phu troi (van chuyen, hao hut, phan bo...).
    dongia = []
    for s in sp:
        lo, hi = cfg.BIEN_LOINHUAN_THEO_NHOM[nhom_map[s]]
        ty_le_mua = random.uniform(lo, hi) * random.uniform(0.85, 0.95)
        dongia.append(round(gia_niem_yet_map[s] * ty_le_mua, -2))

    df = pd.DataFrame({
        "MaDonMuaHang": ma, "MaNhaCungCap": ncc, "MaSanPham": sp,
        "NgayDatHang": ngay, "SoLuong": soluong, "DonGiaMua": dongia,
    })
    return df.sort_values("NgayDatHang").reset_index(drop=True)


def gen_fact_donmuahang_dirty(df_clean):
    df = df_clean.copy()
    df = u.inject_duplicate_rows(df, "MaDonMuaHang", "Fact_DonMuaHang")

    df["MaDonMuaHang"] = u.inject_id_format_mismatch(df["MaDonMuaHang"], "kho", "Fact_DonMuaHang", "MaDonMuaHang")
    df["MaNhaCungCap"] = u.inject_id_format_mismatch(df["MaNhaCungCap"], "kho", "Fact_DonMuaHang", "MaNhaCungCap")
    df["MaNhaCungCap"] = u.inject_orphan_fk(
        df["MaNhaCungCap"], u.make_orphan_pool("NCC", n=10, start=900),
        "Fact_DonMuaHang", "MaNhaCungCap")
    df["MaSanPham"] = u.inject_id_format_mismatch(df["MaSanPham"], "kho", "Fact_DonMuaHang", "MaSanPham")
    df["NgayDatHang"] = u.messy_date_series(df["NgayDatHang"], "Fact_DonMuaHang", "NgayDatHang")
    df["MaSanPham"] = u.inject_missing(df["MaSanPham"], "Fact_DonMuaHang", "MaSanPham")
    return df

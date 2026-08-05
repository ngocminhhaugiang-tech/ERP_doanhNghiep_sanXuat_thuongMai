# -*- coding: utf-8 -*-
"""
================================================================================
MAIN.PY — Sinh toan bo du lieu HPT (Bai tap tuan 2)
================================================================================
Chay:
    python main.py

Ket qua (trong ./output/):
  00_ban_sach/        <He_thong>/<Ten_bang>.csv   -> ban SACH, giu rieng de doi
                                                       chieu lam sach o tuan 8
  01_ban_gieo_loi/     <He_thong>/<Ten_bang>.csv   -> ban DA GIEO LOI, dung cho
                                                       cac bai tuan sau
  02_data_dictionary/  Data_Dictionary.csv/.xlsx    -> tu dong sinh tu METADATA
                        Bang_GhiNhanLech.csv/.xlsx   -> tu dong sinh tu ERROR_LOG
  HPT_DuLieu_GieoLoi_TongHop.xlsx                    -> 1 file Excel gom moi
                                                         bang gieo loi, 1 sheet/bang

4 he thong nguon (dung theo de bai):
  01_BanHang     : Dim_KhachHang, Fact_DonHang, Fact_ChiTietDonHang
  02_KeToan      : Fact_HoaDonCongNoPhaiThu, Fact_CongNoPhaiTra, Fact_ChiPhi, Dim_GiaVon
  03_Kho_MuaHang : Dim_SanPham, Dim_NhaCungCap, Fact_NhapXuatTonKho, Fact_DonMuaHang
  04_ExcelPhongBan: Dim_NhanVienSales, Fact_ChiTieuKeHoach, Dim_PhanNhomKhachHang
================================================================================
"""
import os
import pandas as pd

import config as cfg
import utils as u
import hethong_banhang as p1
import hethong_ketoan as p2
import hethong_kho as p3
import excel_phongban as p4
from generate_data_dictionary import build_data_dictionary, DICTIONARY_METADATA


def _save(df, he_thong, ten_bang, subdir):
    folder = os.path.join(cfg.OUTPUT_DIR, subdir, he_thong)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{ten_bang}.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"   [{subdir}/{he_thong}] {ten_bang}: {len(df):>6} dong -> {path}")


def main():
    print(">> Dang sinh du lieu HPT (4 he thong nguon)...\n")

    # ==========================================================================
    # BUOC 1 — SINH BAN SACH (dung lam nen cho toan bo quan he FK + tinh dung
    #           cac cong thuc nghiep vu, TRUOC KHI gieo bat ky loi nao)
    # ==========================================================================
    print(">> [1/3] Sinh ban SACH...")
    dim_khachhang_c, kh_weights = p1.gen_dim_khachhang_clean()
    dim_sanpham_c, toc_do_lc = p3.gen_dim_sanpham_clean()
    dim_nhacungcap_c = p3.gen_dim_nhacungcap_clean()
    dim_nhanviensales_c = p4.gen_dim_nhanviensales_clean()

    fact_donhang_c = p1.gen_fact_donhang_clean(kh_weights)
    fact_chitietdonhang_c = p1.gen_fact_chitietdonhang_clean(fact_donhang_c, dim_sanpham_c, dim_khachhang_c)

    # THEM NGOAI DE BAI: hieu chinh lai HanMucCongNo dua tren doanh thu THAT
    # SU cua tung khach (phai lam SAU khi co Fact_ChiTietDonHang), tranh han
    # muc qua thap so voi quy mo mua that cua khach Si mua so luong lon
    dim_khachhang_c = p1.recalibrate_han_muc_congno(dim_khachhang_c, fact_donhang_c, fact_chitietdonhang_c)
    
    fact_donmuahang_c = p3.gen_fact_donmuahang_clean(dim_sanpham_c)
    fact_nhapxuatton_c = p3.gen_fact_nhapxuatton_clean(dim_sanpham_c, toc_do_lc)

    fact_congnophaithu_c = p2.gen_fact_congnophaithu_clean(fact_donhang_c, fact_chitietdonhang_c, dim_khachhang_c)
    fact_congnophaitra_c = p2.gen_fact_congnophaitra_clean(fact_donmuahang_c)
    fact_chiphi_c = p2.gen_fact_chiphi_clean(fact_donhang_c, fact_chitietdonhang_c)
    dim_giavon_c = p2.gen_dim_giavon_clean(dim_sanpham_c)

    fact_chitieukehoach_c = p4.gen_fact_chitieukehoach_clean(
        fact_donhang_c, fact_chitietdonhang_c, dim_khachhang_c, dim_nhanviensales_c)
    dim_phannhomkhachhang_c = p4.gen_dim_phannhomkhachhang_clean(dim_khachhang_c)

    clean_tables = {
        "01_BanHang": {
            "Dim_KhachHang": dim_khachhang_c,
            "Fact_DonHang": fact_donhang_c,
            "Fact_ChiTietDonHang": fact_chitietdonhang_c,
        },
        "02_KeToan": {
            "Fact_HoaDonCongNoPhaiThu": fact_congnophaithu_c,
            "Fact_CongNoPhaiTra": fact_congnophaitra_c,
            "Fact_ChiPhi": fact_chiphi_c,
            "Dim_GiaVon": dim_giavon_c,
        },
        "03_Kho_MuaHang": {
            "Dim_SanPham": dim_sanpham_c,
            "Dim_NhaCungCap": dim_nhacungcap_c,
            "Fact_NhapXuatTonKho": fact_nhapxuatton_c,
            "Fact_DonMuaHang": fact_donmuahang_c,
        },
        "04_ExcelPhongBan": {
            "Dim_NhanVienSales": dim_nhanviensales_c,
            "Fact_ChiTieuKeHoach": fact_chitieukehoach_c,
            "Dim_PhanNhomKhachHang": dim_phannhomkhachhang_c,
        },
    }
    for he_thong, bang_dict in clean_tables.items():
        for ten_bang, df in bang_dict.items():
            _save(df, he_thong, ten_bang, cfg.CLEAN_SUBDIR)

    # ==========================================================================
    # BUOC 2 — GIEO LOI TREN BAN SAO (ban sach giu nguyen o tren, KHONG bi doi)
    # ==========================================================================
    print("\n>> [2/3] Gieo loi -> sinh ban GIEO LOI...")
    dim_khachhang_d = p1.gen_dim_khachhang_dirty(dim_khachhang_c)
    fact_donhang_d = p1.gen_fact_donhang_dirty(fact_donhang_c)
    fact_chitietdonhang_d = p1.gen_fact_chitietdonhang_dirty(fact_chitietdonhang_c, dim_sanpham_c)

    dim_sanpham_d = p3.gen_dim_sanpham_dirty(dim_sanpham_c)
    dim_nhacungcap_d = p3.gen_dim_nhacungcap_dirty(dim_nhacungcap_c)
    fact_nhapxuatton_d = p3.gen_fact_nhapxuatton_dirty(fact_nhapxuatton_c)
    fact_donmuahang_d = p3.gen_fact_donmuahang_dirty(fact_donmuahang_c)

    fact_congnophaithu_d = p2.gen_fact_congnophaithu_dirty(fact_congnophaithu_c)
    fact_congnophaitra_d = p2.gen_fact_congnophaitra_dirty(fact_congnophaitra_c)
    fact_chiphi_d = p2.gen_fact_chiphi_dirty(fact_chiphi_c)
    dim_giavon_d = p2.gen_dim_giavon_dirty(dim_giavon_c)

    dim_nhanviensales_d = p4.gen_dim_nhanviensales_dirty(dim_nhanviensales_c)
    fact_chitieukehoach_d = p4.gen_fact_chitieukehoach_dirty(fact_chitieukehoach_c)
    dim_phannhomkhachhang_d = p4.gen_dim_phannhomkhachhang_dirty(dim_phannhomkhachhang_c)

    dirty_tables = {
        "01_BanHang": {
            "Dim_KhachHang": dim_khachhang_d,
            "Fact_DonHang": fact_donhang_d,
            "Fact_ChiTietDonHang": fact_chitietdonhang_d,
        },
        "02_KeToan": {
            "Fact_HoaDonCongNoPhaiThu": fact_congnophaithu_d,
            "Fact_CongNoPhaiTra": fact_congnophaitra_d,
            "Fact_ChiPhi": fact_chiphi_d,
            "Dim_GiaVon": dim_giavon_d,
        },
        "03_Kho_MuaHang": {
            "Dim_SanPham": dim_sanpham_d,
            "Dim_NhaCungCap": dim_nhacungcap_d,
            "Fact_NhapXuatTonKho": fact_nhapxuatton_d,
            "Fact_DonMuaHang": fact_donmuahang_d,
        },
        "04_ExcelPhongBan": {
            "Dim_NhanVienSales": dim_nhanviensales_d,
            "Fact_ChiTieuKeHoach": fact_chitieukehoach_d,
            "Dim_PhanNhomKhachHang": dim_phannhomkhachhang_d,
        },
    }
    for he_thong, bang_dict in dirty_tables.items():
        for ten_bang, df in bang_dict.items():
            _save(df, he_thong, ten_bang, cfg.DIRTY_SUBDIR)

    # 1 file Excel tong hop ban gieo loi (moi bang 1 sheet) cho tien xem nhanh
    excel_path = os.path.join(cfg.OUTPUT_DIR, "HPT_DuLieu_GieoLoi_TongHop.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for he_thong, bang_dict in dirty_tables.items():
            for ten_bang, df in bang_dict.items():
                df.to_excel(writer, sheet_name=ten_bang[:31], index=False)
    print(f"\n   -> Da xuat file Excel tong hop: {excel_path}")

    # ==========================================================================
    # BUOC 3 — PHAN 5: DATA DICTIONARY + BANG GHI NHAN LECH
    # ==========================================================================
    print("\n>> [3/3] Xuat Data Dictionary va Bang Ghi Nhan Lech (PHAN 5)...")
    os.makedirs(cfg.DIR_DICT if hasattr(cfg, "DIR_DICT") else
                os.path.join(cfg.OUTPUT_DIR, "02_data_dictionary"), exist_ok=True)
    dict_dir = os.path.join(cfg.OUTPUT_DIR, "02_data_dictionary")

    dd_df = build_data_dictionary()
    dd_df.to_csv(os.path.join(dict_dir, "Data_Dictionary.csv"), index=False, encoding="utf-8-sig")
    dd_df.to_excel(os.path.join(dict_dir, "Data_Dictionary.xlsx"), index=False)
    print(f"   -> Data_Dictionary: {len(dd_df)} dong cot -> {dict_dir}/Data_Dictionary.csv (.xlsx)")

    log_df = pd.DataFrame(u.ERROR_LOG)
    log_df.to_csv(os.path.join(dict_dir, "Bang_GhiNhanLech.csv"), index=False, encoding="utf-8-sig")
    log_df.to_excel(os.path.join(dict_dir, "Bang_GhiNhanLech.xlsx"), index=False)
    print(f"   -> Bang_GhiNhanLech: {len(log_df)} lan gieo loi -> {dict_dir}/Bang_GhiNhanLech.csv (.xlsx)")

    print("\n>> HOAN TAT! Xem output/ de lay ket qua.")


if __name__ == "__main__":
    main()

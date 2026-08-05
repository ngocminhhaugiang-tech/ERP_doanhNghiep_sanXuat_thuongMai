# -*- coding: utf-8 -*-
"""
utils.py — Cac ham dung chung: sinh ten nguoi/cong ty, gieo loi Data Quality,
            va so ghi nhan lech (ERROR_LOG) de xuat "Bang_GhiNhanLech" o PHAN 5.
"""
import random
import re
import numpy as np
import pandas as pd
from datetime import timedelta
from unidecode import unidecode

import config as cfg

# ==============================================================================
# SO GHI NHAN LECH — moi lan goi log_error() se them 1 dong vao day.
# Cuoi cung main.py se xuat toan bo thanh Bang_GhiNhanLech.csv/xlsx (PHAN 5)
# ==============================================================================
ERROR_LOG = []


def log_error(loai_lech, bang, cot, ty_le_ap_dung, mo_ta, so_dong_anh_huong=None):
    """Ghi 1 dong vao so theo doi cac loai lech da gieo (dung cho PHAN 5)."""
    ERROR_LOG.append({
        "LoaiLech": loai_lech,
        "GieoOBang": bang,
        "GieoOCot": cot,
        "TyLeApDung": round(ty_le_ap_dung, 4) if ty_le_ap_dung is not None else None,
        "SoDongAnhHuong": so_dong_anh_huong,
        "MoTa": mo_ta,
    })


def rr(rng):
    """Random 1 ty le nam trong khoang (lo, hi)."""
    return random.uniform(*rng)


def rate_mask(n, rng):
    """Tra ve (mask, ty_le_da_chon) - mask boolean dai n."""
    r = rr(rng)
    return np.random.rand(n) < r, r


def random_date(start=cfg.DATE_START, end=cfg.DATE_END):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                              seconds=random.randint(0, 86399))


def thang_list(n_thang=cfg.SO_THANG_LICHSU, end=cfg.DATE_END):
    """Danh sach cac ky thang (Timestamp, ngay 1 dau thang) gan nhat, dai n_thang."""
    return pd.date_range(end=end.replace(day=1), periods=n_thang, freq="MS")


# ==============================================================================
# SINH TEN NGUOI / TEN CONG TY VIET NAM
# ==============================================================================
def gen_vn_person_name():
    ho = random.choice(cfg.VN_HO)
    if random.random() < 0.5:
        return f"{ho} {random.choice(cfg.VN_TENDEM_NAM)} {random.choice(cfg.VN_TEN_NAM)}"
    return f"{ho} {random.choice(cfg.VN_TENDEM_NU)} {random.choice(cfg.VN_TEN_NU)}"


def gen_vn_company_name():
    return f"{random.choice(cfg.VN_COMPANY_SUFFIX)} {random.choice(cfg.VN_COMPANY_NGANH)} {random.choice(cfg.VN_COMPANY_BRAND)}"


# ==============================================================================
# GIEO LOI #1 — MA LECH DINH DANG GIUA CAC HE THONG (ap dung PHAN LON ban ghi)
# ==============================================================================
def format_id_theo_he_thong(code, he_thong):
    """
    Dinh dang lai 1 ma khoa theo "kieu" cua tung he thong nguon, mo phong
    dung tinh huong de bai: cung 1 khach hang nhung Sales ghi KH0001,
    Excel ghi KH-0001, Ke toan ghi kh0001.
    """
    if not isinstance(code, str):
        return code
    if he_thong == "sales":
        return code  # he thong goc / chuan
    if he_thong == "ketoan":
        return code.lower()
    if he_thong == "kho":
        return code  # kho dung chung goc voi Sales trong bo nay
    if he_thong == "excel":
        # chen dau gach ngang sau phan chu: KH0001 -> KH-0001
        i = 0
        while i < len(code) and code[i].isalpha():
            i += 1
        return f"{code[:i]}-{code[i:]}"
    return code


def inject_id_format_mismatch(series, he_thong, bang, cot, rng=cfg.RATE_ID_FORMAT_MISMATCH):
    """
    Ap dinh dang "kieu he thong" cho PHAN LON ban ghi cua 1 cot ma khoa
    (mo ta loai lech #1 trong de bai). Ghi log vao ERROR_LOG.
    """
    s = series.astype(object).copy()
    mask, ty_le = rate_mask(len(s), rng)
    idx = np.where(mask)[0]
    for i in idx:
        s.iat[i] = format_id_theo_he_thong(s.iat[i], he_thong)
    log_error(
        "Ma lech dinh dang giua he thong",
        bang, cot, ty_le,
        f"Ap dinh dang kieu '{he_thong}' cho {len(idx)}/{len(s)} dong "
        f"(vd Sales=KH0001, Excel=KH-0001, KeToan=kh0001).",
        so_dong_anh_huong=len(idx),
    )
    return s


# ==============================================================================
# GIEO LOI #2 — TEN KHACH HANG VIET KHAC NHAU (15-20% khach hang)
# ==============================================================================
def double_space(text):
    if not isinstance(text, str) or " " not in text:
        return text
    words = text.split(" ")
    i = random.randrange(len(words) - 1)
    words[i] = words[i] + " "
    return " ".join(words)


def bien_the_ten(text):
    """Sinh 1 trong cac bien the viet cua cung 1 ten: HOA/thuong, bo dau, viet tat Cty/Cong ty."""
    if not isinstance(text, str) or not text.strip():
        return text
    kieu = random.choice(["upper_nodau", "lower", "viet_tat", "double_space"])
    if kieu == "upper_nodau":
        return unidecode(text).upper()
    if kieu == "lower":
        return text.lower()
    if kieu == "viet_tat":
        t = text.replace("Công ty TNHH MTV", "Cty TNHH MTV")
        t = t.replace("Công ty TNHH", "Cty TNHH")
        t = t.replace("Công ty Cổ phần", "Cty CP")
        t = t.replace("Doanh nghiệp tư nhân", "DNTN")
        return t
    return double_space(text)


def inject_ten_khach_lech(series, bang="Dim_KhachHang", cot="TenKhachHang",
                           rng=cfg.RATE_TEN_KHACH_LECH):
    """Gieo bien the cach viet ten cho 15-20% khach hang (loai lech #2)."""
    s = series.astype(object).copy()
    mask, ty_le = rate_mask(len(s), rng)
    idx = np.where(mask)[0]
    for i in idx:
        s.iat[i] = bien_the_ten(s.iat[i])
    log_error(
        "Ten khach hang viet khac nhau",
        bang, cot, ty_le,
        f"{len(idx)}/{len(s)} khach hang bi doi cach viet ten "
        f"(HOA/thuong, bo dau, viet tat Cty/Cong ty...) — nguyen lieu cho bai gop khach hang.",
        so_dong_anh_huong=len(idx),
    )
    return s


# ==============================================================================
# GIEO LOI #3 — NGAY LECH DINH DANG
# ==============================================================================
def messy_date_series(dates, bang, cot, rng=cfg.RATE_NGAY_LECH, as_datetime=False):
    """
    Chuan la dd/mm/yyyy. Mot vai % bi lech thanh yyyy-mm-dd hoac mm/dd/yyyy
    (loai lech #3 trong de bai).
    """
    n = len(dates)
    mask, ty_le = rate_mask(n, rng)
    out = []
    n_anh_huong = 0
    for i, d in enumerate(dates):
        if d is None or (isinstance(d, float) and np.isnan(d)):
            out.append(None)
            continue
        if mask[i]:
            n_anh_huong += 1
            fmt = random.choice(["%Y-%m-%d", "%m/%d/%Y"])
            fmt_full = fmt if not as_datetime else fmt + " %H:%M:%S"
            out.append(d.strftime(fmt_full))
        else:
            fmt_full = "%d/%m/%Y" if not as_datetime else "%d/%m/%Y %H:%M:%S"
            out.append(d.strftime(fmt_full))
    log_error(
        "Ngay lech dinh dang",
        bang, cot, ty_le,
        f"{n_anh_huong}/{n} dong bi doi dinh dang ngay thanh yyyy-mm-dd hoac "
        f"mm/dd/yyyy thay vi chuan dd/mm/yyyy.",
        so_dong_anh_huong=n_anh_huong,
    )
    return pd.Series(out)


# ==============================================================================
# GIEO LOI #4 — GIA TRI THIEU (ma khach, ma san pham, ngay ~3-5%)
# ==============================================================================
def inject_missing(series, bang, cot, rng=cfg.RATE_MISSING, protect=None):
    s = series.astype(object).copy()
    mask, ty_le = rate_mask(len(s), rng)
    if protect is not None:
        mask = mask & (~protect)
    n_anh_huong = int(mask.sum())
    s[mask] = None
    log_error(
        "Gia tri thieu (NULL)",
        bang, cot, ty_le,
        f"{n_anh_huong}/{len(s)} dong bi de trong o cot '{cot}'.",
        so_dong_anh_huong=n_anh_huong,
    )
    return s


# ==============================================================================
# GIEO LOI #5 — MA THAM CHIEU KHONG TON TAI (Orphan FK, 2-3%)
# ==============================================================================
def make_orphan_pool(prefix, n=15, start=9000):
    return [f"{prefix}{start + i}" for i in range(n)]


def inject_orphan_fk(series, fake_pool, bang, cot, rng=cfg.RATE_ORPHAN_FK):
    s = series.astype(object).copy()
    mask, ty_le = rate_mask(len(s), rng)
    idx = np.where(mask)[0]
    for i in idx:
        s.iat[i] = random.choice(fake_pool)
    log_error(
        "Ma tham chieu khong ton tai (Orphan FK)",
        bang, cot, ty_le,
        f"{len(idx)}/{len(s)} dong co '{cot}' tro toi ma khong ton tai trong bang danh muc goc.",
        so_dong_anh_huong=len(idx),
    )
    return s


# ==============================================================================
# GIEO LOI #6 — HAI NGUON GIA KHAC NHAU (20-25% don co chenh)
# ==============================================================================
def inject_gia_chenh_lech(gia_ban_series, gia_niem_yet_series, bang, cot,
                           rng=cfg.RATE_GIA_CHENH_LECH):
    """
    GiaBan thuc te (Fact_ChiTietDonHang) lech so voi GiaNiemYet (Dim_SanPham)
    o 20-25% dong (loai lech #6). Lech theo ca 2 chieu: khuyen mai (thap hon)
    va nhan vien tu y tang gia (cao hon).

    LUU Y: ham nay ap ty le TREN TUNG DONG CHI TIET. De bai dien dat la
    "20-25% DON co chenh" (muc don hang) -> dung ham
    inject_gia_chenh_lech_theo_don() ben duoi de dung sat chu nghia de bai hon.
    Ham nay giu lai (khong xoa) de tham khao / dung cho truong hop can gieo
    o muc dong.
    """
    n = len(gia_ban_series)
    mask, ty_le = rate_mask(n, rng)
    idx = np.where(mask)[0]
    s = gia_ban_series.copy()
    for i in idx:
        niem_yet = gia_niem_yet_series.iat[i]
        if random.random() < 0.7:
            s.iat[i] = round(niem_yet * random.uniform(0.75, 0.95), -2)  # khuyen mai
        else:
            s.iat[i] = round(niem_yet * random.uniform(1.02, 1.15), -2)  # tang gia
    log_error(
        "Hai nguon gia khac nhau",
        bang, cot, ty_le,
        f"{len(idx)}/{n} dong chi tiet don hang co GiaBanThucTe lech so voi "
        f"GiaNiemYet ben Dim_SanPham (khuyen mai hoac tu y tang gia).",
        so_dong_anh_huong=len(idx),
    )
    return s


def inject_gia_chenh_lech_theo_don(df_chitiet, ma_donhang_col, ma_sanpham_col, cot_gia,
                                    gia_niem_yet_map, bang, rng=cfg.RATE_GIA_CHENH_LECH):
    """
    Ban DUNG CHU NGHIA de bai hon inject_gia_chenh_lech(): de bai noi
    "20-25% DON co chenh gia" (muc DON HANG), khong phai muc dong chi tiet.
    Ham nay chon 20-25% SO MA DON HANG (khong phai so dong), roi ap lech gia
    cho TAT CA cac dong chi tiet thuoc nhung don da chon do -> dung "ca don
    bi chenh gia" thay vi rai rac tung dong doc lap.
    """
    don_ids = df_chitiet[ma_donhang_col].unique()
    mask_don, ty_le = rate_mask(len(don_ids), rng)
    don_chon = set(don_ids[mask_don])

    s = df_chitiet[cot_gia].copy()
    idx = df_chitiet.index[df_chitiet[ma_donhang_col].isin(don_chon)]
    n_dong_anh_huong = 0
    for i in idx:
        niem_yet = gia_niem_yet_map.get(df_chitiet.at[i, ma_sanpham_col])
        if niem_yet is None:
            continue
        n_dong_anh_huong += 1
        if random.random() < 0.7:
            s.at[i] = round(niem_yet * random.uniform(0.75, 0.95), -2)  # khuyen mai
        else:
            s.at[i] = round(niem_yet * random.uniform(1.02, 1.15), -2)  # tang gia

    log_error(
        "Hai nguon gia khac nhau",
        bang, cot_gia, ty_le,
        f"{len(don_chon)}/{len(don_ids)} DON HANG (khong phai dong) bi chon co chenh gia; "
        f"tat ca {n_dong_anh_huong} dong chi tiet thuoc cac don do deu bi doi GiaBanThucTe "
        f"lech so voi GiaNiemYet (khuyen mai hoac tu y tang gia). Dung muc DON dung sat "
        f"chu de bai '20-25% don co chenh' hon la gieo rai rac tung dong doc lap.",
        so_dong_anh_huong=n_dong_anh_huong,
    )
    return s


# ==============================================================================
# GIEO LOI #7 — DON VI TINH KHONG THONG NHAT
# ==============================================================================
def inject_categorical_variants(series, variant_map, bang, cot, loai_lech, rng, mo_ta_them=""):
    s = series.astype(object).copy()
    mask, ty_le = rate_mask(len(s), rng)
    idx = np.where(mask)[0]
    n_anh_huong = 0
    for i in idx:
        val = s.iat[i]
        variants = variant_map.get(val)
        if variants:
            s.iat[i] = random.choice(variants)
            n_anh_huong += 1
    log_error(
        loai_lech, bang, cot, ty_le,
        f"{n_anh_huong}/{len(s)} dong bi doi thanh bien the khong chuan cua cot '{cot}'. {mo_ta_them}",
        so_dong_anh_huong=n_anh_huong,
    )
    return s


# ==============================================================================
# GIEO LOI #8 — BAN GHI TRUNG (cung don hang nhap 2 lan, ma khac nhau, 1-2%)
# ==============================================================================
def inject_duplicate_rows(df, pk_col, bang, rate_rng=cfg.RATE_TRUNG_BAN_GHI, sinh_ma_moi=True):
    """
    Loai lech #8: BAN GHI TRUNG.

    - sinh_ma_moi=True (mac dinh, dung cho Fact_DonHang/Fact_DonMuaHang...):
      PK la ma SURROGATE do he thong tu sinh khi nhap. "Trung ban ghi" o day
      nghia la CUNG 1 giao dich duoc nhap tay 2 LAN -> NOI DUNG giu nguyen
      y het (khach/san pham/ngay/tien...), chi khac MA vi moi lan nhap he
      thong tu sinh 1 ma moi. Day la dang trung lap kinh dien phai phat hien
      bang cach so sanh NOI DUNG, khong the loc bang GROUP BY pk_col.

    - sinh_ma_moi=False (dung cho Dim_PhanNhomKhachHang...): PK la MA NGHIEP
      VU that (vd MaKhachHang) chu khong phai ma surrogate. "Trung ban ghi"
      o day nghia la nguoi dung tu nhap Excel ghi TRUNG 1 doi tuong 2 lan ->
      GIU NGUYEN pk_col goc (that su trung khoa), dung GROUP BY pk_col la
      phat hien duoc ngay.
    """
    n = len(df)
    ty_le = rr(rate_rng)
    n_dup = max(1, int(n * ty_le))
    dup_rows = df.sample(n=n_dup, random_state=random.randint(0, 10_000)).copy()

    if sinh_ma_moi:
        sample_pk = str(df[pk_col].iloc[0])
        m = re.match(r"([A-Za-z]+)(\d+)", sample_pk)
        prefix = m.group(1) if m else "DUP"
        dup_rows[pk_col] = [f"{prefix}9{900000 + i}" for i in range(n_dup)]
        mo_ta = (f"Nhan ban {n_dup} dong, GIU NGUYEN toan bo noi dung (khach/san pham/"
                 f"ngay/tien...) nhung gan '{pk_col}' MOI (khac ma goc) -> mo phong nhap "
                 f"tay lai TU DAU cung 1 giao dich (he thong tu sinh ma moi moi lan nhap). "
                 f"Phai phat hien bang cach so sanh NOI DUNG, khong the GROUP BY '{pk_col}'.")
    else:
        mo_ta = (f"Nhan ban {n_dup} dong, GIU NGUYEN '{pk_col}' goc (that su trung khoa) "
                 f"-> mo phong nguoi dung tu nhap Excel ghi trung 1 doi tuong nghiep vu 2 lan. "
                 f"Phat hien duoc ngay bang GROUP BY '{pk_col}'.")

    out = pd.concat([df, dup_rows], ignore_index=True)
    log_error(
        "Ban ghi trung (cung giao dich, ma khac nhau)" if sinh_ma_moi else "Ban ghi trung (trung khoa nghiep vu)",
        bang, pk_col, ty_le, mo_ta, so_dong_anh_huong=n_dup,
    )
    return out.sample(frac=1, random_state=cfg.SEED).reset_index(drop=True)

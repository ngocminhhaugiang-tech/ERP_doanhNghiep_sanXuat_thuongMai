# -*- coding: utf-8 -*-
"""
generate_data_dictionary.py — PHAN 5 (de bai tuan 2): Data Dictionary

File nay TRUOC DAY BI THIEU trong repo (main.py co dong
`from generate_data_dictionary import build_data_dictionary, DICTIONARY_METADATA`
nhung khong co file nao dinh nghia no) -> day la nguyen nhan chinh khien
`python main.py` bao loi ModuleNotFoundError va khong chay duoc.

Noi dung: khai bao metadata cho TUNG COT cua TUNG BANG (dung format de bai
yeu cau o PHAN 5: "tên cột, kiểu dữ liệu, ý nghĩa nghiệp vụ, giá trị hợp lệ,
thuộc hệ thống nguồn nào, và khóa nối sang bảng nào"), roi gop lai thanh 1
DataFrame phang de xuat Data_Dictionary.csv / .xlsx.
"""
import pandas as pd

# ==============================================================================
# DICTIONARY_METADATA
# { "01_HeThong": { "TenBang": (grain, [ (cot, kieu, vai_tro, y_nghia, gia_tri_hop_le, khoa_noi_sang), ... ]) } }
# ==============================================================================
DICTIONARY_METADATA = {

    "01_BanHang": {
        "Dim_KhachHang": (
            "1 dòng = 1 khách hàng",
            [
                ("MaKhachHang", "VARCHAR(20)", "PK", "Mã định danh duy nhất của khách hàng", "KHxxxx (KH0001..KH0450)", ""),
                ("TenKhachHang", "NVARCHAR(250)", "Attribute", "Tên khách hàng — tên người nếu Loại=Lẻ, tên công ty nếu Loại=Sỉ", "Chuỗi ký tự tiếng Việt", ""),
                ("Vung", "NVARCHAR(50)", "Attribute", "Vùng địa lý của khách hàng", "Miền Bắc / Miền Trung / Miền Nam", ""),
                ("LoaiKhach", "VARCHAR(10)", "Attribute", "Phân loại khách hàng theo hình thức mua", "Sỉ / Lẻ", ""),
                ("NgayBatDauGiaoDich", "DATE", "Attribute", "Ngày khách hàng bắt đầu giao dịch với doanh nghiệp", "Ngày hợp lệ, trước DATE_START của kỳ dữ liệu", ""),
                ("HanMucCongNo", "DECIMAL(18,2)", "Attribute [NGOÀI ĐỀ BÀI]", "Hạn mức nợ tối đa được cấp, khác nhau theo LoaiKhach (Sỉ cao hơn Lẻ nhiều) — xem ASSUMPTIONS.md mục 9", "Sỉ: 200tr-800tr / Lẻ: 5tr-30tr VNĐ", ""),
            ],
        ),
        "Fact_DonHang": (
            "1 dòng = 1 đơn hàng",
            [
                ("MaDonHang", "VARCHAR(30)", "PK", "Mã định danh duy nhất của đơn hàng", "DHxxxxxx", ""),
                ("MaKhachHang", "VARCHAR(20)", "FK", "Khách hàng đặt đơn", "Phải tồn tại trong Dim_KhachHang", "Dim_KhachHang.MaKhachHang"),
                ("NgayDatHang", "DATETIME", "Attribute", "Thời điểm đặt hàng (đã cài trọng số mùa vụ theo tháng)", "Ngày giờ hợp lệ trong 24 tháng lịch sử", ""),
                ("KenhBan", "NVARCHAR(50)", "Attribute", "Kênh bán phát sinh đơn hàng", "TMĐT-Shopee/Lazada/Tiki, Đại lý, Bán lẻ trực tiếp, Showroom", ""),
                ("NhanVienBanHang", "VARCHAR(20)", "FK", "Nhân viên phụ trách đơn hàng", "Phải tồn tại trong Dim_NhanVienSales", "Dim_NhanVienSales.MaNhanVien"),
                ("TrangThai", "NVARCHAR(50)", "Attribute", "Trạng thái xử lý đơn hàng", "Mới / Đang xử lý / Đã giao / Đã hủy / Trả hàng", ""),
            ],
        ),
        "Fact_ChiTietDonHang": (
            "1 dòng = 1 dòng sản phẩm trong 1 đơn hàng (order line)",
            [
                ("MaChiTiet", "VARCHAR(30)", "PK", "Mã định danh duy nhất của dòng chi tiết", "CTxxxxxxx", ""),
                ("MaDonHang", "VARCHAR(30)", "FK", "Đơn hàng chứa dòng chi tiết này", "Phải tồn tại trong Fact_DonHang", "Fact_DonHang.MaDonHang"),
                ("MaSanPham", "VARCHAR(20)", "FK", "Sản phẩm được đặt mua", "Phải tồn tại trong Dim_SanPham", "Dim_SanPham.MaSanPham"),
                ("SoLuong", "INT", "Metric", "Số lượng sản phẩm trong dòng chi tiết", "Số nguyên dương", ""),
                ("GiaBanThucTe", "DECIMAL(18,2)", "Metric", "Đơn giá bán thực tế (có thể khác GiaNiemYet bên Dim_SanPham)", "VNĐ > 0", ""),
                ("ChietKhau", "DECIMAL(5,2)", "Metric", "Tỷ lệ chiết khấu áp dụng (dạng thập phân)", "0.00 - 0.30", ""),
            ],
        ),
    },

    "02_KeToan": {
        "Fact_HoaDonCongNoPhaiThu": (
            "1 dòng = 1 hóa đơn bán hàng / khoản công nợ phải thu",
            [
                ("MaHoaDon", "VARCHAR(30)", "PK", "Mã định danh duy nhất của hóa đơn", "HDxxxxxx", ""),
                ("MaDonHang", "VARCHAR(30)", "FK", "Đơn hàng phát sinh hóa đơn này", "Phải tồn tại trong Fact_DonHang", "Fact_DonHang.MaDonHang"),
                ("NgayXuatHoaDon", "DATE", "Attribute", "Ngày xuất hóa đơn (sau ngày đặt hàng 0-3 ngày)", "Ngày hợp lệ", ""),
                ("HanThanhToan", "DATE", "Attribute", "Hạn thanh toán (NgayXuatHoaDon + 30 ngày)", "Ngày hợp lệ, >= NgayXuatHoaDon", ""),
                ("SoTien", "DECIMAL(18,2)", "Metric", "Tổng tiền phải thu của hóa đơn", "VNĐ > 0", ""),
                ("DaThu", "DECIMAL(18,2)", "Metric", "Số tiền đã thu — mô phỏng tuổi nợ (đúng hạn/quá hạn 30-60-90/nợ khó đòi >180)", "0 <= DaThu <= SoTien (bản sạch)", ""),
                ("ConLai", "DECIMAL(18,2)", "Metric", "Số tiền còn phải thu = SoTien - DaThu", "= SoTien - DaThu (bản sạch)", ""),
            ],
        ),
        "Fact_CongNoPhaiTra": (
            "1 dòng = 1 khoản công nợ phải trả nhà cung cấp",
            [
                ("MaCongNoPhaiTra", "VARCHAR(30)", "PK", "Mã định danh duy nhất của khoản công nợ phải trả", "CNTxxxxxx", ""),
                ("MaDonMuaHang", "VARCHAR(30)", "FK", "Đơn mua hàng phát sinh công nợ", "Phải tồn tại trong Fact_DonMuaHang", "Fact_DonMuaHang.MaDonMuaHang"),
                ("MaNhaCungCap", "VARCHAR(20)", "FK", "Nhà cung cấp được nợ tiền", "Phải tồn tại trong Dim_NhaCungCap", "Dim_NhaCungCap.MaNhaCungCap"),
                ("NgayHoaDon", "DATE", "Attribute", "Ngày hóa đơn mua hàng (sau ngày đặt mua 1-5 ngày)", "Ngày hợp lệ", ""),
                ("HanThanhToan", "DATE", "Attribute", "Hạn thanh toán (NgayHoaDon + 45 ngày)", "Ngày hợp lệ, >= NgayHoaDon", ""),
                ("SoTien", "DECIMAL(18,2)", "Metric", "Tổng tiền phải trả = SoLuong × DonGiaMua", "VNĐ > 0", ""),
                ("DaTra", "DECIMAL(18,2)", "Metric", "Số tiền đã trả cho NCC — mô phỏng tuổi nợ tương tự công nợ phải thu", "0 <= DaTra <= SoTien (bản sạch)", ""),
                ("ConLai", "DECIMAL(18,2)", "Metric", "Số tiền còn phải trả = SoTien - DaTra", "= SoTien - DaTra (bản sạch)", ""),
            ],
        ),
        "Fact_ChiPhi": (
            "1 dòng = 1 khoản mục chi phí trong 1 tháng",
            [
                ("MaChiPhi", "VARCHAR(20)", "PK", "Mã định danh duy nhất của dòng chi phí", "CPxxxxx", ""),
                ("Thang", "VARCHAR(10)", "Attribute (Key)", "Tháng phát sinh chi phí", "yyyy-mm", ""),
                ("KhoanMuc", "NVARCHAR(100)", "Attribute", "Khoản mục chi phí", "Lương NV, Thuê mặt bằng, Marketing, Vận chuyển, Điện nước VP, Khấu hao TB, Chi phí khác", ""),
                ("SoTien", "DECIMAL(18,2)", "Metric", "Số tiền chi phí (Marketing/Vận chuyển có hệ số mùa vụ)", "VNĐ > 0", ""),
            ],
        ),
        "Dim_GiaVon": (
            "1 dòng = 1 sản phẩm (giá vốn hiện hành)",
            [
                ("MaSanPham", "VARCHAR(20)", "PK / FK", "Sản phẩm áp dụng giá vốn", "Phải tồn tại trong Dim_SanPham", "Dim_SanPham.MaSanPham"),
                ("GiaVon", "DECIMAL(18,2)", "Metric", "Giá vốn — tỷ lệ GiaVon/GiaNiemYet khác nhau theo NhomHang (biên lợi nhuận)", "VNĐ > 0, < GiaNiemYet (bản sạch)", ""),
            ],
        ),
    },

    "03_Kho_MuaHang": {
        "Dim_SanPham": (
            "1 dòng = 1 sản phẩm",
            [
                ("MaSanPham", "VARCHAR(20)", "PK", "Mã định danh duy nhất của sản phẩm", "SPxxxx (SP0001..SP0220)", ""),
                ("TenSanPham", "NVARCHAR(250)", "Attribute", "Tên sản phẩm — luôn khớp đúng NhomHang tương ứng", "Chuỗi ký tự tiếng Việt", ""),
                ("NhomHang", "NVARCHAR(100)", "Attribute", "Nhóm hàng — quyết định biên lợi nhuận (xem Dim_GiaVon)", "Nguyên liệu đầu vào / Thực phẩm chế biến / Đồ uống / Gia dụng", ""),
                ("DonViTinh", "NVARCHAR(20)", "Attribute", "Đơn vị tính", "Thùng / Hộp / Kg / Tấn / Cái", ""),
                ("GiaNiemYet", "DECIMAL(18,2)", "Metric", "Giá bán niêm yết", "VNĐ > 0", ""),
                ("HanSuDungNgay", "INT", "Attribute [NGOÀI ĐỀ BÀI]", "Hạn sử dụng tính bằng ngày kể từ ngày sản xuất — chỉ có ý nghĩa với Nguyên liệu/Thực phẩm chế biến/Đồ uống; Gia dụng để trống (không phải hàng thực phẩm) — xem ASSUMPTIONS.md mục 9", "180-730 ngày hoặc rỗng (Gia dụng)", ""),
            ],
        ),
        "Dim_NhaCungCap": (
            "1 dòng = 1 nhà cung cấp",
            [
                ("MaNhaCungCap", "VARCHAR(20)", "PK", "Mã định danh duy nhất của nhà cung cấp", "NCCxxx (NCC001..NCC045)", ""),
                ("TenNhaCungCap", "NVARCHAR(250)", "Attribute", "Tên nhà cung cấp (công ty kiểu Việt Nam)", "Chuỗi ký tự tiếng Việt", ""),
                ("Vung", "NVARCHAR(50)", "Attribute", "Vùng địa lý của nhà cung cấp", "Miền Bắc / Miền Trung / Miền Nam", ""),
                ("NgayHopTac", "DATE", "Attribute", "Ngày bắt đầu hợp tác", "Ngày hợp lệ, trước DATE_START của kỳ dữ liệu", ""),
            ],
        ),
        "Fact_NhapXuatTonKho": (
            "1 dòng = 1 sản phẩm x 1 tháng (snapshot tồn kho)",
            [
                ("MaSanPham", "VARCHAR(20)", "PK Composite / FK", "Sản phẩm được chốt tồn", "Phải tồn tại trong Dim_SanPham", "Dim_SanPham.MaSanPham"),
                ("Thang", "VARCHAR(10)", "PK Composite", "Tháng chốt tồn kho", "yyyy-mm", ""),
                ("TonDauKy", "INT", "Metric", "Tồn kho đầu kỳ (= TonCuoiKy tháng trước)", "Số nguyên >= 0", ""),
                ("Nhap", "INT", "Metric", "Số lượng nhập trong kỳ (có hệ số mùa vụ + tốc độ luân chuyển SP)", "Số nguyên >= 0", ""),
                ("Xuat", "INT", "Metric", "Số lượng xuất trong kỳ (SP luân chuyển nhanh/chậm/tồn đọng)", "Số nguyên >= 0", ""),
                ("HaoHut", "INT", "Metric [NGOÀI ĐỀ BÀI]", "Số lượng hao hụt trong kỳ (hư hỏng/hết hạn), tỷ lệ khác nhau theo nhóm hàng — xem ASSUMPTIONS.md mục 9", "Số nguyên >= 0, tính theo % lượng Nhập", ""),
                ("TonCuoiKy", "INT", "Metric", "Tồn cuối kỳ = TonDauKy + Nhap - Xuat - HaoHut", "= TonDauKy + Nhap - Xuat - HaoHut (bản sạch)", ""),
            ],
        ),
        "Fact_DonMuaHang": (
            "1 dòng = 1 đơn mua hàng từ nhà cung cấp",
            [
                ("MaDonMuaHang", "VARCHAR(30)", "PK", "Mã định danh duy nhất của đơn mua hàng", "POxxxxxx", ""),
                ("MaNhaCungCap", "VARCHAR(20)", "FK", "Nhà cung cấp của đơn mua", "Phải tồn tại trong Dim_NhaCungCap", "Dim_NhaCungCap.MaNhaCungCap"),
                ("MaSanPham", "VARCHAR(20)", "FK", "Sản phẩm được mua", "Phải tồn tại trong Dim_SanPham", "Dim_SanPham.MaSanPham"),
                ("NgayDatHang", "DATE", "Attribute", "Ngày lập đơn mua hàng", "Ngày hợp lệ trong 24 tháng lịch sử", ""),
                ("SoLuong", "INT", "Metric", "Số lượng đặt mua", "Số nguyên dương", ""),
                ("DonGiaMua", "DECIMAL(18,2)", "Metric", "Đơn giá mua (35-70% GiaNiemYet)", "VNĐ > 0, < GiaNiemYet tương ứng", ""),
            ],
        ),
    },

    "04_ExcelPhongBan": {
        "Dim_NhanVienSales": (
            "1 dòng = 1 nhân viên kinh doanh",
            [
                ("MaNhanVien", "VARCHAR(20)", "PK", "Mã định danh duy nhất của nhân viên", "NVxx (NV01..NV30)", ""),
                ("TenNhanVien", "NVARCHAR(150)", "Attribute", "Tên nhân viên (kiểu Việt Nam)", "Chuỗi ký tự tiếng Việt", ""),
                ("KhuVucPhuTrach", "NVARCHAR(50)", "Attribute", "Khu vực phụ trách — quyết định hệ số kế hoạch (xem Fact_ChiTieuKeHoach)", "Miền Bắc / Miền Trung / Miền Nam", ""),
                ("ChucVu", "NVARCHAR(50)", "Attribute", "Chức vụ", "Nhân viên/Trưởng nhóm/Giám sát Kinh doanh, Senior Sales", ""),
                ("NgayVaoLam", "DATE", "Attribute", "Ngày vào làm", "Ngày hợp lệ, trước DATE_START của kỳ dữ liệu", ""),
            ],
        ),
        "Fact_ChiTieuKeHoach": (
            "1 dòng = 1 tháng x 1 vùng x 1 nhân viên",
            [
                ("Thang", "VARCHAR(10)", "PK Composite", "Tháng áp dụng chỉ tiêu", "yyyy-mm", ""),
                ("Vung", "NVARCHAR(50)", "PK Composite", "Vùng áp dụng — có hệ số vượt/không đạt kế hoạch riêng theo vùng", "Miền Bắc / Miền Trung / Miền Nam", ""),
                ("MaNhanVien", "VARCHAR(20)", "PK Composite / FK", "Nhân viên được giao chỉ tiêu (thuộc đúng Vung)", "Phải tồn tại trong Dim_NhanVienSales", "Dim_NhanVienSales.MaNhanVien"),
                ("ChiTieuDoanhThu", "DECIMAL(18,2)", "Metric", "Chỉ tiêu doanh thu kế hoạch — tính từ doanh thu thực tế x hệ số vùng, nên thực-tế-vs-kế-hoạch luôn có chênh", "VNĐ > 0", ""),
            ],
        ),
        "Dim_PhanNhomKhachHang": (
            "1 dòng = 1 khách hàng ĐÃ ĐƯỢC phòng KD phân nhóm (chỉ phủ ~70-90% Dim_KhachHang — cố ý KHÔNG đầy đủ)",
            [
                ("MaKhachHang", "VARCHAR(20)", "PK / FK", "Khách hàng được phân nhóm", "Tập con của Dim_KhachHang.MaKhachHang (không đầy đủ)", "Dim_KhachHang.MaKhachHang"),
                ("TenKhachHang", "NVARCHAR(250)", "Attribute", "Tên khách hàng do phòng KD tự ghi lại (không đồng bộ tự động)", "Chuỗi ký tự tiếng Việt", ""),
                ("NhomKH", "NVARCHAR(50)", "Attribute", "Phân nhóm khách hàng do phòng KD tự đặt", "VIP / Thân thiết / Thường / Mới / Tiềm năng", ""),
            ],
        ),
    },
}


def build_data_dictionary() -> pd.DataFrame:
    """Gop toan bo DICTIONARY_METADATA thanh 1 DataFrame phang (PHAN 5 de bai)."""
    rows = []
    for he_thong, bang_dict in DICTIONARY_METADATA.items():
        for ten_bang, (grain, cols) in bang_dict.items():
            for (ten_cot, kieu, vai_tro, y_nghia, gia_tri_hople, khoa_noi_sang) in cols:
                rows.append({
                    "HeThongNguon": he_thong,
                    "TenBang": ten_bang,
                    "Grain": grain,
                    "TenCot": ten_cot,
                    "KieuDuLieu": kieu,
                    "VaiTro": vai_tro,
                    "YNghiaNghiepVu": y_nghia,
                    "GiaTriHopLe": gia_tri_hople,
                    "KhoaNoiSangBang": khoa_noi_sang,
                })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build_data_dictionary()
    print(df.to_string(index=False))
    print(f"\nTong so dong (cot) trong Data Dictionary: {len(df)}")

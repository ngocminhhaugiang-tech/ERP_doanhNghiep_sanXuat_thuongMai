# GIẢ ĐỊNH ĐÃ DÙNG — Bài tập Tuần 2 (sinh dữ liệu 4 hệ thống nguồn)

Đề bài mô tả các trường chính cần có ở mức khái niệm ("mã khách, tên, vùng, loại
khách..."), không quy định chi tiết kiểu dữ liệu, tên cột cụ thể, quy mô chính
xác hay tham số của các quy luật nghiệp vụ. Mọi chỗ phải tự quyết được ghi lại
ở đây, theo đúng tinh thần "Ghi lại giả định" của Tuần 1.

## 1. Bảng phát sinh thêm ngoài danh sách bắt buộc

- **`Dim_NhaCungCap`** (mã, tên, vùng, ngày hợp tác) — đề bài chỉ nhắc tới nhà
  cung cấp gián tiếp qua "Đơn mua hàng từ nhà cung cấp" (Hệ thống kho) và
  "Công nợ phải trả nhà cung cấp" (Hệ thống kế toán), không liệt kê đây là 1
  bảng riêng. Bảng này được thêm vì `Fact_DonMuaHang` và `Fact_CongNoPhaiTra`
  cần một đối tượng để tra cứu tên/vùng nhà cung cấp — nếu không có, không thể
  tạo cột `MaNhaCungCap` có ý nghĩa.

## 2. Quy mô cụ thể (Phần 4 đề bài chỉ cho khung gợi ý)

Chọn giá trị nằm giữa khung gợi ý, trừ các đối tượng đề bài không cho khung:

| Đối tượng | Khung đề bài | Giá trị đã chọn |
|---|---|---|
| Khách hàng | 300 - 600 | 450 |
| Sản phẩm | 150 - 300 | 220 |
| Đơn hàng | 8.000 - 15.000 | 12.000 |
| Nhân viên bán hàng | 20 - 40 | 30 |
| Nhà cung cấp | *(không có khung)* | 45 — chọn tương tự thang khách hàng/sản phẩm, hợp lý cho quy mô 1 doanh nghiệp vừa |
| Đơn mua hàng | *(không có khung)* | 3.500 — chọn tỷ lệ tương đối so với đơn bán (~30%), vì mua NVL thường ít lần hơn bán lẻ |
| Số dòng chi tiết / 1 đơn hàng | *(không có khung)* | 1 - 4 dòng/đơn (ngẫu nhiên) |
| Số tháng lịch sử | 24 tháng | 24 tháng — dùng đúng gợi ý, kết thúc gần thời điểm hiện tại (DATE_END = 2026-07-31) |

## 3. Danh mục giá trị chuẩn (đề bài không liệt kê chi tiết)

- **Nhóm hàng**: Nguyên liệu đầu vào / Thực phẩm chế biến / Đồ uống / Gia dụng
  — chọn theo hướng "ngành thực phẩm" (đề bài dùng ví dụ mùa vụ ngành thực
  phẩm ở Phần 3), thêm nhóm Gia dụng để có ít nhất 1 nhóm biên lợi nhuận khác
  hẳn phần còn lại.
- **Đơn vị tính chuẩn**: Thùng / Hộp / Kg / Tấn / Cái — chọn theo đúng ví dụ đề
  bài đưa ra ở Phần 2, mục "Đơn vị tính không thống nhất".
- **Kênh bán**: TMĐT-Shopee/Lazada/Tiki, Đại lý, Bán lẻ trực tiếp, Showroom —
  tự chọn, không có yêu cầu cụ thể.
- **Khoản mục chi phí**: Lương nhân viên, Thuê mặt bằng, Marketing, Vận
  chuyển, Điện nước văn phòng, Khấu hao thiết bị, Chi phí khác — tự chọn danh
  mục điển hình của doanh nghiệp thương mại vừa.
- **Chức vụ Sales, Loại khách (Sỉ/Lẻ), Vùng (Bắc/Trung/Nam)** — Vùng và
  Loại khách dùng đúng chữ đề bài ("vùng", "loại khách: sỉ hoặc lẻ"); Chức vụ
  tự thêm để dữ liệu nhân viên đầy đủ hơn.

## 4. Tham số cụ thể hóa các quy luật nghiệp vụ (Phần 3 đề bài)

Đề bài mô tả các quy luật ở mức định tính ("phải có mùa cao điểm/thấp điểm",
"phải có tuổi nợ đa dạng"...), không cho số liệu. Các con số cụ thể đã tự chọn:

- **Hệ số mùa vụ theo tháng**: cao nhất tháng 12 (×1.55) và tháng 1 (×1.35),
  thấp nhất tháng 2 (×0.70) — mô phỏng cao điểm Tết / thấp điểm sau Tết như đề
  bài mô tả cho "ngành thực phẩm".
- **Tuổi nợ**: chia 5 nhóm — đúng hạn / quá hạn 30 / quá hạn 60 / quá hạn 90 /
  nợ khó đòi >180 ngày, với xác suất 55% / 18% / 12% / 8% / 7%. Tỷ lệ đã
  thu-trả tương ứng mỗi nhóm cũng tự chọn khoảng hợp lý (vd nợ khó đòi chỉ thu
  được 0-20%).
- **Tốc độ luân chuyển tồn kho**: 3 nhóm — bán chạy (65%) / bán chậm (25%) /
  không bán được (10%), gắn cố định cho từng sản phẩm xuyên suốt 24 tháng.
- **Biên lợi nhuận theo nhóm hàng**: tỷ lệ GiaVon/GiaNiemYet — Nguyên liệu đầu
  vào 82-92% (biên thấp), Thực phẩm chế biến 45-65% (biên cao), Đồ uống
  50-68%, Gia dụng 55-72%. **Áp dụng đồng bộ cho cả `Dim_GiaVon` (giá vốn kế
  toán) và `Fact_DonMuaHang.DonGiaMua` (giá mua thực tế)** — giá mua gốc lấy
  thấp hơn giá vốn hạch toán một chút (nhân thêm hệ số 0.85-0.95) vì giá vốn
  còn cộng thêm chi phí phụ trội (vận chuyển, hao hụt, phân bổ).
- **Hệ số vùng cho chỉ tiêu kế hoạch**: Miền Bắc ×0.85 (dễ vượt kế hoạch),
  Miền Trung ×1.20 (khó đạt), Miền Nam ×0.95 — để đảm bảo luôn có vùng vượt,
  có vùng không đạt như đề bài yêu cầu.
- **Phân bố khách hàng**: dùng phân phối Pareto (tham số a=1.4) để tạo hiệu
  ứng "20% khách hàng lớn chiếm phần lớn doanh thu" — chỉ dùng nội bộ để sinh
  `Fact_DonHang`, không xuất ra thành cột trong bảng giao nộp.

## 5. Tỷ lệ gieo lỗi khi đề bài không cho số cụ thể

Các loại lệch có số % rõ ràng trong đề bài (mã lệch định dạng 70-95%, tên
khách hàng 15-20%, giá trị thiếu 3-5%, orphan FK 2-3%, hai nguồn giá 20-25%,
bản ghi trùng 1-2%) đều dùng đúng khung đã cho. Với 2 loại còn lại đề bài
không cho số, đã tự chọn:

- **Ngày lệch định dạng**: 3-6% ở hệ thống Sales/Kế toán/Kho, riêng file Excel
  phòng ban cao hơn (10-15%) — theo đúng mô tả "đặc biệt hay gặp ở file Excel
  do người nhập tay".
- **Đơn vị tính không thống nhất**: 20-30% danh mục sản phẩm bị đổi nhãn đơn
  vị (Thùng↔Hộp, Kg↔Tấn); riêng với `Fact_NhapXuatTonKho`, thêm 5-10% số dòng
  bị nhân/chia 1.000 để mô phỏng đúng ví dụ "số lượng ghi theo kg và theo tấn
  lẫn lộn" (không chỉ đổi nhãn mà đổi luôn độ lớn con số).

Riêng nguồn Excel phòng ban (Phần 1, mục 4 đề bài gọi là *"nguồn bẩn nhất"*):
áp tỷ lệ lệch mã cao hơn hẳn (80-98% thay vì 70-95%) và tỷ lệ tên viết khác
nhau cũng cao hơn (30-45% thay vì 15-20%) để thể hiện đúng tính chất "bẩn
nhất" mà đề bài mô tả.

## 6. Bảng phân nhóm khách hàng (`Dim_PhanNhomKhachHang`) không đầy đủ

Đề bài mô tả đây là "nguồn bẩn nhất" nhưng không nói rõ "bẩn" theo nghĩa nào.
Tự diễn giải thêm 1 dạng lỗi đặc trưng của bảng Excel do người tự duy trì:
**không đồng bộ tự động nên chỉ phủ được 70-90% tổng số khách hàng** (ngẫu
nhiên mỗi lần chạy) — mô phỏng việc nhân viên phòng kinh doanh bỏ sót khách
khi tự cập nhật tay, khác với lỗi kiểu "sai giá trị" ở các bảng khác.

## 7. Quy tắc "mã lệch định dạng theo hệ thống" (loại lệch #1)

Đề bài chỉ cho 1 ví dụ (Sales=KH001, Excel=KH-001, KeToan=kh001). Tự khái
quát hóa thành quy tắc áp dụng nhất quán cho MỌI mã khóa xuất hiện ở 4 hệ
thống:

| Hệ thống | Quy tắc biến đổi mã |
|---|---|
| Sales | giữ nguyên gốc (hệ thống chuẩn) |
| Kế toán | chuyển thành chữ thường (`kh0001`) |
| Kho | giữ nguyên gốc (dùng chung định dạng với Sales trong bộ này) |
| Excel phòng ban | chèn dấu gạch ngang sau phần chữ cái (`KH-0001`) |

## 8. Seed và mốc thời gian

- `SEED = 42` cố định cho `random` và `numpy` — đảm bảo chạy lại ra đúng bộ cũ
  như tiêu chuẩn nghiệm thu yêu cầu.
- `DATE_END = 2026-07-31`, `DATE_START = 2024-08-01` — chọn mốc kết thúc gần
  sát thời điểm làm bài, lùi lại đúng 24 tháng.

## 9. Mở rộng thêm NGOÀI đề bài — lấy cảm hứng từ ERP thực phẩm thực tế VN

Sau khi đã có bản đầu đúng 100% yêu cầu đề bài, có tham khảo thêm 1 tài liệu
mô tả mô hình dữ liệu ERP thương mại thực phẩm thực tế (Catch Weight, FEFO,
Landed Cost, hạn mức công nợ theo kênh MT/GT/HORECA...). Quyết định **KHÔNG**
thêm bảng mới, **KHÔNG** đổi tên/cấu trúc các bảng đề bài đã yêu cầu, chỉ thêm
1 số field + tinh chỉnh logic trên 13 bảng đã có, và chỉ áp dụng phần **phù
hợp với danh mục sản phẩm đang dùng** (hàng đóng gói sẵn: bột mì, đường, dầu
ăn, snack, bánh, mì gói, nước ngọt, đồ gia dụng — không phải hàng tươi sống
cân trực tiếp), nên **bỏ qua hoàn toàn Catch Weight, FEFO theo lô, Landed
Cost** vì cần có bảng quản lý lô hàng (`inventory_batches`) mới thực sự có ý
nghĩa, trong khi phạm vi cho phép chỉ là "thêm field", không "thêm bảng".

**Field mới đã thêm** (đều đánh dấu `[NGOÀI ĐỀ BÀI]` trong Data Dictionary):

| Bảng | Field mới | Lý do |
|---|---|---|
| `Dim_SanPham` | `HanSuDungNgay` | Hạn sử dụng (ngày) kể từ sản xuất — chỉ có ý nghĩa với Nguyên liệu/Thực phẩm chế biến/Đồ uống; Gia dụng để trống vì không phải hàng thực phẩm |
| `Dim_KhachHang` | `HanMucCongNo` | Hạn mức nợ tối đa — Sỉ được cấp cao hơn Lẻ nhiều, phỏng theo tinh thần `credit_limit_amount` của MT/GT trong tài liệu tham khảo |
| `Fact_NhapXuatTonKho` | `HaoHut` | Số lượng hao hụt trong kỳ (hư hỏng/hết hạn) — tỷ lệ khác nhau theo nhóm hàng, trừ trực tiếp vào công thức `TonCuoiKy` |

**Logic đã tinh chỉnh thêm** (không thêm field, chỉ đổi cách sinh số):

- **Mùa vụ theo nhóm hàng**: ngoài hệ số mùa vụ chung theo tháng (đã có từ
  đầu), `SoLuong` mỗi dòng chi tiết đơn hàng giờ nhân thêm 1 hệ số riêng theo
  nhóm hàng — Thực phẩm chế biến tăng mạnh dịp Tết, Đồ uống tăng thêm vào mùa
  hè (phỏng theo ý "mùa du lịch" của HORECA trong tài liệu), Nguyên liệu đầu
  vào hầu như không đổi (sản xuất liên tục quanh năm).
- **Tuổi nợ + hạn thanh toán theo Loại khách**: trước đây dùng chung 1 phân
  bố tuổi nợ cho mọi khách hàng; giờ tách riêng theo `LoaiKhach` — Sỉ có hạn
  thanh toán dài hơn (45-90 ngày) và tỷ lệ trễ hạn cao hơn hẳn (~55% không
  đúng hạn), Lẻ có hạn ngắn (7-15 ngày) và hầu như luôn đúng hạn (~85%).
  Phỏng theo đúng tinh thần khác biệt MT (trả chậm, hay trễ) vs GT (trả
  nhanh, ít trễ) trong tài liệu tham khảo, ánh xạ qua field `LoaiKhach` sẵn có
  thay vì thêm field `channel_type` mới.

**Lưu ý quan trọng khi dùng `HanMucCongNo` để phân tích sau này**: đây là hạn
mức tại **một thời điểm** (giống hạn mức thẻ tín dụng), còn `ConLai` trong
`Fact_HoaDonCongNoPhaiThu` là số dư CHƯA THU của **từng hóa đơn riêng lẻ**. Bộ
dữ liệu này KHÔNG có khái niệm "ngày hiện tại"/snapshot, nên **KHÔNG được**
cộng dồn `ConLai` của TẤT CẢ hóa đơn trong 24 tháng rồi so với `HanMucCongNo`
— làm vậy sẽ luôn thấy "vượt hạn mức" rất nhiều (vì nợ khó đòi >180 ngày
trong model này không có cơ chế xóa/tất toán, cứ cộng dồn mãi qua các tháng).
Muốn kiểm tra "khách có đang vượt hạn mức không", cần chọn 1 mốc thời gian cụ
thể rồi chỉ cộng `ConLai` của các hóa đơn **còn treo tại đúng mốc đó**, không
cộng dồn toàn bộ lịch sử.

**Không áp dụng** (và lý do):
- Catch Weight (cân nặng thực tế biến động ±5%) — chỉ có ý nghĩa với hàng
  tươi cân trực tiếp (thịt/cá/rau), không hợp với danh mục hàng đóng gói sẵn
  đang dùng (bao/thùng/chai đã đóng gói cố định trọng lượng).
- FEFO theo lô hàng cụ thể, Landed Cost phân bổ theo lô — cần bảng quản lý
  lô hàng (`inventory_batches`) riêng mới có ý nghĩa thực chất; nằm ngoài
  phạm vi "chỉ thêm field, không thêm bảng" đã thống nhất.
- Trạng thái duyệt tín dụng (`credit_check_status`, khóa đơn khi vượt hạn
  mức) — không thêm field mới cho việc này; `HanMucCongNo` chỉ mang tính
  tham khảo/đối chiếu (so sánh với `ConLai` khi phân tích), không dùng để
  chặn đơn hàng trong lúc sinh dữ liệu.


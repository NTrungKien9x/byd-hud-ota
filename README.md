# BYD HUD — Web Nạp Firmware Online & Cập Nhật OTA qua GitHub Pages

Thư mục này đã chứa sẵn toàn bộ trang web nạp USB (ESP Web Tools) và các file `.bin` đã biên dịch sẵn cho cả 2 loại màn hình:
- **Bản V1 (`firmware/byd_hud_v1.bin`)**: Màn hình **SKU 10120005 (2509)**
- **Bản V2 (`firmware/byd_hud_v2.bin`)**: Màn hình **SKU 10120003 (2636)**

## Hướng dẫn đưa lên GitHub Pages (chỉ mất ~2 phút, không cần cài Git)

1. **Đăng nhập GitHub** bằng tài khoản **`NTrungKien9x`** (`sumire111111@gmail.com`).
2. **Tạo Repository mới** tại: https://github.com/new
   - Repository name: `byd-hud-ota`
   - Chọn **Public** → bấm **Create repository**.
3. **Tải toàn bộ file lên Repo**:
   - Bấm dòng **uploading an existing file** trên trang repo vừa tạo.
   - Kéo thả toàn bộ các file & thư mục `firmware/` bên trong thư mục `github_ota_web` (trừ `build_release.py`/`build_release.bat` nếu không cần) vào trình duyệt → bấm **Commit changes**.
4. **Bật GitHub Pages**:
   - Vào **Settings** → **Pages** → mục **Branch** chọn `main` và `/ (root)` → bấm **Save**.
   - Đợi ~1 phút, trang web nạp firmware online của bạn sẽ hoạt động tại:
     `https://ntrungkien9x.github.io/byd-hud-ota/`

## Cách phát hành bản cập nhật mới sau này
1. Sửa code trong Arduino sketch `HUD_BYD_Dolphin`, tăng số phiên bản `#define BLE_HUD_FW_STR "2.61"`.
2. Chạy đúp file `build_release.bat` → tự động đồng bộ V1/V2, biên dịch 2 file `.bin` và cập nhật `version.json`.
3. Tải đè `version.json`, `manifest_v1.json`, `manifest_v2.json` và thư mục `firmware/` lên GitHub → mọi HUD kết nối WiFi chỉ cần bấm **CẬP NHẬT ONLINE** là tự nâng cấp!

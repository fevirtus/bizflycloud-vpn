#!/bin/bash

# Hàm parse argument
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --secret)
                secret="$2"
                shift 2
                ;;
            --secret_qr)
                secret_qr="$2"
                shift 2
                ;;
            --password)
                password="$2"
                shift 2
                ;;
            --usr)
                usr="$2"
                shift 2
                ;;
            --sudo_pass)
                sudo_pass="$2"
                shift 2
                ;;
            --vpn_config)
                vpn_config="$2"
                shift 2
                ;;
            *)
                echo "Tham số không hợp lệ: $1"
                exit 1
                ;;
        esac
    done

    if [[ -z "$password" || -z "$usr" || -z "$sudo_pass" || -z "$vpn_config" ]]; then
        echo "Các tham số --password, --usr, --sudo_pass, và --vpn_config là bắt buộc."
        exit 1
    fi

    if [[ -z "$secret" && -z "$secret_qr" ]]; then
        echo "Cần chỉ định ít nhất một trong các tùy chọn --secret hoặc --secret_qr."
        exit 1
    fi
}

# Hàm lấy secret từ QR code
get_secret_from_qr() {
    local qr_image_path="$1"
    local secret

    secret=$(python3 - <<EOF
import cv2
import pyotp
import sys

try:
    img = cv2.imread("$qr_image_path")
    if img is None:
        print("Không thể mở ảnh, vui lòng kiểm tra đường dẫn.")
        sys.exit(1)

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    if not data:
        print("Không tìm thấy mã QR trong ảnh.")
        sys.exit(1)

    if not data.startswith("otpauth://totp/"):
        print("Mã QR không phải định dạng TOTP.")
        sys.exit(1)

    secret = pyotp.parse_uri(data).secret
    print(secret)
except Exception as e:
    print(f"Lỗi khi đọc mã QR: {e}")
    sys.exit(1)
EOF
)
    echo "$secret"
}

# Hàm tạo mã OTP
get_auth_code() {
    local secret="$1"
    local password="$2"
    local otp_with_pass

    otp_with_pass=$(python3 - <<EOF
import pyotp

try:
    totp = pyotp.TOTP("$secret")
    code = totp.now()
    print(code + "$password")
except Exception as e:
    print(f"Lỗi: {e}")
    sys.exit(1)
EOF
)
    echo "$otp_with_pass"
}

# Hàm kết nối VPN
connect_vpn() {
    local otp_with_pass="$1"
    local sudo_pass="$2"
    local vpn_config="$3"
    local usr="$4"

    local auth_file_path="/tmp/vpn_auth.txt"
    echo -e "$usr\n$otp_with_pass" > "$auth_file_path"

    echo "$sudo_pass" | sudo -S openvpn --config "$vpn_config" --auth-user-pass "$auth_file_path"
    rm -f "$auth_file_path"
}

# Main script
parse_args "$@"

if [[ -n "$secret_qr" ]]; then
    secret_key=$(get_secret_from_qr "$secret_qr")
else
    secret_key="$secret"
fi

otp_with_pass=$(get_auth_code "$secret_key" "$password")
connect_vpn "$otp_with_pass" "$sudo_pass" "$vpn_config" "$usr"
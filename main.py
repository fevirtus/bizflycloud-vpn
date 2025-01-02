import cv2
import pyotp
import pyperclip
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Tạo mã OTP từ secret hoặc mã QR và mật khẩu.')
    
    parser.add_argument('--secret', type=str, help='Secret key cho OTP (chuỗi)')
    parser.add_argument('--secret_qr', type=str, help='Đường dẫn đến ảnh mã QR chứa secret key')
    parser.add_argument('--password', type=str, required=True, help='Mật khẩu người dùng để thêm vào sau OTP')

    args = parser.parse_args()
    
    if not args.secret and not args.secret_qr:
        print("Cần chỉ định ít nhất một trong các tùy chọn --secret hoặc --secret_qr.")
        sys.exit(1)
    
    return args

def get_secret_from_qr(qr_image_path):
    try:
        img = cv2.imread(qr_image_path)
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
        print(f"Lấy secret key thành công: {secret}")
        return secret
    except Exception as e:
        print(f"Lỗi khi đọc mã QR: {e}")
        sys.exit(1)

def get_auth_code(secret, password):
    try:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        otp_with_pass = code + password
        pyperclip.copy(otp_with_pass)
        print(f"Mã OTP với mật khẩu: {otp_with_pass} (đã sao chép vào clipboard)")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    args = parse_args()
    
    secret = args.secret
    secret_qr = args.secret_qr
    password = args.password

    if secret_qr:
        secret_key = get_secret_from_qr(secret_qr)
    else:
        secret_key = secret

    get_auth_code(secret_key, password)
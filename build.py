# build.py
import PyInstaller.__main__
import os
import platform
import sys
import shutil

def optimize_code():
    """Tối ưu hóa mã nguồn trước khi build"""
    optimized_code = """
import cv2
import pyotp
import sys
import argparse
import subprocess
from typing import Optional

class VPNConnector:
    def __init__(self, args):
        self.secret = args.secret
        self.secret_qr = args.secret_qr
        self.usr = args.usr
        self.password = args.password
        self.sudo_pass = args.sudo_pass
        self.vpn_config = args.vpn_config
        self.detector = cv2.QRCodeDetector()

    def get_secret_from_qr(self, qr_image_path: str) -> str:
        img = cv2.imread(qr_image_path)
        if img is None:
            raise ValueError("Không thể mở ảnh, vui lòng kiểm tra đường dẫn.")

        data, _, _ = self.detector.detectAndDecode(img)
        if not data:
            raise ValueError("Không tìm thấy mã QR trong ảnh.")

        if not data.startswith("otpauth://totp/"):
            raise ValueError("Mã QR không phải định dạng TOTP.")

        secret = pyotp.parse_uri(data).secret
        print(f"Lấy secret key thành công: {secret}")
        return secret

    def get_auth_code(self, secret: str) -> str:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        otp_with_pass = code + self.password
        print(f"Mã OTP với mật khẩu: {otp_with_pass}")
        return otp_with_pass

    def connect_vpn(self, otp_with_pass: str) -> None:
        auth_file_path = '/tmp/vpn_auth.txt'
        try:
            with open(auth_file_path, 'w') as f:
                f.write(f"{self.usr}\\n{otp_with_pass}\\n")

            subprocess.run(
                ['sudo', '-S', 'openvpn', '--config', self.vpn_config, '--auth-user-pass', auth_file_path],
                input=self.sudo_pass.encode(),
                check=True
            )
            print("Kết nối OpenVPN thành công!")
        except subprocess.CalledProcessError as e:
            print(f"Lỗi khi kết nối OpenVPN: {e}")
        finally:
            if os.path.exists(auth_file_path):
                os.remove(auth_file_path)

def parse_args():
    parser = argparse.ArgumentParser(description='Tạo mã OTP từ secret hoặc mã QR và mật khẩu.')
    
    parser.add_argument('--secret', type=str, help='Secret key cho OTP (chuỗi)')
    parser.add_argument('--secret_qr', type=str, help='Đường dẫn đến ảnh mã QR chứa secret key')
    parser.add_argument('--password', type=str, required=True, help='Mật khẩu người dùng để thêm vào sau OTP')
    parser.add_argument('--usr', type=str, required=True, help='Tên người dùng OpenVPN')
    parser.add_argument('--sudo_pass', type=str, required=True, help='Mật khẩu sudo')
    parser.add_argument('--vpn_config', type=str, required=True, help='Đường dẫn đến file cấu hình OpenVPN')

    args = parser.parse_args()
    
    if not args.secret and not args.secret_qr:
        print("Cần chỉ định ít nhất một trong các tùy chọn --secret hoặc --secret_qr.")
        sys.exit(1)
    
    return args

def main():
    args = parse_args()
    connector = VPNConnector(args)
    
    try:
        if args.secret_qr:
            secret_key = connector.get_secret_from_qr(args.secret_qr)
        else:
            secret_key = args.secret

        otp_with_pass = connector.get_auth_code(secret_key)
        connector.connect_vpn(otp_with_pass)
    except Exception as e:
        print(f"Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open("optimized_vpn_connector.py", "w") as f:
        f.write(optimized_code)

def build_binary():
    """Build binary với các tùy chọn tối ưu cho macOS"""
    # Tạo spec file tùy chỉnh
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['optimized_vpn_connector.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['cv2', 'pyotp'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='vpn_connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    bundle_identifier=None,
)
"""
    
    with open("vpn_connector.spec", "w") as f:
        f.write(spec_content)

    # Clean build directories
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # Build using custom spec file
    os.system("pyinstaller --clean vpn_connector.spec")

if __name__ == "__main__":
    optimize_code()
    build_binary()
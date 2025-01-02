# Requirements

- Python 3.6+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- OpenVPN

## Usage

```bash
uv run main.py --secret "JBSWY3DPEHPK3PXP" --password "mypassword" --sudo_pass "sudo_password" --vpn_config "vpn.ovpn" --usr "myuser"
```

or

```bash
uv run main.py --secret_qr "secret.png" --password "mypassword" --sudo_pass "sudo_password" --vpn_config "vpn.ovpn" --usr "myuser"
```

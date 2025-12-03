import base64
import pyotp


def _hex_seed_to_base32(hex_seed: str) -> str:
    """
    Convert 64-char hex seed to base32 string for TOTP
    """
    seed_bytes = bytes.fromhex(hex_seed)

    base32_bytes = base64.b32encode(seed_bytes)

    return base32_bytes.decode("utf-8")

def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed

    Args:
        hex_seed: 64-character hex string

    Returns:
        6-digit TOTP code as string
    """
    base32_seed = _hex_seed_to_base32(hex_seed)

    totp = pyotp.TOTP(base32_seed)

    code = totp.now() 

    return code


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance

    Args:
        hex_seed: 64-character hex string
        code: 6-digit code to verify
        valid_window: Number of periods before/after to accept (default 1 = ±30s)

    Returns:
        True if code is valid, False otherwise
    """
    base32_seed = _hex_seed_to_base32(hex_seed)

    totp = pyotp.TOTP(base32_seed)

    is_valid = totp.verify(code, valid_window=valid_window)

    return is_valid
if __name__ == "__main__":
    try:
        with open("/data/seed.txt", "r") as f:
            hex_seed = f.read().strip()
    except FileNotFoundError:
        with open("data/seed.txt", "r") as f:
            hex_seed = f.read().strip()

    code = generate_totp_code(hex_seed)
    print("Current TOTP code:", code)

    is_valid = verify_totp_code(hex_seed, code)
    print("Verification result:", is_valid)



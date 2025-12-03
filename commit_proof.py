import subprocess
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization

# -----------------------------
# Helper: Sign commit hash
# -----------------------------
def sign_message(message: str, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    Sign a message using RSA-PSS with SHA-256
    """
    message_bytes = message.encode('utf-8')
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# -----------------------------
# Helper: Encrypt signature
# -----------------------------
def encrypt_with_public_key(data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    """
    Encrypt data using RSA-OAEP with SHA-256
    """
    encrypted = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

# -----------------------------
# Main Proof Generation
# -----------------------------
def generate_commit_proof():
    # 1. Get current commit hash
    commit_hash = subprocess.check_output(
        ['git', 'log', '-1', '--format=%H'],
        text=True
    ).strip()
    
    # 2. Load student private key
    with open("student_private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    # 3. Sign commit hash
    signature_bytes = sign_message(commit_hash, private_key)

    # 4. Load instructor public key
    with open("instructor_public.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # 5. Encrypt signature with instructor public key
    encrypted_signature = encrypt_with_public_key(signature_bytes, public_key)

    # 6. Base64 encode
    b64_signature = base64.b64encode(encrypted_signature).decode('utf-8')

    # Output
    return commit_hash, b64_signature

if __name__ == "__main__":
    commit_hash, proof = generate_commit_proof()
    print("Commit Hash:", commit_hash)
    print("Encrypted Signature (Base64):", proof)

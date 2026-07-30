import hmac
import hashlib
import time
import base64
import json

# SECURITY WARNING: Change this secret key in production!
SECRET_KEY = b"QUOTEX_SAAS_SUPER_SECRET_SIGNING_KEY_2026"

def generate_license_key(days: int, user_email: str) -> str:
    """
    Generates a cryptographically signed license key containing expiration payload.
    """
    expiry_time = int(time.time()) + (days * 86400)
    payload = {
        "email": user_email.strip().lower(),
        "exp": expiry_time,
        "days": days
    }
    
    # Serialize payload
    raw_payload = json.dumps(payload).encode('utf-8')
    b64_payload = base64.urlsafe_b64encode(raw_payload).decode('utf-8')
    
    # Generate HMAC signature
    signature = hmac.new(SECRET_KEY, b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()[:12]
    
    # Form key structure: QTX-PAYLOAD-SIGNATURE
    license_key = f"QTX-{b64_payload}-{signature}"
    return license_key

if __name__ == "__main__":
    print("==================================================")
    print("      QUOTEX SAAS ADMIN LICENSE GENERATOR        ")
    print("==================================================")
    
    email = input("Enter User Email: ").strip()
    print("\nSelect Access Tier:")
    print("1. 3 Days Access Pass ($6)")
    print("2. 7 Days Access Pass ($10)")
    print("3. 30 Days Access Pass ($20)")
    choice = input("Enter choice (1-3): ").strip()
    
    tier_map = {"1": 3, "2": 7, "3": 30}
    if choice in tier_map:
        days = tier_map[choice]
        key = generate_license_key(days, email)
        print("\n--------------------------------------------------")
        print(f"SUCCESS! Key generated for {email} ({days} Days):")
        print(f"\nLICENSE KEY:\n{key}\n")
        print("--------------------------------------------------")
    else:
        print("Invalid choice selected.")
        

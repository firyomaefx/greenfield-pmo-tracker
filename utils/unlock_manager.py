"""
Unlock / Donation Manager for Greenfield Dashboard
Phase 4: Ko-fi donation → unlock code → job links access
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import (
    create_unlock_code, verify_unlock_code, mark_code_used,
    get_unlock_code_by_email
)

KOFI_URL = "https://ko-fi.com/greenfieldtrackerbypedot"


def process_donation(email: str, ko_fi_reference: str = "") -> dict:
    """Process a donation and generate unlock code."""
    code = create_unlock_code(email=email, ko_fi_ref=ko_fi_reference)
    return {
        "success": True,
        "code": code,
        "email": email,
        "ko_fi_url": KOFI_URL,
        "message": f"Thank you for your support! Your unlock code is: {code}"
    }


def check_code(code: str) -> dict:
    """Verify and consume an unlock code."""
    is_valid = verify_unlock_code(code)
    if not is_valid:
        return {"success": False, "message": "Invalid or already used code"}
    
    mark_code_used(code)
    return {"success": True, "message": "Code verified! Job links unlocked."}


def get_donor_history(email: str) -> list:
    """Get unlock code history for a donor email."""
    codes = get_unlock_code_by_email(email)
    return [
        {
            "code": c.get("code"),
            "used": c.get("is_used"),
            "used_at": c.get("used_at"),
            "created_at": c.get("created_at")
        }
        for c in codes
    ]


if __name__ == "__main__":
    # Quick test
    print("Unlock Manager Test")
    print("-" * 40)
    
    result = process_donation("test@greenfield.com", "ko-fi-123")
    print(f"Created code: {result['code']}")
    print(f"Code valid: {verify_unlock_code(result['code'])}")
    
    check_result = check_code(result['code'])
    print(f"Check result: {check_result}")
    
    print(f"Ko-fi URL: {KOFI_URL}")

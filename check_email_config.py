"""Script to check email configuration from .env file."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("Email Configuration Check")
print("=" * 60)

mail_server = os.environ.get('MAIL_SERVER', '').strip()
mail_port = os.environ.get('MAIL_PORT', '').strip()
mail_username = os.environ.get('MAIL_USERNAME', '').strip()
mail_password = os.environ.get('MAIL_PASSWORD', '').strip()
mail_use_tls = os.environ.get('MAIL_USE_TLS', '').strip()

print(f"\nMAIL_SERVER: '{mail_server}' (length: {len(mail_server)})")
print(f"MAIL_PORT: '{mail_port}' (will be converted to: {int(mail_port) if mail_port.isdigit() else 'INVALID'})")
print(f"MAIL_USE_TLS: '{mail_use_tls}'")
print(f"MAIL_USERNAME: '{mail_username}' (length: {len(mail_username)})")
print(f"MAIL_PASSWORD: {'*' * len(mail_password)} (length: {len(mail_password)})")
print(f"MAIL_DEFAULT_SENDER: '{os.environ.get('MAIL_DEFAULT_SENDER', '').strip()}'")

print("\n" + "=" * 60)
print("Issues to check:")
print("=" * 60)

issues = []

if not mail_server:
    issues.append("❌ MAIL_SERVER is not set")
else:
    print("✅ MAIL_SERVER is set")

if not mail_port or not mail_port.isdigit():
    issues.append("❌ MAIL_PORT is not set or invalid")
else:
    print("✅ MAIL_PORT is set")

if not mail_username:
    issues.append("❌ MAIL_USERNAME is not set")
else:
    print("✅ MAIL_USERNAME is set")
    # Check for common issues
    if mail_username.startswith('"') or mail_username.startswith("'"):
        issues.append("⚠️  MAIL_USERNAME appears to have quotes - remove them from .env file")
    if ' ' in mail_username:
        print("⚠️  MAIL_USERNAME contains spaces (should be fine)")

if not mail_password:
    issues.append("❌ MAIL_PASSWORD is not set")
else:
    print("✅ MAIL_PASSWORD is set")
    # Check for common issues
    if mail_password.startswith('"') and mail_password.endswith('"'):
        issues.append("⚠️  MAIL_PASSWORD has double quotes - remove them from .env file")
        print("   Removing quotes...")
        mail_password = mail_password.strip('"')
    if mail_password.startswith("'") and mail_password.endswith("'"):
        issues.append("⚠️  MAIL_PASSWORD has single quotes - remove them from .env file")
        print("   Removing quotes...")
        mail_password = mail_password.strip("'")
    if len(mail_password) != 16:
        print(f"⚠️  MAIL_PASSWORD length is {len(mail_password)} (Gmail app passwords are usually 16 characters)")

if not mail_use_tls.lower() in ['true', '1', 'on']:
    print("⚠️  MAIL_USE_TLS is not set to 'true' (recommended for Gmail)")

print("\n" + "=" * 60)
if issues:
    print("Found issues:")
    for issue in issues:
        print(f"  {issue}")
    print("\n💡 Tips:")
    print("  - Remove quotes around values in .env file")
    print("  - Ensure no extra spaces before/after values")
    print("  - Gmail app passwords should be 16 characters")
    print("  - Example .env format:")
    print("    MAIL_USERNAME=your-email@gmail.com")
    print("    MAIL_PASSWORD=kepjqfrzunwgzgfv")
else:
    print("✅ All configuration looks good!")
    
print("=" * 60)


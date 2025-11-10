"""Direct SMTP connection test to verify credentials."""
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def clean_env_value(value):
    """Clean environment variable value by removing quotes and whitespace."""
    if not value:
        return None
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1].strip()
    return value if value else None

mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com').strip()
mail_port = int(os.environ.get('MAIL_PORT') or 587)
mail_username = clean_env_value(os.environ.get('MAIL_USERNAME'))
mail_password = clean_env_value(os.environ.get('MAIL_PASSWORD'))
test_email = mail_username  # Send to self for testing

print("=" * 60)
print("Direct SMTP Connection Test")
print("=" * 60)
print(f"\nServer: {mail_server}")
print(f"Port: {mail_port}")
print(f"Username: {mail_username}")
print(f"Password length: {len(mail_password) if mail_password else 0}")
print(f"Test email: {test_email}")
print("\n" + "=" * 60)

if not mail_username or not mail_password:
    print("❌ MAIL_USERNAME or MAIL_PASSWORD not set!")
    exit(1)

try:
    print("\nAttempting to connect to SMTP server...")
    server = smtplib.SMTP(mail_server, mail_port)
    server.set_debuglevel(1)  # Show debug output
    
    print("Starting TLS...")
    server.starttls()
    
    print(f"Attempting to login with username: {mail_username}")
    print(f"Password: {'*' * len(mail_password)}")
    
    server.login(mail_username, mail_password)
    print("✅ Successfully authenticated!")
    
    # Try sending a test email
    print(f"\nSending test email to {test_email}...")
    msg = MIMEText("This is a test email from the SMTP connection test.")
    msg['Subject'] = "SMTP Test Email"
    msg['From'] = mail_username
    msg['To'] = test_email
    
    server.send_message(msg)
    print("✅ Test email sent successfully!")
    
    server.quit()
    print("\n" + "=" * 60)
    print("✅ All tests passed! Your SMTP credentials are working.")
    print("=" * 60)
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\nTroubleshooting tips:")
    print("1. Verify the app password is correct (16 characters, no spaces)")
    print("2. Ensure 2-Factor Authentication is enabled on your Google account")
    print("3. Verify the app password was generated for 'Mail' application")
    print("4. Make sure you're using the app password, not your regular Gmail password")
    print("5. Try generating a new app password")
    print("6. Verify MAIL_USERNAME matches the Gmail account that generated the app password")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")


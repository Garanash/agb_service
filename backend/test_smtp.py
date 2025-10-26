#!/usr/bin/env python3
"""Тестовая отправка письма через Mail.ru SMTP"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Настройки
smtp_server = "smtp.mail.ru"
smtp_port = 587
username = "almazgeobur@mail.ru"
password = "vqtpauqXZ5vLjffA7JQs"
to_email = "dolgov_am@mail.ru"

# Создаем сообщение
msg = MIMEMultipart("alternative")
msg["Subject"] = "Test Email from AGB Service"
msg["From"] = f"AGB Service <{username}>"
msg["To"] = to_email

# Добавляем содержимое
text_content = "Test message"
html_content = "<p>Test message</p>"

msg.attach(MIMEText(text_content, "plain", "utf-8"))
msg.attach(MIMEText(html_content, "html", "utf-8"))

# Пробуем отправить
try:
    print(f"Connecting to {smtp_server}:{smtp_port}...")
    context = ssl.create_default_context()
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        print("Starting TLS...")
        server.starttls(context=context)
        
        try:
            print(f"Logging in as {username}...")
            server.login(username, password)
            print("✅ Login successful!")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            exit(1)
        
        try:
            print(f"Sending message to {to_email}...")
            server.send_message(msg)
            print("✅ Message sent successfully!")
        except Exception as e:
            print(f"❌ Send failed: {e}")
            exit(1)
            
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

print("\n🎉 Email sent successfully!")


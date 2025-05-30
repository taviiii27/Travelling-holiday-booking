import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_email(name, destination, kind):
    return f"""
Hi {name},

 We have an amazing {kind.lower()} holiday offer just for you – a trip to {destination} for under $2000!

All packages include transport, accommodation, and exclusive experiences.

Book now and travel with ease – it's time to relax.

 Visit us online too
"""

def send_email(to_email, subject, name, destination, kind, sender_email, sender_password):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email

    body = generate_email(name, destination, kind)
    mime_text = MIMEText(body, "plain")
    message.attach(mime_text)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        print(f" Email sent to {to_email}")
    except Exception as e:
        print(f" Error sending email: {str(e)}")

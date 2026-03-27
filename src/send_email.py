import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from jinja2 import Environment, FileSystemLoader

import os
from dotenv import load_dotenv

load_dotenv()



def send_email(to_email, username, otp, expiry):

    from_email = "gptmedy@gmail.com"
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader('src/templates'))
    template = env.get_template('email_template.html')

    # Render HTML with dynamic data
    html_content = template.render(
        username=username,
        otp=otp,
        expiry=expiry
    )

    # Create email
    msg = MIMEMultipart('related')
    msg['Subject'] = "OTP Verification"
    msg['From'] = from_email
    msg['To'] = to_email

    # Attach HTML
    msg.attach(MIMEText(html_content, 'html'))

    # Attach banner image
    with open("src/banner.png", "rb") as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<banner_image>')
        msg.attach(img)

    # Send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, app_password)
    server.send_message(msg)
    server.quit()



if __name__=="__main__":
    send_email(
        to_email="rajaprabhu484@gmail.com",
        username="Raja",
        otp="123456",
        expiry=5
    )
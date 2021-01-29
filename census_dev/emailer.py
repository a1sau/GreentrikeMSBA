# https://realpython.com/python-send-email/

import configparser as cp
import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import reverse_geocoder2 as rg2




def create_email(email,password):
    port = 465  # For SSL

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)
        message = MIMEMultipart("alternative")
        message["Subject"] = "multipart test"
        message["From"] = email
        message["To"] = email
        text = """\
        Hi,
        How are you?
        This is a test email from the MSBA A1 Sauce as plain text
        """
        html = """\
        <html>
          <body>
            <p>Hi,<br>
               How are you?<br>
               This is a test email from the MSBA A1 Sauce as html<br>
            </p>
          </body>
        </html>
        """
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        server.sendmail(email, email, message.as_string())


if __name__ == '__main__':
    if rg2.check_for_config():
        config = rg2.read_config()
        email_config = config['Email']
        password = email_config.get('password',raw=True)
        create_email(email_config['email'],password)
    else:
        sys.exit("Configure ""config.ini"" before running script again.")
# https://realpython.com/python-send-email/

import configparser as cp
import smtplib
import ssl
import sys
import email as em
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import reverse_geocoder2 as rg2
import imaplib
from email.header import decode_header
import os



def create_email(to_email,email,password,attachment_name=None):
    port = 465  # For SSL
    if attachment_name:
        file = attachment_name
        attachment = open(attachment_name,'rb')
        obj = MIMEBase('application','octet-stream')
        obj.set_payload((attachment).read())
        encoders.encode_base64(obj)
        obj.add_header('Content-Disposition',"attachment; filename= "+file)
        # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        pass
        server.login(email, password)
        message = MIMEMultipart("alternative")
        message["Subject"] = "Building Score File"
        message["From"] = email
        message["To"] = to_email
        text = """\
        Hi,
        Here is a score file for you to review. Save the file and fill in the scores.
        Once you are done, save the file and send it back to: {}
        This is a test email from the MSBA A1 Sauce as plain text
        """.format(email)
        html = """\
        <html>
          <body>
            <p>Hi,<br>
            Here is a score file for you to review. Save the file and fill in the scores.<br>
            Once you are done, save the file and send it back to: {}<br>
            </p>
          </body>
        </html>
        """.format(email)
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        if obj:
            message.attach(obj)
        server.sendmail(email, to_email, message.as_string())


def check_email(email,password):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(email, password)
    status, messages = imap.select("INBOX")
    messages = int(messages[0])
    print(messages)
    for i in range(messages, messages-3, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = em.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                        print("BODY:",body)
                    except:
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            print("BODY:",body)
                        elif "attachment" in content_disposition:
                            pass
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = "attachment"
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))



if __name__ == '__main__':
    if rg2.check_for_config():
        config = rg2.read_config()
        email_config = config['Email']
        password = email_config.get('password',raw=True)
        work_dir = email_config.get('attachment',raw=True)
        if work_dir:
            os.chdir(work_dir)
            print("Working directory:",os.getcwd())
        if (password == "") or (email_config['email'] == ""):
            sys.exit("Update ""config.ini"" with email and password before running script again.")
        create_email("brian.krumholz@gmail.com",email_config['email'],password)


    else:
        sys.exit("Configure ""config.ini"" before running script again.")
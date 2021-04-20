# https://realpython.com/python-send-email/

import smtplib
import ssl
import sys
import email as em
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import reverse_geocoder2 as rg2
from combine_var import getConn
import imaplib
from email.header import decode_header
import os
from datetime import datetime
import re
import pandas as pd
import openpyxl


def create_email(to_email,email,password,attachment_name=None):
    port = 465  # For SSL
    datestr=datetime.now().strftime('%Y/%m/%d')
    if attachment_name:
        file = attachment_name
        attachment = open(attachment_name,'rb')
        obj = MIMEBase('application','octet-stream')
        obj.set_payload(attachment.read())
        encoders.encode_base64(obj)
        obj.add_header('Content-Disposition',"attachment; filename= "+file)
        # Create a secure SSL context
    else:
        return False
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        pass
        server.login(email, password)
        message = MIMEMultipart("alternative")
        message["Subject"] = "Building Score File "+datestr
        message["From"] = email
        message["To"] = to_email
        text = """\
        Hi,
        Here is a score file for you to review. Save the file and fill in the scores.
        Once you are done, save the file with the same name and send it back to: {}
        This is a test email from the MSBA A1 Sauce as plain text
        """.format(email)
        html = """\
        <html>
          <body>
            <p>Hi,<br>
            Here is a score file for you to review. Save the file and fill in the scores.<br>
            Once you are done, save the file with the same name and send it back to: {}<br>
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
    return True


def parse_uid(data):
    pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')   #regular expression for message UID
    match = pattern_uid.match(data)
    return match.group('uid')


def parse_file(filename):
    re_pat = re.compile('(?P<type>^Building|^Census)_(?P<uid>\\d+)_')
    match = re_pat.match(filename)
    if not match:
        return None, None
    type = match.group('type')
    uid = match.group('uid')
    return type, uid


def check_email(email,password,conn):
    new_scores=False  #flag if new excel files are downloaded
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(email, password)
    status, messages = imap.select("INBOX")
    messages = int(messages[0])
    print("Reviewing", messages, "messages")
    for i in range(messages, 0,-1):  #gmail ids start at 1
        print("Msg:",i)
        # fetch the email message by ID
        attachmentLst = []
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = em.message_from_bytes(response[1])
                # decode the email subject
                try:
                    subject, encoding = decode_header(msg["Subject"])[0]
                except Exception as e:
                    print(e)
                    subject = "(No Subject)"
                    encoding = None
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                from_email, encoding = decode_header(msg.get("From"))[0]
                if isinstance(from_email, bytes):
                    from_email = from_email.decode(encoding)
                print("Subject:", subject)
                print("From:", from_email)
                print(msg.is_multipart())
            if msg.is_multipart() and (from_email.lower() != email.lower()):  #Don't download excel that are CCed from main account
                # iterate over email parts
                part_cnt=0
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    print("Part",part_cnt,attachmentLst,content_type,content_disposition)
                    part_cnt+=1
                    if "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename[-5:] == ".xlsx":
                            if filename not in attachmentLst:
                                print("Downloading attachment:",filename)
                                folder_name = "attachment"
                                if not os.path.isdir(folder_name):
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                                attachmentLst.append(filename)
                                new_scores=True
                            else:
                                print("Skip:",filename)
                        else:  #Some other content type that we don't care about
                            pass
        #Once message is reviewed, move out of inbox and put into reviewed
        resp, data = imap.fetch(str(i), "(UID)")
        if data[0] is not None:
            if isinstance(data[0],bytes):
                msg_uid = parse_uid(str(em.message_from_bytes(data[0])).strip())
            else:
                msg_uid = parse_uid(str(data[0]).strip())
                print(data[0])
            if msg_uid:
                result = imap.uid('MOVE', msg_uid, 'Reviewed')
                print("Result of move:",str(i),"UID",msg_uid,result[0])
            else:
                print("UID not found",subject)
    return new_scores


def update_user_scores(conn,inbox_folder,archive_folder):
    if inbox_folder[0]!="/":
        all_files=os.listdir(os.getcwd()+"/"+inbox_folder)
    else:
        all_files=os.listdir(inbox_folder)
    for filename in all_files:
        print("Loading:",filename)
        filepath=os.path.join(os.getcwd(),inbox_folder, filename)
        xl_file = openpyxl.load_workbook(r'C:\output\attachment\Building_2_20210411_101451.xlsx',read_only=True,data_only=True)
        type, uid = parse_file(filename)
        if type and uid:
            if type=="Building":
                try:
                    xl_file = openpyxl.load_workbook(filepath,read_only=True,data_only=True)
                    sheets=xl_file.sheetnames
                    xl_file.close()
                except Exception as e:
                    print("File {} couldn't be opened. Error: {}".format(filepath, e))
                    continue
                for sheetname in sheets:
                    print("Sheet:",sheetname)
                    try:
                        df=pd.read_excel(filepath,sheet_name=sheetname,header=None,index_col=0)
                        print(df.index)
                        if ('CS_ID' in df.index) & ('Building Score' in df.index):
                            etl_building_score(conn,df,uid)
                        if ('Block Group ID' in df.index) & ('Block Group Score' in df.index):
                            etl_census_score(conn,df,uid)
                    except Exception as e:
                        print("Building ETL Fail:",e)
                        continue
            else:  #Census
                for sheetname in sheets:
                    print("Sheet:",sheetname)
                    try:
                        df=pd.read_excel(filepath,sheet_name=sheetname,header=None,index_col=0)
                        if ('Block Group ID' in df.index) & ('Block Group Score' in df.index):
                            etl_census_score(conn,df,uid)
                    except Exception as e:
                        print("Census ETL Fail:",e)
                        continue
                pass
    return True


def etl_building_score(conn,df,uid):
    if conn is None:
        return False
    cur = conn.cursor()
    sql_command = 'truncate "ETL_Building_Score";'  #clear out ETL data
    cur.execute(sql_command)
    conn.commit()

    dft=df.loc[['CS_ID','Building Score']].copy()
    dft=dft.transpose()
    print(dft)
    # print(df.loc[['CS_ID','Building Score']])
    today_date=datetime.date
    for row in dft.itertuples(index=False):
        cs_id=str(row[0])
        score=validate_score(row[1])
        print("read",cs_id,score)
        if cs_id and score and uid:
            sql_command='insert into "ETL_Building_Score" (cs_id,score,uid,date) values (\'{}\',\'{}\',\'{}\',NOW()::date);'.format(cs_id,score,uid)
            print(sql_command)
            cur.execute(sql_command)

        else:
            continue
    conn.commit()
    print("Move ETL Building Score into live table")
    building_score_etl_to_live(conn,cur)
    return True


def etl_census_score(conn,df,uid):
    if conn is None:
        return False
    cur = conn.cursor()
    sql_command = 'truncate "ETL_BG_Score";'  #clear out ETL data
    cur.execute(sql_command)
    conn.commit()
    dft=df.loc[['Block Group ID','Block Group Score']].copy()
    dft=dft.transpose()
    print(dft)
    today_date=datetime.date
    for row in dft.itertuples(index=False):
        bg_geo_id=str(row[0])
        score=validate_score(row[1])
        print("read",bg_geo_id,score)
        if bg_geo_id and score and uid:
            sql_command='insert into "ETL_BG_Score" (bg_geo_id,score,uid,date) values (\'{}\',\'{}\',\'{}\',NOW()::date);'.format(bg_geo_id,score,uid)
            print(sql_command)
            cur.execute(sql_command)

        else:
            continue
    conn.commit()
    print("Move ETL Census Score into live table")
    bg_score_etl_to_live(conn,cur)
    return True


def validate_score(score):
    try:
        score=int(score)
    except Exception as e:
        print("Score {} is not a valid integer".format(score))
        return None
    if 0 < score < 6:
        return score
    else:
        return None


def building_score_etl_to_live(conn,cur):
    if conn is None:
        return None
    sql_command = """
    insert into "Building_Score" (cs_id, uid, "Score", date_obtained) select cs_id,uid,score,date from "ETL_Building_Score"
    on conflict on constraint building_score_pk do update
    set "Score" = excluded."Score",
    date_obtained = excluded.date_obtained;
    """
    cur.execute(sql_command)
    conn.commit()
    return True


def bg_score_etl_to_live(conn,cur):
    if conn is None:
        return None
    sql_command = """
    insert into "BG_Score" (bg_geo_id, uid, score, date_obtained) select bg_geo_id,uid,score,date from "ETL_BG_Score"
    on conflict on constraint bg_score_pk do update
    set score = excluded.score,
    date_obtained = excluded.date_obtained;
    """
    cur.execute(sql_command)
    conn.commit()
    return True


def main():
    conn=getConn()
    if conn is None:
        sys.exit("Failed to get SQL connection")
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
        new_scores = check_email(email_config['email'],password,conn)
        if new_scores:
            update_user_scores(conn,'attachment','archive')
    else:
        sys.exit("Configure ""config.ini"" before running script again.")
    conn.close()
    return True


if __name__ == '__main__':
    main()
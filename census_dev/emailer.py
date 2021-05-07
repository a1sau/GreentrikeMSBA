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
import shutil
from datetime import datetime
import re
import pandas as pd
import openpyxl
import calc_models as cm



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
                <p>Greentrike Property Finder
                    <br/>
                    <br/>
         <b>Purpose</b> 
                    <br/>
                    <br/>
        This automated email focuses on providing GreenTrike with location options that our model has rated and selected based on your feedback.
                    <br/>
                    <br/>
        In this email, you will find an attached excel workbook. The workbook will have two sheets: "Sale" and "Lease."
                    <br/>
                    <br/>
        In these excel sheets, there are a few things that you will be doing. 
                    <br/>
                    <br/>
         <b>Getting Started</b>
                    <br/>
                    <br/>
        Once you receive the email, mouse-over the attachment in Gmail. You will see an icon that looks like a pencil.
                    <br/>
        Click this icon to open the spreadsheet in Google Sheets.
                    <br/>
        Once Google Sheets is open, you will be able to edit the file. The only rows you should edit will be highlighted in blue.
                    <br/>
        Those rows are labeled: "Building Score" and "Block Group Score". You may not see Building related information if
        you are configured to only receive Census Block Group Scores.
                    <br/>
        Looking at properties
                    <br/>
                    <br/>
         1. You can click on the links along with the associated location to go to Loopnet listing of the property for additional information.
                    <br/>
        2. Examine the property that is affiliated with the link. Does it match your criteria? How well does this property fit for your team in terms of a future location?
                    <br/>
        3. Rank how well it matches that criteria from 1-5 with 1 being a property you would never consider and 5 meaning you are very interested.
                    <br/>
        4. Along with the building score, the demographics of the area are included.
        Once you have filled out the scoring row for the building, provide your score for the census area that the building is located. 
                    <br/>
        5. Once you have completed the "Sale" tab, go to the "Lease" tab and repeat the process. You are free to rate some or all of the listings.
                    <br/>
                    <br/>
        In a coming update, there will be additional tabs that will show the model's predicted score for the properties you are rating.
                    <br/>
                    <br/>
        Once you have finished scoring buildings and areas, you are ready to send the file back.
                    <br/>
        Go to the top left of your page and click on the File tab.
                    <br/>
        Scroll down to the email option (right above download)
                    <br/>
        Select "Reply with this file" and then select send.
                    <br/>
                    <br/>
        5. Once you send both spreadsheets back, our program will analyze your scores and utilize them to better train the model and provide you with properties that better match your criteria.
                    <br/>
                </p>
        <br/>
        <br/>
        If you want a new score spreadsheet send tomorrow rather than wait until the next scheduled file, click this 
        <a href="mailto:msba.greentrike@gmail.com?subject=Send new scores"> link: </a> and send the email.
        <br/>
        
        <br/><br/>
        If you want to stop receiving emails, click this <a href="mailto:msba.greentrike@gmail.com?subject=Unsubscribe"> link: </a> and send the email.
        <br/>
        
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
                ##TODO Add special handling for unsubscribe and send immediately emails
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
    if not inbox_folder:
        print("No inbox folder specified.")
        return None
    if not archive_folder:
        print("No archive folder specified")
        return None
    if inbox_folder[0] != "/":
        all_files=os.listdir(os.getcwd()+"/"+inbox_folder)
    else:
        all_files=os.listdir(inbox_folder)
    if archive_folder[0] != "/":
        archive_folder=os.path.join(os.getcwd(),archive_folder)
    if not(os.path.isdir(archive_folder)):
        print("Archive folder doesn't exist:",archive_folder)
    for filename in all_files:
        print("Loading:",filename)
        filepath=os.path.join(os.getcwd(),inbox_folder, filename)
        archivepath = os.path.join(archive_folder, filename)
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
        print("Archiving file:",filename)
        shutil.move(filepath,archivepath)
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
            sql_command="""insert into "ETL_Building_Score" (cs_id,score,uid,date) values (\'{}\',\'{}\',\'{}\',NOW()::date)
            on conflict on constraint etl_building_score_pk do update
            set score = excluded.score;
            ;""".format(cs_id,score,uid)
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
            sql_command="""insert into "ETL_BG_Score" (bg_geo_id,score,uid,date) values (\'{}\',\'{}\',\'{}\',NOW()::date)
                        on conflict on constraint etl_bg_score_pk do update
                        set score = excluded.score;""".format(bg_geo_id,score,uid)
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
            old_work_dir=os.getcwd()
            os.chdir(work_dir)
            print("Working directory:",os.getcwd())
        if (password == "") or (email_config['email'] == ""):
            sys.exit("Update ""config.ini"" with email and password before running script again.")
        new_scores = check_email(email_config['email'],password,conn)
        new_scores=True
        if new_scores:
            update_user_scores(conn,'attachment','archive')
            os.chdir(old_work_dir) #restore old working directory in case config needs to be reloaded
            cm.main(conn)   #recalculate model scores
        else:
            os.chdir(old_work_dir) #restore old working directory in case config needs to be reloaded
    else:
        sys.exit("Configure ""config.ini"" before running script again.")
    conn.close()
    return True


if __name__ == '__main__':
    main()

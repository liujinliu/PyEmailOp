#coding=utf-8
import csv
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from oslo_config import cfg
import sys
CONF = cfg.CONF

cli_opts = [
    cfg.StrOpt('smtp_server', 
               help='address of smtp server'),
    cfg.StrOpt('userpass', 
               help='user password'),
    cfg.StrOpt('fr', 
               help='address of email sender from'),
    cfg.StrOpt('to', 
               help='address of email send to'),
    cfg.StrOpt('filename', 
               help='attachment file name'),
    cfg.StrOpt('subject',
               default=('unkown'),
               help='email subject'),
]

CONF.register_cli_opts(cli_opts)

def setup():
    CONF(sys.argv[1:])

def mail_report(mailfrom,to,mail_name, filenames):
    outer = MIMEMultipart()
    outer['Subject'] = mail_name + " ---automatic send"
    outer['From'] = mailfrom 
    outer['To'] = to

    # Internal text container
    inner = MIMEMultipart('alternative')
    text = "Here is the automatic mail report for " + mail_name
    html = """\
    <html>
        <head></head>
        <body>
         <p>Here is the mail report for
            <b> """ + mail_name + """</b>
         </p>
        </body>
    </html>
    """
    part1 = MIMEText(text,'plain')
    part2 = MIMEText(html, 'html')
    inner.attach(part1)
    inner.attach(part2)
    outer.attach(inner)
    filename_list = filenames.split(',')
    for filename in filename_list:
        csv_part = MIMEText(open(filename,'rb').read())
        csv_part.add_header('Content-Disposition','attachment',filename=filename)
        outer.attach(csv_part)

    return outer

def send_message(message, smtp_addr, userlogin, userpass):
    s = smtplib.SMTP(smtp_addr)
    s.login(userlogin,userpass)
    s.sendmail(message['From'],message['To'].split(','),message.as_string())
    s.close()


def main():
    setup()
    if not (CONF.fr and CONF.to and CONF.filename and CONF.smtp_server and CONF.userpass and CONF.filename):
        print "useage:"
        print "python mail_send.py --fr=youremail --to=outeremail --subject=example --filename=somefile --smtp_server=xxx --userpass=yourpass" 
        return
    email=mail_report(CONF.fr, CONF.to, CONF.subject, CONF.filename)
    send_message(email, CONF.smtp_server, CONF.fr, CONF.userpass)


if __name__ == '__main__':
    main()


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random

password = ""
with open("key.txt","r") as f:
    password=f.readlines()[3]
    password=password.replace(" ","")
    print(password)

subject = '2FA'
body = 'Your Code: '
sender = 'oridostore1@gmail.com'
recipient = [sender]

def send_mail(subject, body, sender, recipient, password):
    """
    sends the mail 'manually', not in use
    :param subject:
    :param body:
    :param sender:
    :param recipient:
    :param password:
    :return:
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipient)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipient, msg.as_string())
    print('Mail sent successfully')

def send_2FA(recipient):
    """
    sends the 2FA email
    :param recipient: the Gmail to send auth code
    :return: 1.if was sent(true or false) , 2. the auth code that was generated and sent
    """
    code = str(random.randint(100000, 999999))
    body = 'Your Code: ' + code
    print(body)
    recipients = [sender]
    recipients.append(recipient)

    msg = MIMEText(body)     #msg form
    msg['Subject'] = '2FA'
    msg['From'] = 'oridostore1@gmail.com'
    msg['To'] = ', '.join(recipients)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:   #sends as smtp protocol, with ssl encryption
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipient, msg.as_string())
        print('Mail sent successfully')
        return True, code
    except Exception as e:
        print(e)
        return False, ""

print(send_2FA("2idobaruch@gmail.com"))


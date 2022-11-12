from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import sqlite3
# get the platform

fromEmail = 'sekyuisme27@gmail.com'
fromEmailPassword = 'gwlstadxritinfiq'


toEmail = 'raizensangalang.tech@gmail.com'

def getEmailSave():
    return "dsds"

def getTheEmail(USERID):
    con = sqlite3.connect('db_web.db')
    cursor = con.cursor()
    print("Opened database successfully")
    select_query = "SELECT * FROM users WHERE uid = ?"
    cursor.execute(select_query, (USERID,))
    records = cursor.fetchone()
    print(records)
    return (records)
    cursor.close()

def sendEmail(image, USERID):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Person Detected'
    msgRoot['From'] = fromEmail
    # msgRoot['To'] = getTheEmail()[2]
    # print(getTheEmail()[2])
    # #xtx = mail.getTheEmail()[1]
    # #print(xtx)
    # print("SDKSKDKSKDKSKD")
    # print(getTheEmail(username))
    emailSend  =getTheEmail(USERID)[3]
    print(emailSend)
    msgRoot['To'] = emailSend
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    # get the day and time in format of Saturday - November 12, 2022 - 12:00:00 AM
    day = datetime.now().strftime("%A - %B %d, %Y - %I:%M:%S %p")
    msgText = MIMEText(f'motion detected - Date: {day}')
    msgAlternative.attach(msgText)

    msgText = MIMEText('<img src="cid:image1">', 'html')
    msgAlternative.attach(msgText)

    msgImage = MIMEImage(image)
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(fromEmail, fromEmailPassword)
    smtp.sendmail(fromEmail, emailSend, msgRoot.as_string())
    smtp.quit()

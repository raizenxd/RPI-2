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

def getTheEmail(username):
    con = sqlite3.connect('db_web.db')
    cursor = con.cursor()
    print("Opened database successfully")
    select_query = "SELECT * FROM users WHERE uid = ?"
    cursor.execute(select_query, (username,))
    records = cursor.fetchone()
    print("Total rows are:  ", len(records))
    print(records)    
    return (records)
    

def sendEmail(image, username):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Person Detected'
    msgRoot['From'] = fromEmail
    # msgRoot['To'] = getTheEmail()[2]
    # print(getTheEmail()[2])
    # #xtx = mail.getTheEmail()[1]
    # #print(xtx)
    # print("SDKSKDKSKDKSKD")
    print(getTheEmail(username))
    emailSend  = toEmail #getTheEmail(username)[3] # toEmail
    print(emailSend)
    msgRoot['To'] = emailSend
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    msgText = MIMEText('motion detected')
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

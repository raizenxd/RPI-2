import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import sqlite3

fromEmail = 'sekyuisme27@gmail.com'

fromEmailPassword = 'gwlstadxritinfiq'


toEmail = 'raizensangalang.tech@gmail.com'

def getEmailSave():
    return "dsds"

def getTheEmail():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    print("Opened database successfully")
    select_query = "SELECT * FROM usercon WHERE id=1"
    cursor.execute(select_query)
    records = cursor.fetchone()
    print(records)
    return (records)
    cursor.close()

def sendEmail(image):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Person Detected'
    msgRoot['From'] = fromEmail
    # msgRoot['To'] = getTheEmail()[2]
    # print(getTheEmail()[2])
    # #xtx = mail.getTheEmail()[1]
    # #print(xtx)
    # print("SDKSKDKSKDKSKD")
    msgRoot['To'] = toEmail
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
    smtp.sendmail(fromEmail, toEmail, msgRoot.as_string())
    smtp.quit()

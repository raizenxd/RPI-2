from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import sqlite3
# This is the email address that will send the email
# You will need to allow less secure apps to access this email 
# https://myaccount.google.com/lesssecureapps 
# https://accounts.google.com/b/0/DisplayUnlockCaptcha  
# You can also watch this video https://youtu.be/yuT6PhH-5iw
fromEmail = 'sekyuisme27@gmail.com'
fromEmailPassword = 'gwlstadxritinfiq'
toEmail = 'raizensangalang.tech@gmail.com'

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
# This is the SMTP mail server
# You can use any SMTP mail server you want
# For example, if you are using gmail, you can use smtp.gmail.com
# smtpServer = 'smtp.gmail.com'
# smtpPort = 587
def sendEmail(image, USERID):
    # Create the root message and fill in the from, to, and subject headers 
    # MIME meaninbg Multipurpose Internet Mail Extensions
    # https://en.wikipedia.org/wiki/MIME
    # https://docs.python.org/3/library/email.mime.html       
    msgRoot = MIMEMultipart('related')
    # Subject of the email
    msgRoot['Subject'] = 'Person Detected'
    # From email address
    msgRoot['From'] = fromEmail    
    # To email address
    # getTheEmail is a function that will get the email address of the database
    # The reason why it needs [3] is because the email address is the 4th column in the database    
    emailSend  =getTheEmail(USERID)[3]
    # Print to the console the email address that will receive the email
    print(emailSend)
    # Recipient email address
    msgRoot['To'] = emailSend
    # Create the body of the message (a plain-text and an HTML version).
    msgAlternative = MIMEMultipart('alternative')
    # Attach the body to the root message
    msgRoot.attach(msgAlternative)
    # get the day and time in format of Saturday - November 12, 2022 - 12:00:00 AM
    day = datetime.now().strftime("%A - %B %d, %Y - %I:%M:%S %p")
    # Create the body of the message (a plain-text and an HTML version).
    msgText = MIMEText(f'motion detected - Date: {day}')
    # Attach the body to the root message
    msgAlternative.attach(msgText)
    # This is the message in HTML format
    msgText = MIMEText('<img src="cid:image1">', 'html')
    # Attach the body to the root message also it is alternative format
    msgAlternative.attach(msgText)
    # This example assumes the image is in the current directory
    msgImage = MIMEImage(image)
    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    # attach the image to the root message
    msgRoot.attach(msgImage)
    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    # identify ourselves to smtp gmail client
    # start TLS for security
    # TLS (Transport Layer Security) is a cryptographic protocol that provides communication security over the Internet.
    smtp.starttls()
    # Authentication or log in on the server
    smtp.login(fromEmail, fromEmailPassword)
    # Send the email
    smtp.sendmail(fromEmail, emailSend, msgRoot.as_string())
    smtp.quit()

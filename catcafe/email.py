import sendgrid
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from .settings import SITE_NAME, ADMIN_SMTP
import os

TEMPLATES = {
    'CONFIRM_ACCOUNT_EMAIL' : 'd-ec72ceb7fa3740b1867b64d5fb5639e1',
    'RESET_PASSWORD_EMAIL' : 'd-73260915064549a1994de2844ce3d271'
}

def sendjoiningconfirmation(url,emailad,name,template):
    f = settings.ADMIN_SMTP
    t = emailad
    mail = Mail(from_email=f, to_emails=t)
    mail.template_id = TEMPLATES[template]
    mail.dynamic_template_data = {
        'confirm_link': url,
        'name' : name
    }
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def sendpasswordresetemail(url,emailad,name,template):
    f = settings.ADMIN_SMTP
    t = emailad
    mail = Mail(from_email=f,to_emails=t)
    mail.template_id = TEMPLATES[template]
    mail.dynamic_template_data = {
        'reset_link': url,
        'name':name
    }
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def sendcontactmessage(message,subject):
    f = ADMIN_SMTP
    t = 'cbri4nt@gmail.com'
    s = subject
    c = "<html><head><title>Reset Password</title></head><body><p> "+ \
                                    message + "</p></body></html>"
    mail = Mail(from_email=f, subject=s, to_emails=t, html_content=c)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

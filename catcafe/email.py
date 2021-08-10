import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from .settings import SITE_NAME, ADMIN_SMTP
import os

def sendjoiningconfirmation(url,username,emailad):
    f = ADMIN_SMTP
    t = emailad
    s = "Please Confirm Membership for " + SITE_NAME
    c = "<html><head><title>" + SITE_NAME + " - Confirm Membership</title></head><body><h1>Hello "+ username + "</h1>" \
                                    + "<p>Please confirm membership of forum.org by clicking on the link below.</p>" \
                                    + "<h2><a href='" + url + "' target='_blank'>" + url + "</a></h2>" \
                                    + "</body></html>"
    mail = Mail(from_email=f, subject=s, to_emails=t, html_content=c)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def sendpasswordresetemail(url,username,emailad):
    f = ADMIN_SMTP
    t = emailad
    s = "Reset your password for " + SITE_NAME
    c = "<html><head><title>Reset Password</title></head><body><h1>Hello "+ username + \
                                    " click on the link below or copy and paste into the browser address bar to reset your password</h1>" \
                                    + "<h2><a href='" + url + "'>" + url + "</a></h2>" \
                                    + "</body></html>"
    mail = Mail(from_email=f, subject=s, to_emails=t, html_content=c)
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

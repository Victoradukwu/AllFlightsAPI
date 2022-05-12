from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def send_email(payload):
    subject = payload['subject']
    html_content = payload['html_content']
    to_email = payload['to_email'],
    email = EmailMessage(subject, html_content, to=to_email)
    email.content_subtype = "html"
    email.send()

from celery import shared_task
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.response import Response


@shared_task
def send_email(payload):
    subject = payload['subject']
    html_content = payload['html_content']
    to_email = payload['to_email'],
    email = EmailMessage(subject, html_content, to=to_email)
    email.content_subtype = "html"
    email.send()


def custom_exception_handler(exc, context):

    msg = exc.detail if hasattr(exc, 'detail') else str(exc)
    return Response({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)

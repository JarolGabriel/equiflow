import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        if settings.RESEND_API_KEY:
            resend.api_key = settings.RESEND_API_KEY

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        count = 0
        for message in email_messages:
            try:
                params = {
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": message.to,
                    "subject": message.subject,
                    "html": message.body,
                }
                resend.Emails.send(params)
                count += 1
            except Exception:
                if not self.fail_silently:
                    raise
        return count

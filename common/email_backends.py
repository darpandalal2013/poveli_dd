from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend


class TestingEmailBackend(EmailBackend):
    """
    Used in non-dev, non-prod environments.
    """
    def send_messages(self, email_messages):
        """
        Overrides the to email address for all the messages that are being
        sent out.
        """
        for email_message in email_messages:
            new_to_list = []    # new sanitized list of email addresses
            for email in email_message.to:
                if email.endswith('povelli.com'):
                    new_to_list.append(email)

            if new_to_list: # if at least one email then good to go
                email_message.to = new_to_list
            else:
                email_message.to = ['dev@povelli.com',]

            # pre-pend ENV to subject of email
            email_message.subject = '[%s] %s' % \
                (settings.ENV, email_message.subject)

        super(TestingEmailBackend, self).send_messages(email_messages)

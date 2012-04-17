from .message import EmailMessage, EmailMultiAlternatives
from .smtp import SMTPClient

def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, headers=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    msg = EmailMessage(subject, message, from_email, recipient_list,
                        connection=connection,
                        headers=headers)

    if not connection:
        connection = SMTPClient()
    connection.send_message(msg)

def send_template(subject="", html=None, text=None, rcpt=[], sender=None, context_instance=None, fail_silently=True, connection=None):
    from thistle import render_to_string, Context

    if not context_instance:
        context_instance = Context()

    if text:
        body_text = render_to_string(text, context_instance)
    else:
        body_text = ""
    msg = EmailMultiAlternatives(subject, body_text, sender, rcpt)

    if html:
        body_html = render_to_string(html, context_instance)
        msg.attach_alternative(body_html, 'text/html')

    if not connection:
        connection = SMTPClient()
    connection.send_message(msg)

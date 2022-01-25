import os

import html2text

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from accounts.utils import cents_to_dollars, get_current_payout_per_referral


def send_email(
    recipients,
    message,
    subject,
    from_email="no-reply@m.guppy.co",
    reply_to_email=None,
    from_name="Guppy",
    bcc=None,
):
    """
    The sender method
    """
    try:
        if from_email is None:
            from_email = "no-reply@m.guppy.co"
        scoped = ""
        if settings.DEBUG:
            scoped = "scoped"
        header = (
            """
            <style %s type='text/css'>
                .emailImage{
                    height:auto !important;
                    max-width:200px !important;
                    width: 100%% !important;
                }
            </style>
            """
            % scoped
        )

        message = header + message

        to_email = recipients
        if os.environ.get("DJANGO_SETTINGS_MODULE") != "settings.production":
            to_email += ".sink.sparkpostmail.com"
        html_content = message
        text_content = html2text.html2text(message)
        if bcc is None:
            bcc = ["ian@guppy.co"]
        elif isinstance(bcc, list):
            bcc.append("ian@guppy.co")
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email="%s <%s>" % (from_name, from_email),
            to=to_email,
            bcc=bcc,
        )
        if reply_to_email is not None:
            msg.reply_to = reply_to_email
        msg.attach_alternative(html_content, "text/html")

        fail_silently = not settings.DEBUG
        result = msg.send(fail_silently=fail_silently)
        return result, html_content
    except Exception as err:  # pylint: disable=broad-except
        print(("An email error occurred: %s - %s" % (err.__class__, err)))
        return False, html_content


def send_welcome_signup_email(recipients):
    subject = "Welcome to Guppy!"
    message = """
        <p>Welcome to the Guppy community!</p>
        <p>We have one goal - to pay you as much as we can
        when you're surfing the web.
        If you have any questions, please reach out at ian@guppy.co
        and I'll be happy to help.</p>
        <br><br>
        Sincerely,
        <br><br>
        Ian Campbell
        <br>
        Founder & CTO, <a href="https://guppy.co">https://guppy.co</a>
        """
    from_email = "ian@m.guppy.co"
    reply_to_email = "ian@guppy.co"
    from_name = "Ian Campbell"
    result, message = send_email(
        recipients, message, subject, from_email, reply_to_email, from_name
    )

    return result, message


def send_referral_program_email(recipients):
    payout_amount = cents_to_dollars(get_current_payout_per_referral())
    subject = "Earn more with Guppy's referral program"
    message = f"""
        <p>Tell your friends about Guppy,
        and you'll earn even more cash with our referral program.</p>
        <p>Current payout per referral is {payout_amount}</p>
        <br>
        <a href="/"><button style="
            padding: 10px;
            border: none;
            border-radius: 3px;
            background-color: #0084FF;
            font-size: 15px;
            color: #fff;
            cursor: pointer;
        ">🎣 REFER FRIENDS AND EARN 💰 💰 💰</button></a>
        <br><br>
        Sincerely,
        <br><br>
        The Guppy Team
        """
    from_email = "ian@m.guppy.co"
    reply_to_email = "ian@guppy.co"
    from_name = "The Guppy Team"
    result, message = send_email(
        recipients, message, subject, from_email, reply_to_email, from_name
    )

    return result, message


def send_follow_up_email(recipients):
    subject = "Your Guppy account is inactive"
    message = """
        <p>I noticed your Guppy account is inactive -
        you'll no longer earn cash on the web with Guppy.</p>
        <br>
        <p>
        Is there anything we could have done to improve your Guppy experience?
        I'd love to hear from you - just reply to this email
        or reach me at <a href="mailto:ian@guppy.co">ian@guppy.co</a>.
        </p>
        <br><br>
        Sincerely,
        <br><br>
        Ian Campbell
        <br>
        Founder & CTO, <a href="https://guppy.co">https://guppy.co</a>
        """
    from_email = "ian@m.guppy.co"
    reply_to_email = "ian@guppy.co"
    from_name = "Ian Campbell"
    result, message = send_email(
        recipients, message, subject, from_email, reply_to_email, from_name
    )

    return result, message

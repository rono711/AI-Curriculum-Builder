"""SMTP transport for validated learning feedback."""

import os
import smtplib
import ssl

from email.message import EmailMessage


class FeedbackMailSender:

    def __init__(self):
        self.host = os.getenv(
            "SMTP_HOST",
            ""
        ).strip()

        self.port = int(
            os.getenv(
                "SMTP_PORT",
                "0"
            )
            or 0
        )

        self.username = os.getenv(
            "SMTP_USERNAME",
            ""
        ).strip()

        self.password = os.getenv(
            "SMTP_PASSWORD",
            ""
        )

        self.from_email = os.getenv(
            "SMTP_FROM_EMAIL",
            ""
        ).strip()

        self.from_name = os.getenv(
            "SMTP_FROM_NAME",
            "Learning Feedback"
        ).strip()

        self.security = os.getenv(
            "SMTP_SECURITY",
            "ssl"
        ).strip().lower()

        self.test_email = os.getenv(
            "FEEDBACK_TEST_EMAIL",
            ""
        ).strip()

        self.live_enabled = (
            os.getenv(
                "FEEDBACK_LIVE_ENABLED",
                "false"
            )
            .strip()
            .lower()
            == "true"
        )

        self._validate_config()

    def _validate_config(self):
        required = {
            "SMTP_HOST":
                self.host,

            "SMTP_PORT":
                self.port,

            "SMTP_USERNAME":
                self.username,

            "SMTP_PASSWORD":
                self.password,

            "SMTP_FROM_EMAIL":
                self.from_email,

            "FEEDBACK_TEST_EMAIL":
                self.test_email,
        }

        missing = [
            key
            for key, value in required.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing email configuration: "
                + ", ".join(missing)
            )

        if self.security not in {
            "ssl",
            "starttls",
        }:
            raise RuntimeError(
                "SMTP_SECURITY must be "
                "'ssl' or 'starttls'."
            )

    def send_test(
            self,
            *,
            subject,
            html
    ):
        """Send only to the configured TEST recipient."""

        return self._send(
            recipient=self.test_email,
            subject=subject,
            html=html
        )

    def send_live(
            self,
            *,
            recipient,
            subject,
            html
    ):
        """LIVE delivery is configuration-gated."""

        if not self.live_enabled:
            raise RuntimeError(
                "LIVE feedback delivery is disabled."
            )

        return self._send(
            recipient=recipient,
            subject=subject,
            html=html
        )

    def _send(
            self,
            *,
            recipient,
            subject,
            html
    ):
        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = (
            f"{self.from_name} "
            f"<{self.from_email}>"
        )
        message["To"] = recipient

        message.set_content(
            "Your learning feedback is available "
            "in the HTML version of this email."
        )

        message.add_alternative(
            html,
            subtype="html"
        )

        context = (
            ssl.create_default_context()
        )

        if self.security == "ssl":
            with smtplib.SMTP_SSL(
                self.host,
                self.port,
                context=context,
                timeout=30
            ) as smtp:
                smtp.login(
                    self.username,
                    self.password
                )

                smtp.send_message(
                    message
                )

        else:
            with smtplib.SMTP(
                self.host,
                self.port,
                timeout=30
            ) as smtp:
                smtp.ehlo()

                smtp.starttls(
                    context=context
                )

                smtp.ehlo()

                smtp.login(
                    self.username,
                    self.password
                )

                smtp.send_message(
                    message
                )

        return {
            "recipient":
                recipient,

            "subject":
                subject,
        }

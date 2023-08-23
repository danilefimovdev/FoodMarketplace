from mailings.tasks import send_notification_task


def notify_vendor_of_status_change(approve_state: bool, first_name: str, status_changed: bool, email: str):

    if status_changed:
        email_template = 'accounts/email/admin_approval_email.html'
        context = {
            'first_name': first_name,
            'to_email': [email],
            'is_approved': approve_state
        }

        if approve_state is True:
            message_subject = 'Congratulations! Your restaurant has been approved.'
        else:
            message_subject = 'We are sorry! Your restaurant has been disapproved.'

        send_notification_task.delay(message_subject, email_template, context)

import smtplib

from config.settings import Settings
from utils.helpers import utcnow

class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = Settings.SMTP_HOST
        self.email_port = Settings.SMTP_PORT
        self.email_user = Settings.SMTP_USER
        self.email_password = Settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        import logging
        logger = logging.getLogger(__name__)
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info("Email enviado para %s", to)
            return True
        except Exception as e:
            logger.error("Erro ao enviar email: %s", str(e))
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utcnow()
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        result = []
        for n in self.notifications:
            if n['user_id'] == user_id:
                result.append(n)
        return result

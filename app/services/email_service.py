import smtplib
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from ..models import OTPCode
from ..models.database import db

class EmailService:
    """Service for handling email operations including OTP."""
    
    def __init__(self):
        self.smtp_server = current_app.config['SMTP_SERVER']
        self.smtp_port = current_app.config['SMTP_PORT']
        self.smtp_username = current_app.config['SMTP_USERNAME']
        self.smtp_password = current_app.config['SMTP_PASSWORD']
        self.smtp_use_tls = current_app.config.get('SMTP_USE_TLS', True)
    
    def generate_otp(self) -> str:
        """Generate a 6-digit OTP."""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def send_otp_email(self, email: str, otp_code: str) -> bool:
        """Send OTP code via email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = email
            msg['Subject'] = 'Email Auditor - OTP Code'
            
            body = f"""
            Your OTP code is: {otp_code}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.smtp_use_tls:
                server.starttls()
            
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, email, text)
            server.quit()
            
            current_app.logger.info(f"OTP email sent to {email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending email to {email}: {e}")
            return False
    
    def send_otp_sms(self, mobile: str, otp_code: str) -> bool:
        """Send OTP code via SMS (placeholder - implement with your SMS provider)."""
        # This is a placeholder - you'll need to integrate with an SMS service
        # like Twilio, AWS SNS, etc.
        current_app.logger.info(f"SMS OTP for {mobile}: {otp_code}")
        return True
    
    def send_otp(self, user) -> bool:
        """Send OTP to user via email or SMS."""
        otp_code = self.generate_otp()
        
        # Create OTP record
        otp = OTPCode(
            user_id=user.id,
            code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp)
        db.session.commit()
        
        # Send OTP
        success = False
        if user.email:
            success = self.send_otp_email(user.email, otp_code)
        if user.mobile and not success:
            success = self.send_otp_sms(user.mobile, otp_code)
        
        return success 
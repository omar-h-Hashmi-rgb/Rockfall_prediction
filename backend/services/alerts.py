from __future__ import annotations
import requests
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Dict, List, Optional
import logging
from datetime import datetime
import json
from ..config import settings

logger = logging.getLogger(__name__)

class AlertServiceError(Exception):
    """Custom exception for alert service errors."""
    pass

class EmailService:
    """Email alert service using SendGrid."""
    
    def __init__(self):
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.alert_email_from
        self.to_email = settings.alert_email_to
        self.client = None
        
        if self.api_key:
            try:
                self.client = sendgrid.SendGridAPIClient(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid client: {e}")
    
    def send_email(
        self, 
        subject: str, 
        content: str, 
        to_email: Optional[str] = None,
        content_type: str = "text/plain"
    ) -> bool:
        """Send email alert."""
        
        if not self.client:
            logger.error("SendGrid client not initialized")
            return False
        
        try:
            recipient = to_email or self.to_email
            
            # Create email message
            mail = Mail(
                from_email=Email(self.from_email),
                to_emails=To(recipient),
                subject=subject,
                plain_text_content=Content("text/plain", content) if content_type == "text/plain" else None,
                html_content=Content("text/html", content) if content_type == "text/html" else None
            )
            
            # Send email
            response = self.client.send(mail)
            
            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Email send failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
    
    def send_risk_alert(
        self, 
        risk_level: str, 
        probability: float, 
        location: Optional[str] = None,
        additional_info: Optional[Dict] = None
    ) -> bool:
        """Send formatted risk alert email."""
        
        # Create email content
        subject = f"🚨 {risk_level} RISK ALERT - Rockfall Prediction System"
        
        # Build email body
        content_lines = [
            f"ROCKFALL RISK ALERT",
            f"=" * 50,
            f"Risk Level: {risk_level}",
            f"Probability: {probability:.2%}",
            f"Timestamp: {datetime.utcnow().isoformat()}Z",
        ]
        
        if location:
            content_lines.append(f"Location: {location}")
        
        if additional_info:
            content_lines.append("\nAdditional Information:")
            for key, value in additional_info.items():
                content_lines.append(f"  {key}: {value}")
        
        content_lines.extend([
            "\nRecommended Actions:",
            "- Evacuate personnel from affected area",
            "- Secure equipment and materials", 
            "- Monitor sensor readings closely",
            "- Contact safety team immediately",
            "",
            "This is an automated alert from the AI-based Rockfall Prediction System.",
            "Please respond according to your emergency protocols."
        ])
        
        content = "\n".join(content_lines)
        
        return self.send_email(subject, content)
    
    def test_connection(self) -> Dict:
        """Test email service connection."""
        if not self.client:
            return {
                'status': 'error',
                'message': 'SendGrid client not configured'
            }
        
        try:
            # Send a test email to verify service
            test_result = self.send_email(
                "Test Email - Rockfall System",
                "This is a test email from the Rockfall Prediction System."
            )
            
            return {
                'status': 'success' if test_result else 'error',
                'message': 'Test email sent' if test_result else 'Test email failed',
                'configured': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'configured': True
            }

class SMSService:
    """SMS alert service using SMS77 via RapidAPI."""
    
    def __init__(self):
        self.api_key = settings.sms77_key
        self.host = settings.sms77_host
        self.to_number = settings.alert_sms_to
        self.base_url = f"https://{self.host}"
    
    def send_sms(self, message: str, to_number: Optional[str] = None) -> bool:
        """Send SMS alert."""
        
        if not self.api_key:
            logger.error("SMS77 API key not configured")
            return False
        
        try:
            recipient = to_number or self.to_number
            
            if not recipient:
                logger.error("No SMS recipient configured")
                return False
            
            # SMS77 API endpoint
            url = f"{self.base_url}/sms"
            
            # Request parameters
            params = {
                "to": recipient,
                "text": message,
                "from": "RockfallAI"  # Sender ID
            }
            
            # Headers
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": self.host
            }
            
            # Send SMS
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {recipient}")
                return True
            else:
                logger.error(f"SMS send failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return False
    
    def send_risk_alert(
        self, 
        risk_level: str, 
        probability: float, 
        location: Optional[str] = None
    ) -> bool:
        """Send formatted risk alert SMS."""
        
        # Create concise SMS message (SMS character limit)
        message_parts = [
            f"🚨 {risk_level} RISK ALERT",
            f"Rockfall probability: {probability:.1%}",
            f"Time: {datetime.utcnow().strftime('%H:%M UTC')}"
        ]
        
        if location:
            message_parts.append(f"Location: {location}")
        
        message_parts.append("Evacuate immediately!")
        
        message = " | ".join(message_parts)
        
        # Ensure message is within SMS limits (160 characters)
        if len(message) > 160:
            message = f"🚨 {risk_level} RISK - {probability:.1%} - {location or 'Unknown'} - Evacuate now!"
        
        return self.send_sms(message)
    
    def test_connection(self) -> Dict:
        """Test SMS service connection."""
        if not self.api_key:
            return {
                'status': 'error',
                'message': 'SMS77 API key not configured'
            }
        
        try:
            # Send a test SMS
            test_message = "Test SMS from Rockfall Prediction System"
            test_result = self.send_sms(test_message)
            
            return {
                'status': 'success' if test_result else 'error',
                'message': 'Test SMS sent' if test_result else 'Test SMS failed',
                'configured': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'configured': True
            }

class AlertManager:
    """Main alert management class."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.alert_history = []
    
    def send_alert(
        self,
        message: str,
        risk_level: str,
        probability: float,
        channels: List[str],
        location: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, bool]:
        """Send alert through specified channels."""
        
        results = {}
        
        # Send email alert
        if 'email' in channels:
            try:
                results['email'] = self.email_service.send_risk_alert(
                    risk_level, probability, location, metadata
                )
            except Exception as e:
                logger.error(f"Email alert failed: {e}")
                results['email'] = False
        
        # Send SMS alert
        if 'sms' in channels:
            try:
                results['sms'] = self.sms_service.send_risk_alert(
                    risk_level, probability, location
                )
            except Exception as e:
                logger.error(f"SMS alert failed: {e}")
                results['sms'] = False
        
        # Log alert
        alert_record = {
            'timestamp': datetime.utcnow(),
            'message': message,
            'risk_level': risk_level,
            'probability': probability,
            'channels': channels,
            'results': results,
            'location': location,
            'metadata': metadata
        }
        
        self.alert_history.append(alert_record)
        
        return results
    
    def should_send_alert(self, probability: float, risk_level: str) -> bool:
        """Determine if alert should be sent based on thresholds."""
        
        # Alert thresholds
        thresholds = {
            'HIGH': 0.7,    # Always alert for high risk
            'MEDIUM': 0.5,  # Alert for medium risk above 50%
            'LOW': 0.9      # Only alert for low risk if very high probability
        }
        
        threshold = thresholds.get(risk_level, 0.5)
        return probability >= threshold
    
    def get_alert_statistics(self) -> Dict:
        """Get alert sending statistics."""
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'success_rate': 0.0,
                'channel_stats': {}
            }
        
        total_alerts = len(self.alert_history)
        successful_alerts = 0
        channel_stats = {'email': 0, 'sms': 0}
        
        for alert in self.alert_history:
            if any(alert['results'].values()):
                successful_alerts += 1
            
            for channel, success in alert['results'].items():
                if success:
                    channel_stats[channel] = channel_stats.get(channel, 0) + 1
        
        return {
            'total_alerts': total_alerts,
            'successful_alerts': successful_alerts,
            'success_rate': successful_alerts / total_alerts if total_alerts > 0 else 0.0,
            'channel_stats': channel_stats
        }
    
    def health_check(self) -> Dict:
        """Check health of all alert services."""
        email_health = self.email_service.test_connection()
        sms_health = self.sms_service.test_connection()
        
        overall_status = 'healthy'
        if email_health['status'] == 'error' and sms_health['status'] == 'error':
            overall_status = 'error'
        elif email_health['status'] == 'error' or sms_health['status'] == 'error':
            overall_status = 'warning'
        
        return {
            'status': overall_status,
            'email': email_health,
            'sms': sms_health,
            'statistics': self.get_alert_statistics()
        }

# Global alert manager instance
alert_manager = AlertManager()

# Convenience functions
def send_alert(
    message: str,
    risk_level: str,
    probability: float,
    channels: List[str],
    location: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, bool]:
    """Send alert using global alert manager."""
    return alert_manager.send_alert(message, risk_level, probability, channels, location, metadata)

def send_email_alert(subject: str, content: str, to_email: Optional[str] = None) -> bool:
    """Send simple email alert."""
    return alert_manager.email_service.send_email(subject, content, to_email)

def send_sms_alert(message: str, to_number: Optional[str] = None) -> bool:
    """Send simple SMS alert."""
    return alert_manager.sms_service.send_sms(message, to_number)

def health_check() -> Dict:
    """Check alert services health."""
    return alert_manager.health_check()

if __name__ == "__main__":
    # Test alert services
    print("Testing Alert Services...")
    
    health = health_check()
    print(f"Health Check: {health}")
    
    # Test email if configured
    if health['email']['status'] != 'error':
        print("Testing email service...")
        result = send_email_alert(
            "Test Alert - Rockfall System",
            "This is a test alert from the rockfall prediction system."
        )
        print(f"Email test result: {result}")
    
    # Test SMS if configured
    if health['sms']['status'] != 'error':
        print("Testing SMS service...")
        result = send_sms_alert("Test alert from Rockfall System")
        print(f"SMS test result: {result}")
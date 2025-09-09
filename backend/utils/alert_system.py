import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, List
import json

class AlertSystem:
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        self.sms_api_key = os.getenv('SMS77IO_RAPIDAPI_KEY')
        self.sms_host = os.getenv('SMS77IO_HOST')
        
    def send_email_alert(self, to_email: str, alert_data: Dict) -> bool:
        """Send email alert using SendGrid"""
        try:
            message = Mail(
                from_email='alerts@rockfallsystem.com',
                to_emails=to_email,
                subject=f"ROCKFALL ALERT - {alert_data['risk_class']} Risk Detected",
                html_content=self._create_email_template(alert_data)
            )
            
            response = self.sendgrid_client.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_sms_alert(self, phone_number: str, alert_data: Dict) -> bool:
        """Send SMS alert using SMS77.io"""
        try:
            url = f"https://{self.sms_host}/rcs/events"
            
            payload = {
                "to": phone_number,
                "text": self._create_sms_message(alert_data)
            }
            
            headers = {
                "X-RapidAPI-Key": self.sms_api_key,
                "X-RapidAPI-Host": self.sms_host,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def _create_email_template(self, alert_data: Dict) -> str:
        """Create HTML email template"""
        risk_color = {
            'Low': '#28a745',
            'Medium': '#ffc107', 
            'High': '#dc3545'
        }.get(alert_data['risk_class'], '#6c757d')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: {risk_color}; text-align: center;">
                    🚨 ROCKFALL ALERT - {alert_data['risk_class']} Risk
                </h1>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Alert Details:</h3>
                    <ul>
                        <li><strong>Risk Level:</strong> {alert_data['risk_class']}</li>
                        <li><strong>Probability:</strong> {alert_data['risk_probability']:.2%}</li>
                        <li><strong>Location:</strong> Mine Site Sector {alert_data.get('sector', 'Unknown')}</li>
                        <li><strong>Timestamp:</strong> {alert_data.get('timestamp', 'Now')}</li>
                    </ul>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h4>Recommended Actions:</h4>
                    <p>{'Immediate evacuation required!' if alert_data['risk_class'] == 'High' else 
                       'Monitor conditions closely.' if alert_data['risk_class'] == 'Medium' else 
                       'Continue normal operations with awareness.'}</p>
                </div>
                
                <p style="text-align: center; margin-top: 30px; color: #6c757d;">
                    This is an automated alert from the AI Rockfall Prediction System
                </p>
            </div>
        </body>
        </html>
        """
    
    def _create_sms_message(self, alert_data: Dict) -> str:
        """Create SMS message"""
        return f"🚨 ROCKFALL ALERT: {alert_data['risk_class']} risk detected ({alert_data['risk_probability']:.0%} probability). Sector {alert_data.get('sector', 'Unknown')}. Check dashboard for details."
    
    def send_bulk_alerts(self, recipients: List[Dict], alert_data: Dict) -> Dict[str, int]:
        """Send alerts to multiple recipients"""
        results = {'email_sent': 0, 'sms_sent': 0, 'email_failed': 0, 'sms_failed': 0}
        
        for recipient in recipients:
            if recipient.get('email'):
                if self.send_email_alert(recipient['email'], alert_data):
                    results['email_sent'] += 1
                else:
                    results['email_failed'] += 1
            
            if recipient.get('phone'):
                if self.send_sms_alert(recipient['phone'], alert_data):
                    results['sms_sent'] += 1
                else:
                    results['sms_failed'] += 1
        
        return results
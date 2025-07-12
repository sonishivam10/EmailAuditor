import email
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import os
import re
from io import BytesIO

class EmailParser:
    def __init__(self, eml_path: str):
        self.eml_path = eml_path
        self.messages = self._load_eml_thread()

    def _load_eml_thread(self) -> List[email.message.Message]:
        """Load email thread - handles both single emails and email threads."""
        with open(self.eml_path, 'rb') as f:
            content = f.read()
        
        # Try to detect if this is a thread with multiple emails
        # Look for common email thread markers
        thread_markers = [
            b'From: ',
            b'\nFrom: ',
            b'\r\nFrom: ',
            b'Subject: ',
            b'\nSubject: ',
            b'\r\nSubject: '
        ]
        
        # Count potential email starts
        email_count = 0
        for marker in thread_markers:
            email_count += content.count(marker)
        
        if email_count > 2:  # Likely a thread
            return self._parse_email_thread(content)
        else:
            # Single email
            return [BytesParser(policy=policy.default).parse(BytesIO(content))]

    def _parse_email_thread(self, content: bytes) -> List[email.message.Message]:
        """Parse multiple emails from a thread."""
        messages = []
        
        # Split by common email boundaries
        # This is a simplified approach - real email threads can be complex
        email_parts = re.split(b'\n(?=From: )', content)
        
        for part in email_parts:
            if part.strip():
                try:
                    message = BytesParser(policy=policy.default).parse(BytesIO(part))
                    messages.append(message)
                except Exception as e:
                    # Skip malformed parts
                    print(f"Warning: Skipping malformed email part: {e}")
                    continue
        
        return messages if messages else [BytesParser(policy=policy.default).parse(BytesIO(content))]

    def get_content(self) -> Dict[str, Any]:
        """Get content from the first email in the thread."""
        if not self.messages:
            return {'text': '', 'html': '', 'attachments': []}
        
        return self._extract_content_from_message(self.messages[0])

    def get_thread_content(self) -> List[Dict[str, Any]]:
        """Get content from all emails in the thread."""
        thread_content = []
        for message in self.messages:
            thread_content.append(self._extract_content_from_message(message))
        return thread_content

    def _extract_content_from_message(self, message: email.message.Message) -> Dict[str, Any]:
        """Extract content from a single email message."""
        text = ""
        html = ""
        attachments = []
        
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                try:
                    text += part.get_content()
                except Exception:
                    text += str(part.get_payload(decode=True), 'utf-8', errors='ignore')
            elif content_type == 'text/html':
                try:
                    html += part.get_content()
                except Exception:
                    html += str(part.get_payload(decode=True), 'utf-8', errors='ignore')
            elif part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    attachments.append({
                        'filename': filename,
                        'content_type': content_type
                    })
        
        if html and not text:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
        
        return {'text': text, 'html': html, 'attachments': attachments}

    def has_image_attachment(self) -> bool:
        """Check if any email in the thread has image attachments."""
        for message in self.messages:
            for part in message.walk():
                if part.get_content_disposition() == 'attachment':
                    if part.get_content_type().startswith('image/'):
                        return True
        return False

    def get_thread_summary(self) -> Dict[str, Any]:
        """Get summary information about the email thread."""
        return {
            'email_count': len(self.messages),
            'has_image_attachment': self.has_image_attachment(),
            'total_attachments': sum(len(self._extract_content_from_message(msg)['attachments']) for msg in self.messages)
        } 
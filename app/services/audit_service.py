import json
import os
from typing import Dict, Any
from flask import current_app
from .email_parser import EmailParser
from .rules_engine import RulesEngine
from .audit_report import AuditReport
from . import rules_impl
from ..models import EmailAudit, User
from ..models.database import db

class AuditService:
    """Service for email auditing operations."""
    
    def __init__(self):
        self.rules_path = os.path.join(current_app.root_path, 'rules.json')
    
    def audit_email_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Audit a single email content."""
        rules_engine = RulesEngine(self.rules_path)
        rule_results = []
        
        for rule in rules_engine.rules:
            func = getattr(rules_impl, rule['function'], None)
            if func:
                result = func(content['text'])
                rule_results.append({
                    'rule_id': rule['id'],
                    'description': rule['description'],
                    **result
                })
            else:
                rule_results.append({
                    'rule_id': rule['id'],
                    'description': rule['description'],
                    'passed': False,
                    'score': 0,
                    'justification': f"Rule function {rule['function']} not implemented."
                })
        
        return rule_results
    
    def audit_email_file(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """Audit an email file and save results."""
        try:
            # Parse email
            email_parser = EmailParser(file_path)
            content = email_parser.get_content()
            
            # Audit content
            rule_results = self.audit_email_content(content)
            report = AuditReport(rule_results).to_dict()
            
            # Save audit result
            audit = EmailAudit(
                user_id=user_id,
                email_content=content['text'][:500],  # Store first 500 chars
                audit_result=json.dumps(report),
                file_name=os.path.basename(file_path),
                file_size=os.path.getsize(file_path)
            )
            db.session.add(audit)
            db.session.commit()
            
            current_app.logger.info(f"Email audited successfully for user {user_id}")
            return report
            
        except Exception as e:
            current_app.logger.error(f"Error auditing email: {str(e)}")
            raise
    
    def get_user_audit_history(self, user_id: int, limit: int = 10) -> list:
        """Get user's audit history."""
        audits = EmailAudit.query.filter_by(user_id=user_id)\
            .order_by(EmailAudit.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [audit.to_dict() for audit in audits] 
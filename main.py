import argparse
import os
import json
from email_parser import EmailParser
from rules_engine import RulesEngine
from audit_report import AuditReport
import rules_impl

RULES_IMPL_MAP = {
    'check_greeting': rules_impl.check_greeting,
    'check_grammar': rules_impl.check_grammar,
    'check_clarity': rules_impl.check_clarity,
}

def audit_email_content(content, rules_engine):
    """Audit a single email content."""
    rule_results = []
    for rule in rules_engine.rules:
        func = RULES_IMPL_MAP.get(rule['function'])
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

def main():
    parser = argparse.ArgumentParser(description='Email Audit Service')
    parser.add_argument('eml_file', help='.eml file to audit')
    parser.add_argument('--rules', default=os.path.join(os.path.dirname(__file__), 'rules.json'), help='Path to rules.json')
    parser.add_argument('--thread', action='store_true', help='Process entire email thread instead of just first email')
    args = parser.parse_args()

    email_parser = EmailParser(args.eml_file)
    thread_summary = email_parser.get_thread_summary()
    
    if not email_parser.has_image_attachment():
        print('Warning: No image attachment found in the email thread.')

    rules_engine = RulesEngine(args.rules)
    
    if args.thread and thread_summary['email_count'] > 1:
        # Process entire thread
        thread_content = email_parser.get_thread_content()
        thread_results = []
        
        for i, content in enumerate(thread_content):
            email_results = audit_email_content(content, rules_engine)
            thread_results.append({
                'email_index': i + 1,
                'content_preview': content['text'][:100] + '...' if len(content['text']) > 100 else content['text'],
                'results': email_results
            })
        
        # Calculate overall thread score
        all_scores = []
        for email_result in thread_results:
            for rule_result in email_result['results']:
                if rule_result['score'] is not None:
                    all_scores.append(rule_result['score'])
        
        overall_score = int(sum(all_scores) / len(all_scores)) if all_scores else 0
        
        report = {
            'thread_summary': thread_summary,
            'overall_score': overall_score,
            'emails': thread_results
        }
    else:
        # Process single email (default behavior)
        content = email_parser.get_content()
        rule_results = audit_email_content(content, rules_engine)
        report = AuditReport(rule_results).to_dict()
        report['thread_summary'] = thread_summary
    
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main() 
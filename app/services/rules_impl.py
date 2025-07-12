import re
import math

def check_greeting(email_text):
    """Check if the email contains an appropriate greeting."""
    greetings = ["hello", "hi", "dear", "greetings", "good morning", "good afternoon", "good evening"]
    email_lower = email_text.lower()
    
    # Check for greetings in the first few lines
    first_lines = email_lower.split('\n')[:3]
    for line in first_lines:
        # Use word boundaries to avoid partial matches
        for greet in greetings:
            if re.search(r'\b' + re.escape(greet) + r'\b', line):
                return {'passed': True, 'score': 10, 'justification': 'Professional greeting found.'}
    
    return {'passed': False, 'score': 0, 'justification': 'No appropriate greeting detected. Consider adding a professional greeting.'}

def check_grammar(email_text):
    """Check grammar quality using multiple metrics."""
    if not email_text.strip():
        return {'passed': False, 'score': 0, 'justification': 'Email content is empty.'}
    
    # Basic grammar checks
    issues = []
    score = 10
    
    # Check for proper sentence endings
    sentences = re.split(r'[.!?]+', email_text)
    incomplete_sentences = [s.strip() for s in sentences if s.strip() and not s.strip().endswith(('.', '!', '?'))]
    if incomplete_sentences:
        issues.append(f"Found {len(incomplete_sentences)} incomplete sentences")
        score -= 2
    
    # Check for common grammar mistakes
    common_mistakes = [
        (r'\b(you\'re|your)\b', 'your/you\'re confusion'),
        (r'\b(there|their|they\'re)\b', 'there/their/they\'re confusion'),
        (r'\b(its|it\'s)\b', 'its/it\'s confusion'),
        (r'\b(loose|lose)\b', 'loose/lose confusion'),
        (r'\b(affect|effect)\b', 'affect/effect confusion'),
        (r'\bcant\b', 'missing apostrophe in "can\'t"'),
        (r'\bdont\b', 'missing apostrophe in "don\'t"'),
        (r'\bwont\b', 'missing apostrophe in "won\'t"'),
        (r'\bim\b', 'missing apostrophe in "I\'m"'),
        (r'\bive\b', 'missing apostrophe in "I\'ve"'),
        (r'\byouve\b', 'missing apostrophe in "you\'ve"'),
        (r'\bweve\b', 'missing apostrophe in "we\'ve"'),
        (r'\btheyve\b', 'missing apostrophe in "they\'ve"')
    ]
    
    mistake_count = 0
    for pattern, description in common_mistakes:
        if re.search(pattern, email_text, re.IGNORECASE):
            mistake_count += 1
    
    if mistake_count > 0:
        issues.append(f"Found {mistake_count} potential grammar issues")
        score -= min(3, mistake_count)
    
    # Basic readability check
    word_count = len(email_text.split())
    if word_count > 0:
        avg_word_length = sum(len(word) for word in email_text.split()) / word_count
        if avg_word_length > 8:
            issues.append("Text might be too complex (long average word length)")
            score -= 1
        
        # Check sentence complexity
        sentences = re.split(r'[.!?]+', email_text)
        if sentences:
            avg_sentence_length = word_count / len([s for s in sentences if s.strip()])
            if avg_sentence_length > 25:
                issues.append("Sentences are too long - consider breaking them up")
                score -= 1
    
    justification = "Grammar quality is good." if not issues else f"Grammar issues found: {'; '.join(issues)}"
    return {'passed': score >= 7, 'score': max(0, score), 'justification': justification}

def check_clarity(email_text):
    """Check email clarity and structure."""
    if not email_text.strip():
        return {'passed': False, 'score': 0, 'justification': 'Email content is empty.'}
    
    issues = []
    score = 10
    
    # Check email length
    word_count = len(email_text.split())
    if word_count < 10:
        issues.append("Email is too short - may lack necessary detail")
        score -= 3
    elif word_count > 500:
        issues.append("Email is very long - consider breaking into smaller parts")
        score -= 2
    
    # Check for clear structure
    paragraphs = [p.strip() for p in email_text.split('\n\n') if p.strip()]
    if len(paragraphs) < 2:
        issues.append("Email lacks clear paragraph structure")
        score -= 2
    
    # Check for action items or clear purpose
    action_words = ["please", "request", "need", "require", "action", "follow up", "next steps"]
    if not any(word in email_text.lower() for word in action_words):
        issues.append("Email may lack clear purpose or action items")
        score -= 1
    
    # Check for professional tone indicators
    professional_indicators = ["thank you", "regards", "sincerely", "best regards", "kind regards"]
    if not any(indicator in email_text.lower() for indicator in professional_indicators):
        issues.append("Email may benefit from a professional closing")
        score -= 1
    
    # Check for excessive use of exclamation marks
    exclamation_count = email_text.count('!')
    if exclamation_count > 3:
        issues.append("Too many exclamation marks - may appear unprofessional")
        score -= 2
    
    # Check for all caps (shouting)
    if re.search(r'\b[A-Z]{3,}\b', email_text):
        issues.append("Avoid using ALL CAPS - it appears as shouting")
        score -= 2
    
    justification = "Email is clear and well-structured." if not issues else f"Clarity issues: {'; '.join(issues)}"
    return {'passed': score >= 7, 'score': max(0, score), 'justification': justification} 
# Email Audit Service

## Overview
This service audits email threads (.eml files) for quality and compliance, using a dynamic rules engine. It outputs a detailed report with scores, per-rule feedback, and a summary of strengths and areas for improvement.

## Features
- **Dynamic Rules Engine**: Rules defined in JSON, no code changes needed for new rules
- **Email Thread Processing**: Handles both single emails and complete email threads
- **Comprehensive Parsing**: Parses .eml files (plain text, basic HTML, attachments)
- **Advanced Grammar Checks**: Detects incomplete sentences, common mistakes, and readability issues
- **Clarity Analysis**: Evaluates structure, tone, formatting, and professional standards
- **Per-rule Scoring**: Detailed scoring and justifications for each rule
- **Thread Summary**: Provides overview of email thread characteristics
- **Dockerized**: Easy local deployment and execution

## Assignment Requirements Coverage

### ✅ Dynamic Rules Engine
- Rules defined in `rules.json` with function mappings
- Can add, update, or remove rules without changing core code
- Each rule evaluates one specific guideline

### ✅ Audit Report Generation
- Numerical score per email thread (0-10 scale)
- Pass/fail per rule with detailed explanations
- Summary of strengths and areas for improvement
- Thread-level analysis when processing multiple emails

### ✅ Input Handling
- Primary input: .eml file format
- Handles plain-text and basic HTML content
- Image attachment detection and validation
- Email thread parsing and processing

### ✅ Containerization
- Complete Docker setup with Dockerfile
- docker-compose.yml for easy local execution
- Instructions for running with `docker-compose up`

## Setup & Usage

### Prerequisites
- Docker and docker-compose installed

### Dependencies
The service requires the following Python packages (specified in `requirements.txt`):
- `beautifulsoup4` - For HTML parsing
- `textstat` - For text analysis and scoring

### Running Locally
1. Place your `.eml` file in the `emailAudit` directory.
2. Build and run the service:

   **Single Email (default):**
   ```sh
   docker-compose run --rm email-audit your-email-file.eml
   ```

   **Email Thread:**
   ```sh
   docker-compose run --rm email-audit your-email-file.eml --thread
   ```

### Output
- JSON report printed to stdout
- Includes thread summary, overall score, and per-email results

## Project Structure
- `main.py` - Entry point with thread processing support
- `email_parser.py` - Parses .eml files and email threads
- `rules_engine.py` - Loads and applies rules
- `rules_impl.py` - Enhanced rule logic implementations
- `audit_report.py` - Generates the report
- `rules.json` - List of rules
- `test_email.eml` - Sample good quality email
- `test_email_with_issues.eml` - Sample problematic email
- `test_email_thread.eml` - Sample email thread



## Enhanced Features Beyond Requirements
- **Sophisticated Grammar Analysis**: Incomplete sentence detection, common mistake identification, readability scoring
- **Professional Communication Standards**: Greeting detection, tone analysis, formatting checks
- **Thread Processing**: Support for analyzing complete email conversations
- **Comprehensive Scoring**: Detailed feedback with specific improvement suggestions

##  Test Files
- `test_email.eml` - Professional email demonstrating good practices
- `test_email_with_issues.eml` - Email with multiple quality issues
- `test_email_thread.eml` - Complete email conversation with varying quality
   - All test files include image attachments as required 

## Usage Examples

### Adding New Rules

1. **Add rule definition** to `rules.json`:
   ```json
   {
     "id": "response_time",
     "description": "Check if email responds within expected timeframe.",
     "function": "check_response_time"
   }
   ```

2. **Implement rule function** in `rules_impl.py`:
   ```python
   def check_response_time(email_text):
       # Your implementation here
       return {'passed': True, 'score': 10, 'justification': 'Response time is acceptable.'}
   ```

3. **Add to mapping** in `main.py`:
   ```python
   RULES_IMPL_MAP = {
       # ... existing rules
       'check_response_time': rules_impl.check_response_time,
   }
   ```

### Custom Email Analysis

```bash
# Analyze your own email file
docker-compose run --rm email-audit your-email-file.eml

# Analyze with custom rules file
docker-compose run --rm email-audit your-email-file.eml --rules custom-rules.json
```

## Approach & Technology Choices

- **Python**: Chosen for rapid development
- **Docker**: Ensures consistent deployment across environments
- **JSON Configuration**: Enables dynamic rule management
- **Modular Architecture**: Facilitates easy extension and maintenance
- **Comprehensive Testing**: Multiple test scenarios with real email formats

## 📋 Assumptions & Design Decisions

### Email Format & Parsing
- **Email Format**: Assumes standard .eml format with proper MIME structure
- **Encoding**: Assumes UTF-8 encoding for email content; fallback handling for encoding issues
- **HTML Parsing**: Basic HTML support only
- **Attachments**: Focuses on image attachments for compliance
- **Thread Detection**: Uses simple heuristics (multiple "From:" headers) to detect email threads

### Grammar & Quality Assessment
- **Grammar Rules**: Implements basic grammar checks; assumes professional business communication standards
- **Greeting Detection**: Assumes professional greetings should appear in the first 3 lines of email content
- **Sentence Completion**: Assumes sentences should end with proper punctuation (., !, ?)
- **Common Mistakes**: Focuses on frequently confused words and missing apostrophes in contractions

### Professional Standards
- **Tone Assessment**: Assumes professional emails should avoid excessive exclamation marks (>3) and ALL CAPS
- **Structure**: Assumes emails should have multiple paragraphs and clear purpose indicators
- **Length**: Assumes emails should be between 10-500 words for optimal clarity
- **Closings**: Assumes professional emails should include appropriate closing phrases


### Business Rules
- **Scoring Scale**: Uses 0-10 scale where 7+ is considered acceptable quality
- **Rule Weighting**: All rules have equal weight in overall score calculation

### Limitations & Constraints
- **Language**: Assumes English language emails only
- **Domain**: Focuses on business/professional communication, not personal emails
- **Real-time**: Designed for batch processing, not real-time email analysis
- **Scale**: Optimized for individual email analysis, not high-volume enterprise processing
- **Accuracy**: Rule-based approach provides guidance but may not catch all nuanced issues

### Extensibility Assumptions
- **Rule Addition**: Assumes new rules can be added without breaking existing functionality
- **Configuration**: Assumes JSON format is sufficient for rule definitions
- **Function Mapping**: Assumes rule functions follow consistent return format
- **Error Handling**: Assumes graceful degradation when rules fail or content is malformed
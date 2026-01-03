# SkillLink - AI Resume & Job Connector

## Project Overview
SkillLink is a comprehensive Flask-based web application that helps blue-collar workers create professional resumes and find job opportunities using AI-powered conversational interfaces. The platform also enables employers to post jobs and discover qualified candidates through intelligent matching algorithms.

## Core Features

### Worker Features
- **Conversational Resume Builder**: Gemini AI-powered chat interface that guides workers through resume creation in English, Hindi, or Odia
- **Bidirectional Voice Integration**: 
  - Speech-to-Text (STT) for voice input in multiple languages
  - Text-to-Speech (TTS) for AI responses to be read aloud
  - Auto-speak toggle for hands-free conversation
- **AI Skill Extraction**: Automatically categorizes skills into Technical, Soft Skills, and Tools/Equipment
- **ATS-Optimized Resume Generation**: Creates professional, single-page resumes with PDF export
- **Smart Job Matching**: AI-powered job recommendations with 1-10 scoring based on skills, experience, and location
- **Job Applications**: Direct application submission within the platform

### Employer Features
- **Job Posting**: Easy-to-use interface for posting job opportunities
- **AI Candidate Matching**: Intelligent candidate discovery with match scores and reasoning
- **Dashboard**: View all posted jobs and application statistics
- **Candidate Management**: Browse matched candidates with detailed profiles

## Technical Stack

### Backend
- Flask 3.0.0 - Web framework
- SQLAlchemy 2.0.23 - Database ORM
- Google Gemini AI (gemini-2.5-flash, gemini-2.5-pro) - Conversational AI and matching
- SQLite - Database
- ReportLab 4.0.7 - PDF generation
- Bleach 6.1.0 - Input sanitization

### Frontend
- Jinja2 - Template engine
- Vanilla JavaScript - Bidirectional voice (STT/TTS), chat interface, form handling
- Custom CSS - Responsive design for mobile and desktop
- Web Speech API - Speech recognition and synthesis

## Project Structure
```
skilllink/
├── app.py                      # Main Flask application with all routes
├── config.py                   # Application configuration
├── models/                     # Database models
│   ├── database.py            # DB initialization and session management
│   ├── user.py                # Worker profile model
│   ├── organization.py        # Employer model
│   ├── job.py                 # Job listing model
│   └── application.py         # Job application model
├── utils/                      # AI and utility modules
│   ├── ai_assistant.py        # Gemini conversational assistant
│   ├── skill_extractor.py     # AI skill categorization
│   ├── job_matcher.py         # AI job matching algorithm
│   ├── resume_generator.py    # ATS resume content generation
│   ├── pdf_generator.py       # PDF export functionality
│   ├── validators.py          # Input validation and sanitization
│   └── translator.py          # Multilingual translation
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navbar and footer
│   ├── index.html             # Landing page
│   ├── worker/                # Worker journey templates
│   │   ├── chat.html          # Conversational interface
│   │   ├── resume_preview.html
│   │   └── jobs.html
│   └── employer/              # Employer journey templates
│       ├── dashboard.html
│       ├── post_job.html
│       └── matches.html
└── static/                     # Static assets
    ├── css/style.css          # Responsive styling
    ├── js/
    │   ├── voice.js           # Voice input handling
    │   ├── chat.js            # Chat interface logic
    │   └── validation.js      # Form validation
    └── resumes/               # Generated PDF resumes
```

## Database Schema

### Users Table
- Stores worker profiles with skills, experience, and resume data
- JSON fields for flexible skill and work history storage
- Tracks chat history for conversational context

### Organizations Table
- Employer company information
- Contact details and industry classification

### Jobs Table
- Job listings with requirements and salary ranges
- Required skills stored as JSON array
- Status tracking (active/inactive)

### Applications Table
- Links workers to jobs they've applied for
- Stores AI-generated match scores and reasoning
- Application status tracking

## AI Integration

### Gemini API Usage
1. **Conversational Resume Building** (gemini-2.5-flash)
   - Multi-turn conversations with context retention
   - Multilingual support (English/Hindi/Odia)
   - Structured data extraction from natural language

2. **Skill Extraction** (gemini-2.5-flash)
   - Normalizes and categorizes raw skills
   - Generates ATS-friendly skill descriptions

3. **Job Matching** (gemini-2.5-pro)
   - Scores candidates 1-10 for each job
   - Provides reasoning for match scores
   - Considers skills, experience, location, and growth potential

4. **Resume Generation** (gemini-2.5-pro)
   - Creates professional, one-page resumes
   - Uses action verbs and quantifiable achievements
   - Optimized for Applicant Tracking Systems

5. **Translation** (gemini-2.5-flash)
   - Real-time UI and response translation
   - Supports English, Hindi, and Odia

## Environment Variables Required
- `GEMINI_API_KEY` - Google Gemini API key (required for AI features)
- `SESSION_SECRET` - Flask session secret (auto-configured)

## Security Features
- Indian phone number validation (10 digits, starts with 6-9)
- Input sanitization using Bleach
- HTTP-only session cookies
- 24-hour session expiration
- CSRF protection via session management

## Recent Changes

### October 21, 2025 - Comprehensive Dashboard System
- Built complete dashboard system for both workers and employers
- **Worker Dashboard Features:**
  - Resume summary with quick view and download options
  - Applications list showing all jobs applied for with status tracking (Pending/Approved/Rejected)
  - Visual status badges with color coding for easy identification
  - Empty states with helpful call-to-action when no resume or applications exist
- **Worker Account Page:**
  - View profile information (name, phone, trade, location, experience, language)
  - Edit and update profile details with real-time validation
  - Success/error messaging for profile updates
- **Employer Applicants Management:**
  - Dedicated page for each job showing all applicants
  - Rich candidate information including skills, experience, location
  - Status update functionality (Pending → Approved/Rejected) with immediate persistence
  - Applicant details displayed in organized, scannable cards
- **Employer Account Page:**
  - View organization profile (name, phone, email, location, industry, description)
  - Edit and update organization details
  - Form validation and success messaging
- **Navigation Updates:**
  - Added "Dashboard" link for workers and employers
  - Added "Account" link for profile management
  - Renamed "Chat" to "Build Resume" for clarity
  - Renamed "Jobs" to "Browse Jobs" for clarity
- **Comprehensive Styling:**
  - Professional status badges (yellow for pending, green for approved, red for rejected)
  - Card-based layouts for better data organization
  - Responsive design that works seamlessly on mobile and desktop
  - Hover effects and smooth transitions for better UX
  - Empty state designs with clear next-step guidance
- **Bidirectional Data Flow:**
  - When workers apply to jobs, applications automatically appear in employer's applicants list
  - When employers update application status, changes instantly reflect in worker's dashboard
  - All status changes persist to database and sync across both dashboards
- All features reviewed and approved by architect with no security issues found

### October 21, 2025 - Pixel-Perfect PDF Resume Generation
- Replaced ReportLab-based PDF generation with WeasyPrint for HTML-to-PDF conversion
- Created dedicated resume_pdf.html template with print-optimized CSS
- Implemented generate_pdf_resume_from_html() function for pixel-perfect PDF output
- Updated download endpoint to use WeasyPrint-based generation
- PDF downloads now exactly match the HTML preview shown on screen
- Added print-specific CSS with proper page breaks, margins, and typography
- All changes reviewed and approved by architect

### October 21, 2025 - Fresh GitHub Import Setup for Replit
- Successfully imported project from GitHub repository
- Installed all Python dependencies using packager tool (Flask, google-genai, SQLAlchemy, weasyprint, etc.)
- Configured GEMINI_API_KEY secret in Replit environment for AI features
- Set up Flask workflow to run on port 5000 with 0.0.0.0 binding for development
- Configured deployment with Gunicorn (4 workers, autoscale mode) for production
- Created comprehensive .gitignore for Python projects
- Verified application is running successfully and accessible
- Website tested and confirmed fully functional with all features working

### October 20, 2025 - Enhanced Voice Features and Odia Language Support
- Added Odia language support to AI assistant with native prompts
- Implemented bidirectional voice integration:
  - Speech-to-Text (STT) for English, Hindi, and Odia
  - Text-to-Speech (TTS) with auto-speak toggle for AI responses
  - Language-specific voice synthesis (or-IN, hi-IN, en-US)
- Added speaker button (🔊) to toggle AI response readback
- Enhanced chat interface with Odia translations
- Updated translator utility to support Odia language
- Improved voice.js with robust speech synthesis lifecycle management
- All voice features tested and verified by architect review

### October 20, 2025 - Replit Environment Setup
- Configured Python 3.11 environment with all dependencies
- Fixed imports to use `google-genai` SDK (updated from `google.generativeai`)
- Configured Flask workflow to run on port 5000 with 0.0.0.0 binding
- Set up deployment configuration using Gunicorn for production
- Added comprehensive .gitignore for Python projects
- Configured GEMINI_API_KEY secret management
- Successfully tested application - server running and website accessible

### October 18, 2025 - Initial Implementation
- Initial project setup with complete implementation
- Integrated Gemini AI for all conversational and matching features
- Implemented worker journey (chat → resume → jobs)
- Implemented employer journey (dashboard → post job → view matches)
- Added responsive design for mobile compatibility
- Voice input support using Web Speech API
- PDF resume generation and download
- Multilingual support (English/Hindi)
- Application successfully tested and verified working

## User Preferences
- None specified yet

## Development Notes
- Database is SQLite for easy development; can be upgraded to PostgreSQL for production
- All AI features use the Gemini API via the Replit integration
- Voice features (STT/TTS) require modern browsers (Chrome, Edge) with Web Speech API support
- Odia language support uses native Odia script (ଓଡ଼ିଆ)
- PDF generation uses WeasyPrint for pixel-perfect HTML-to-PDF conversion (matches web preview exactly)
- Text-to-Speech quality depends on browser's available voices for each language

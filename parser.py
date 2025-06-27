import pytesseract
import easyocr
from pdf2image import convert_from_path
from PIL import Image
import re
import numpy as np

# Path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def extract_skills(text):
    skill_keywords = [
        'Python', 'Java', 'C', 'C++', 'C#', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'Ruby',
        'Kotlin', 'Swift', 'Scala', 'PHP', 'Perl', 'R', 'Dart', 'Objective-C', 'MATLAB',
        'HTML', 'CSS', 'Bootstrap', 'Tailwind', 'React', 'Angular', 'Vue.js',
        'Node.js', 'Express.js', 'Django', 'Flask', 'Spring Boot', 'FastAPI', 'Laravel',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Oracle', 'Redis',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'CI/CD', 'Jenkins',
        'Git', 'GitHub', 'Bitbucket', 'Linux', 'Unix', 'Windows', 'TensorFlow', 'PyTorch',
        'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision'
    ]
    found_skills = []
    for skill in skill_keywords:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ''

# ------------------- EXTRACT PHONE -------------------
def extract_phone(text):
    match = re.search(r'(\+\d{1,3}[\s-]?)?(\d{10}|\d{5}[\s-]\d{5})', text)
    return match.group(0).replace(' ', '').replace('-', '') if match else ''

# ------------------- EXTRACT DOB -------------------
def extract_dob(text):
    match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|\bDOB[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text, re.IGNORECASE)
    return match.group(0) if match else ''

# ------------------- EXTRACT EXPERIENCE -------------------
def extract_experience(text):
    matches = re.findall(r'(\d+\+?)\s+(years|yrs|year)', text, re.IGNORECASE)
    years = [int(re.sub(r'\D', '', y[0])) for y in matches if y[0].isdigit() or '+' in y[0]]
    return str(max(years)) if years else '0'


# ------------------- EXTRACT UNIVERSITIES -------------------
def extract_universities(text):
    university_patterns = [
        r'\b[A-Z][a-zA-Z&.\-\s]*University\b',
        r'\bUniversity of [A-Z][a-zA-Z&.\-\s]*\b',
        r'\b[A-Z][a-zA-Z&.\-\s]*Institute of Technology\b',
        r'\b[A-Z][a-zA-Z&.\-\s]*College\b',
        r'\bNational Institute of [A-Z][a-zA-Z&.\-\s]*\b',
        r'\bIndian Institute of [A-Z][a-zA-Z&.\-\s]*\b'
    ]

    matches = []
    for pattern in university_patterns:
        found = re.findall(pattern, text)
        matches.extend(found)

    universities = list(set(match.strip() for match in matches if len(match) > 5))

    return universities if universities else []

def extract_projects(text):
    project_sections = re.findall(r'(?:Projects|Academic Projects|Major Projects)\s*[:\-]*\s*\n(.+?)(?=\n[A-Z][^\n]{1,40}\n|\Z)', 
                                  text, re.IGNORECASE | re.DOTALL)

    projects = []
    for section in project_sections:
        raw_projects = re.split(r'[\n•\-–]+', section)
        for proj in raw_projects:
            proj = proj.strip()
            if len(proj) > 10 and not proj.lower().startswith(('skills', 'tools')):
                projects.append(proj)

    clean_projects = list(set(projects))
    return " | ".join(clean_projects) if clean_projects else ""

# ------------------- EXTRACT DEGREES -------------------
def extract_degrees(text):
    degrees = ['B\.Tech', 'M\.Tech', 'B\.E', 'M\.E', 'BSc', 'MSc', 'BCA', 'MCA', 'MBA', 'PhD','Bachelor','Master']
    found = [deg for deg in degrees if re.search(r'\b' + deg + r'\b', text)]
    return list(set(found))

# ------------------- EXTRACT DESIGNATION -------------------
def extract_designation(text):
    return re.findall(r'(Software Developer | Web Developer | Front-End Developer | Back-End Developer | Full-Stack Developer | Mobile App Developer | Game Developer | DevOps Engineer | Software Engineer in Test | UI/UX Designer | Embedded Systems Developer | Machine Learning Engineer | Data Scientist | Data Analyst | AI Researcher | NLP Engineer | Computer Vision Engineer | Deep Learning Engineer | Data Engineer | Business Intelligence Analyst | Big Data Developer | Network Engineer | System Administrator | Cloud Engineer | IT Support Specialist | Infrastructure Engineer | DevOps Architect | Linux Administrator | Cloud Solutions Architect | Site Reliability Engineer | Cybersecurity Analyst | Penetration Tester | Security Engineer | Information Security Analyst | Network Security Engineer | SOC Analyst | Security Architect | Cryptographer | Malware Analyst | Risk & Compliance Analyst | Database Administrator | Data Architect | SQL Developer | Database Engineer | ETL Developer | Storage Engineer | Hardware Engineer | VLSI Design Engineer | Embedded Software Engineer | Robotics Engineer | Firmware Engineer | IoT Developer | Chip Design Engineer | Web Designer | SEO Specialist | Cloud Developer | SaaS Developer | Web Hosting Technician | Platform Engineer | IT Project Manager | Product Manager | IT Business Analyst | Scrum Master | Agile Coach | IT Consultant | Technical Program Manager | QA Analyst | Test Automation Engineer | Manual Tester | Performance Tester | QA Lead | Computer Science Professor | Technical Trainer | Coding Bootcamp Instructor | EdTech Developer | Blockchain Developer | AR/VR Developer | Game Tester | Computer Forensics Analyst | Tech Support Representative | CAD Engineer | Virtualization Engineer | Open Source Contributor | IT Auditor | Scientific Programmer | Mainframe Developer)', text, re.IGNORECASE)

# ------------------- EXTRACT SUMMARY -------------------
def extract_summary(text):
    # Keywords indicating start of summary section
    summary_keywords = r'(?:Summary|Professional Summary|Career Summary|About Me|Profile)'
    
    # Try to match section heading followed by text until the next section (2+ newlines or end)
    match = re.search(rf'{summary_keywords}[:\s]*\n*(.+?)(?=\n{{2,}}|\n[A-Z][^\n]{1,40}\n|\Z)', 
                      text, re.IGNORECASE | re.DOTALL)
    
    if match:
        summary = match.group(1).strip()
        # Clean excessive internal newlines and spaces
        summary = re.sub(r'\n+', ' ', summary)
        summary = re.sub(r'\s{2,}', ' ', summary)
        return summary

    return None

def extract_fields(text):
    email = extract_email(text)
    phone = extract_phone(text)
    dob = extract_dob(text)
    experience = extract_experience(text)
    skills = extract_skills(text)
    universities = extract_universities(text)
    projects = extract_projects(text)
    degrees = extract_degrees(text)
    designation = extract_designation(text)
    summary = extract_summary(text)

    return {
        "Email": email,
        "Phone": phone,
        "DOB": dob,
        "Experience (Years)": experience,
        "Skills": ', '.join(skills),
        "Universities": ', '.join(universities),
        "Projects": ', '.join(projects),
        "Degrees": ', '.join(degrees),
        "Designation": ', '.join(designation),
        "Summary": summary
    }

def parse_resume(file_path: str, mode="Digital"):
    text = ""
    if mode == "Digital":
        if file_path.lower().endswith(".pdf"):
            images = convert_from_path(file_path)
            for image in images:
                text += pytesseract.image_to_string(image)
        else:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
    else:
        reader = easyocr.Reader(['en'])
        if file_path.lower().endswith(".pdf"):
            images = convert_from_path(file_path)
            for image in images:
                text += " ".join(reader.readtext(np.array(image), detail=0))
        else:
            text = " ".join(reader.readtext(file_path, detail=0))
    
    return extract_fields(text)
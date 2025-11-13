import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import json
import random
import time
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Professional Resume Generator", layout="wide")

# Initialize session state
if 'generated_resumes' not in st.session_state:
    st.session_state.generated_resumes = []

# Fake data generators
def generate_fake_phone():
    return f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"

def generate_fake_email(name):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com"]
    return f"{name.lower().replace(' ', '.')}{random.randint(10,99)}@{random.choice(domains)}"

def generate_unique_name(index, department):
    """Generate a unique name based on index"""
    first_names = [
        "James", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William", "Linda",
        "David", "Elizabeth", "Richard", "Barbara", "Joseph", "Susan", "Thomas", "Jessica",
        "Charles", "Sarah", "Christopher", "Karen", "Daniel", "Nancy", "Matthew", "Lisa",
        "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
        "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle",
        "Kevin", "Carol", "Brian", "Amanda", "George", "Dorothy", "Timothy", "Melissa",
        "Ronald", "Deborah", "Edward", "Stephanie", "Jason", "Rebecca", "Jeffrey", "Sharon",
        "Ryan", "Laura", "Jacob", "Cynthia", "Gary", "Kathleen", "Nicholas", "Amy",
        "Eric", "Angela", "Jonathan", "Shirley", "Stephen", "Anna", "Larry", "Brenda",
        "Justin", "Pamela", "Scott", "Emma", "Brandon", "Nicole", "Benjamin", "Helen",
        "Samuel", "Samantha", "Raymond", "Katherine", "Gregory", "Christine", "Alexander", "Debra",
        "Patrick", "Rachel", "Frank", "Carolyn", "Dennis", "Janet", "Jerry", "Catherine"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
        "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
        "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
        "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
        "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
        "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers"
    ]
    
    first = first_names[index % len(first_names)]
    last = last_names[(index * 7) % len(last_names)]  # Use prime multiplier for more variation
    return f"{first} {last}"

# Resume generation prompt
resume_prompt = PromptTemplate(
    input_variables=["department", "sub_department", "experience", "seed", "name_hint"],
    template="""Generate a detailed professional resume for a candidate with the following profile:
    
Department: {department}
Sub-Department: {sub_department}
Years of Experience: {experience}
Unique Identifier: {seed}
Name must start with letter: {name_hint}

CRITICAL REQUIREMENTS:
1. MUST use a COMPLETELY DIFFERENT name starting with the letter "{name_hint}"
2. MUST use DIFFERENT companies than previous resumes
3. MUST use DIFFERENT universities
4. Generate UNIQUE and DIVERSE content - no repetition

Create a complete resume with the following sections in JSON format:
1. Full Name (MUST start with "{name_hint}" - be creative with first and last names)
2. Professional Summary (3-4 sentences, unique achievements)
3. Skills (8-12 relevant technical and soft skills)
4. Work Experience (2-3 positions with DIFFERENT company names, job titles, dates, and 4-5 bullet points each)
5. Education (degree, DIFFERENT university name, graduation year)
6. Certifications (2-3 relevant certifications)

Return ONLY a valid JSON object with this structure:
{{
    "name": "Full Name starting with {name_hint}",
    "summary": "Professional summary text",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Start Date - End Date",
            "responsibilities": ["resp1", "resp2", ...]
        }}
    ],
    "education": {{
        "degree": "Degree Name",
        "university": "University Name",
        "year": "Year"
    }},
    "certifications": ["cert1", "cert2", ...]
}}

Make it realistic and professional for the specified department and experience level."""
)

def generate_pdf(resume_data):
    """Generate a professional PDF resume"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2C3E50',
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#5D6D7E',
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#34495E',
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#2C3E50',
        spaceAfter=6,
        leading=14
    )
    
    # Name
    story.append(Paragraph(resume_data['name'], title_style))
    
    # Contact Info
    contact_text = f"{resume_data['email']} | {resume_data['phone']}"
    story.append(Paragraph(contact_text, contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color='#BDC3C7', spaceAfter=12))
    
    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    story.append(Paragraph(resume_data['summary'], body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Skills
    story.append(Paragraph("SKILLS", heading_style))
    skills_text = " • ".join(resume_data['skills'])
    story.append(Paragraph(skills_text, body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Work Experience
    story.append(Paragraph("WORK EXPERIENCE", heading_style))
    for exp in resume_data['experience']:
        title_company = f"<b>{exp['title']}</b> - {exp['company']}"
        story.append(Paragraph(title_company, body_style))
        story.append(Paragraph(f"<i>{exp['duration']}</i>", body_style))
        for resp in exp['responsibilities']:
            story.append(Paragraph(f"• {resp}", body_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Education
    story.append(Paragraph("EDUCATION", heading_style))
    edu_text = f"<b>{resume_data['education']['degree']}</b><br/>{resume_data['education']['university']}<br/>{resume_data['education']['year']}"
    story.append(Paragraph(edu_text, body_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Certifications
    if resume_data['certifications']:
        story.append(Paragraph("CERTIFICATIONS", heading_style))
        for cert in resume_data['certifications']:
            story.append(Paragraph(f"• {cert}", body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("🎯 Professional Resume Generator")
st.markdown("Generate multiple professional resumes using AI")

# Sidebar for input
with st.sidebar:
    st.header("Resume Configuration")
    
    # API Key input
    api_key = st.text_input("Google API Key", type="password", help="Enter your Gemini API key")
    
    st.info("💡 **Free Tier Limits**: Generate 2-5 resumes at a time to avoid rate limits")
    
    department = st.text_input("Department", placeholder="e.g., Information Technology")
    sub_department = st.text_input("Sub-Department", placeholder="e.g., Software Development")
    experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=3)
    quantity = st.number_input("Number of Resumes", min_value=1, max_value=20, value=3, 
                                help="Recommended: 2-5 resumes at a time for free tier")
    
    generate_button = st.button("🚀 Generate Resumes", type="primary", use_container_width=True)
    
    if st.button("Clear All", use_container_width=True):
        st.session_state.generated_resumes = []
        st.rerun()

# Main content area
if generate_button:
    if not api_key:
        st.error("Please enter your Google API Key in the sidebar")
    elif not department or not sub_department:
        st.error("Please fill in Department and Sub-Department fields")
    else:
        try:
            # Initialize LangChain with Gemini
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=api_key,
                temperature=1.0
            )
            
            chain = resume_prompt | llm
            
            st.session_state.generated_resumes = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # List of name starting letters for variety
            name_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'V', 'W', 'Z']
            
            for i in range(quantity):
                status_text.text(f"Generating resume {i+1} of {quantity}... (This may take a moment)")
                
                # Add delay between requests to avoid rate limiting
                if i > 0:
                    time.sleep(4)  # Increased to 4 seconds for better rate limiting
                
                # Retry logic for rate limiting
                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        # Add variety to prompt
                        experience_variation = experience + random.randint(-1, 2)
                        if experience_variation < 0:
                            experience_variation = 0
                        
                        # Generate unique seed and name hint for each resume
                        unique_seed = f"RESUME-{i}-{random.randint(10000, 99999)}-{int(time.time() * 1000)}"
                        name_hint = name_letters[i % len(name_letters)]
                        
                        status_text.text(f"Generating resume {i+1} of {quantity}... Calling API...")
                        
                        # Generate resume content
                        response = chain.invoke({
                            "department": department,
                            "sub_department": sub_department,
                            "experience": experience_variation,
                            "seed": unique_seed,
                            "name_hint": name_hint
                        })
                        
                        status_text.text(f"Generating resume {i+1} of {quantity}... Parsing response...")
                        
                        # Parse JSON response
                        resume_text = response.content
                        
                        # Debug: Show first 200 chars of response
                        st.sidebar.text(f"Response preview: {resume_text[:200]}...")
                        
                        # Extract JSON from markdown code blocks if present
                        if "```json" in resume_text:
                            resume_text = resume_text.split("```json")[1].split("```")[0]
                        elif "```" in resume_text:
                            resume_text = resume_text.split("```")[1].split("```")[0]
                        
                        resume_data = json.loads(resume_text.strip())
                        
                        # Force unique name by overwriting with generated name
                        unique_name = generate_unique_name(i, department)
                        resume_data['name'] = unique_name
                        
                        # Add fake contact info
                        resume_data['email'] = generate_fake_email(resume_data['name'])
                        resume_data['phone'] = generate_fake_phone()
                        
                        st.session_state.generated_resumes.append(resume_data)
                        status_text.text(f"✅ Resume {i+1} completed!")
                        break  # Success, exit retry loop
                        
                    except json.JSONDecodeError as je:
                        st.error(f"JSON Parse Error on resume {i+1}: {str(je)}")
                        st.code(resume_text[:500] if 'resume_text' in locals() else "No response text")
                        break
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"Error details: {error_msg}")
                        if "429" in error_msg or "quota" in error_msg.lower():
                            retry_count += 1
                            if retry_count < max_retries:
                                wait_time = 25 * retry_count  # Exponential backoff
                                status_text.text(f"Rate limit hit. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                                time.sleep(wait_time)
                            else:
                                st.error(f"Rate limit exceeded. Successfully generated {len(st.session_state.generated_resumes)} resumes. Please wait a few minutes and try again for the remaining resumes.")
                                break
                        else:
                            st.error(f"Error on resume {i+1}: {error_msg}")
                            break
                
                progress_bar.progress((i + 1) / quantity)
            
            status_text.text(f"✅ Successfully generated {len(st.session_state.generated_resumes)} resumes!")
            if len(st.session_state.generated_resumes) == quantity:
                st.success(f"Generated {quantity} professional resumes!")
            else:
                st.warning(f"Generated {len(st.session_state.generated_resumes)} out of {quantity} resumes due to rate limits.")
            
        except Exception as e:
            st.error(f"Error generating resumes: {str(e)}")
            if "429" in str(e) or "quota" in str(e).lower():
                st.info("💡 **Tip**: You've hit the API rate limit. Try:\n- Reducing the quantity\n- Waiting a few minutes\n- Using a different API key\n- Upgrading to a paid plan")

# Display generated resumes in grid
if st.session_state.generated_resumes:
    st.markdown("---")
    st.header("Generated Resumes")
    
    # Create grid layout
    cols_per_row = 2
    resumes = st.session_state.generated_resumes
    
    for i in range(0, len(resumes), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(resumes):
                resume = resumes[i + j]
                
                with col:
                    with st.container(border=True):
                        st.subheader(f"👤 {resume['name']}")
                        st.caption(f"📧 {resume['email']} | 📱 {resume['phone']}")
                        
                        with st.expander("View Details", expanded=False):
                            st.markdown("**Summary:**")
                            st.write(resume['summary'])
                            
                            st.markdown("**Skills:**")
                            st.write(", ".join(resume['skills'][:5]) + "...")
                            
                            st.markdown("**Experience:**")
                            for exp in resume['experience'][:2]:
                                st.write(f"• {exp['title']} at {exp['company']}")
                        
                        # Download button
                        pdf_buffer = generate_pdf(resume)
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_buffer,
                            file_name=f"resume_{resume['name'].replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_btn_{i+j}"
                        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d;'>Built with Streamlit, LangChain & Gemini 2.5 Flash</div>",
    unsafe_allow_html=True
)
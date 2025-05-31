"""
Sample data and examples for testing the resume analysis MCP server
"""

SAMPLE_RESUME_TEXT = """
John Doe
Software Engineer
john.doe@example.com
(555) 123-4567
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe

PROFESSIONAL SUMMARY
Experienced full-stack software engineer with 5+ years of experience developing scalable web applications. 
Proficient in Python, JavaScript, React, and cloud technologies. Strong background in machine learning 
and data analysis. Passionate about clean code and agile development practices.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, TypeScript, Java, C++
• Web Technologies: React, Angular, Node.js, Express, Django, Flask
• Databases: PostgreSQL, MySQL, MongoDB, Redis
• Cloud Platforms: AWS, Google Cloud Platform, Azure
• DevOps: Docker, Kubernetes, Jenkins, Git, CI/CD
• Machine Learning: TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy
• Other: RESTful APIs, GraphQL, Microservices, Agile/Scrum

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Inc. | January 2021 - Present
• Led development of microservices architecture serving 1M+ daily active users
• Implemented machine learning models for recommendation systems, improving user engagement by 25%
• Mentored junior developers and conducted code reviews
• Designed and built RESTful APIs using Python/Django and Node.js
• Optimized database queries resulting in 40% improvement in application performance

Software Engineer | StartupXYZ | June 2019 - December 2020
• Developed responsive web applications using React and Redux
• Built backend services with Python/Flask and PostgreSQL
• Implemented automated testing and CI/CD pipelines
• Collaborated with product team to define technical requirements
• Participated in agile development process and sprint planning

Junior Developer | DevCompany | September 2018 - May 2019
• Developed web applications using JavaScript, HTML, and CSS
• Assisted in database design and optimization
• Participated in code reviews and pair programming sessions
• Fixed bugs and implemented new features based on user feedback

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2018
• GPA: 3.8/4.0
• Relevant Coursework: Data Structures, Algorithms, Database Systems, Machine Learning
• Senior Project: Built a machine learning-powered chatbot for customer service

PROJECTS
E-commerce Platform (2020)
• Built full-stack e-commerce application using React, Node.js, and PostgreSQL
• Implemented payment processing with Stripe API
• Deployed on AWS with auto-scaling capabilities
• GitHub: github.com/johndoe/ecommerce-platform

Data Analytics Dashboard (2019)
• Created interactive dashboard for business intelligence using Python and D3.js
• Processed large datasets with Pandas and NumPy
• Implemented real-time data visualization with WebSocket connections

CERTIFICATIONS
• AWS Certified Solutions Architect - Associate (2021)
• Google Cloud Professional Data Engineer (2020)
• Certified Scrum Master (CSM) (2019)

ACHIEVEMENTS
• Recipient of "Employee of the Year" award at TechCorp Inc. (2022)
• Led team that won company hackathon with AI-powered productivity tool (2021)
• Published article on machine learning best practices in Tech Medium (2020)
"""

SAMPLE_JOB_REQUIREMENTS = {
    "title": "Senior Full-Stack Developer",
    "description": """
    We are seeking a Senior Full-Stack Developer to join our growing engineering team. 
    The ideal candidate will have strong experience in modern web technologies and cloud platforms.
    
    Key Responsibilities:
    • Design and develop scalable web applications
    • Work with cross-functional teams to deliver high-quality software
    • Mentor junior developers and participate in code reviews
    • Implement best practices for testing and deployment
    • Contribute to technical architecture decisions
    
    Requirements:
    • 3+ years of experience in full-stack development
    • Proficiency in React, Node.js, and Python
    • Experience with cloud platforms (AWS or Google Cloud)
    • Knowledge of database design and optimization
    • Strong understanding of software development best practices
    • Experience with agile development methodologies
    
    Preferred Qualifications:
    • Experience with machine learning or data science
    • Knowledge of DevOps practices and CI/CD
    • Contributions to open source projects
    • Strong communication and leadership skills
    """,
    "required_skills": [
        "React", "Node.js", "Python", "JavaScript", "AWS", "PostgreSQL", 
        "Git", "RESTful APIs", "Agile"
    ],
    "preferred_skills": [
        "Machine Learning", "Docker", "Kubernetes", "TensorFlow", 
        "Django", "Redis", "GraphQL"
    ],
    "required_experience_years": 3,
    "required_education": "bachelor",
    "location": "San Francisco, CA",
    "salary_range": "$120,000 - $180,000"
}

SAMPLE_RESUME_2_TEXT = """
Sarah Wilson
Data Scientist
sarah.wilson@email.com
(555) 987-6543
LinkedIn: linkedin.com/in/sarahwilson

SUMMARY
Data scientist with 4 years of experience in machine learning, statistical analysis, and big data processing. 
Expertise in Python, R, and SQL with a strong background in developing predictive models and data pipelines.

SKILLS
• Programming: Python, R, SQL, Java
• Machine Learning: Scikit-learn, TensorFlow, Keras, XGBoost
• Data Processing: Pandas, NumPy, Spark, Hadoop
• Visualization: Matplotlib, Seaborn, Tableau, Power BI
• Databases: PostgreSQL, MySQL, MongoDB, Cassandra
• Cloud: AWS, Google Cloud, Azure

EXPERIENCE
Data Scientist | DataCorp | 2020 - Present
• Developed predictive models for customer churn, improving retention by 15%
• Built automated data pipelines processing 100GB+ daily
• Created interactive dashboards for business stakeholders
• Led A/B testing initiatives for product features

Junior Data Analyst | Analytics Inc | 2019 - 2020
• Performed statistical analysis on customer behavior data
• Created reports and visualizations for executive team
• Assisted in data cleaning and preprocessing tasks

EDUCATION
Master of Science in Data Science | Data University | 2019
Bachelor of Science in Statistics | State University | 2017
"""

SAMPLE_RESUME_3_TEXT = """
Mike Chen
Frontend Developer
mike.chen@dev.com
(555) 456-7890

OBJECTIVE
Frontend developer with 2 years of experience building responsive web applications. 
Passionate about user experience and modern JavaScript frameworks.

TECHNICAL SKILLS
JavaScript, TypeScript, React, Vue.js, HTML5, CSS3, SASS, Webpack

WORK EXPERIENCE
Frontend Developer | WebStudio | 2022 - Present
• Built responsive websites using React and Vue.js
• Collaborated with designers to implement pixel-perfect UIs
• Optimized web performance achieving 95+ Lighthouse scores

Intern Developer | TechStart | 2021 - 2022
• Assisted in frontend development using vanilla JavaScript
• Created landing pages and marketing websites
• Learned React and modern development practices

EDUCATION
Bachelor of Arts in Computer Science | Tech College | 2021
"""

# Sample analysis results for testing
SAMPLE_ANALYSIS_RESULTS = [
    {
        "candidate_name": "John Doe",
        "overall_score": 0.92,
        "job_match_percentage": 88.5,
        "experience_years": 5.5,
        "strengths": ["Strong technical skills", "Leadership experience", "ML expertise"],
        "weaknesses": ["Could improve mobile development skills"],
        "recommendation": "Excellent candidate - highly recommended for senior roles"
    },
    {
        "candidate_name": "Sarah Wilson",
        "overall_score": 0.78,
        "job_match_percentage": 72.0,
        "experience_years": 4.0,
        "strengths": ["Data science expertise", "Statistical knowledge", "Cloud experience"],
        "weaknesses": ["Limited web development experience", "No leadership experience"],
        "recommendation": "Good candidate for data-focused roles, may need mentoring for full-stack work"
    },
    {
        "candidate_name": "Mike Chen",
        "overall_score": 0.65,
        "job_match_percentage": 55.5,
        "experience_years": 2.0,
        "strengths": ["Modern frontend skills", "Good educational background"],
        "weaknesses": ["Limited experience", "No backend skills", "No cloud experience"],
        "recommendation": "Junior candidate with potential, needs significant development"
    }
]

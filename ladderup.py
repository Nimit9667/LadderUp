import streamlit as st
import csv
import os
import pandas as pd
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
    </style>
    """,
    unsafe_allow_html=True
)

def set_background_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    base64_img = base64.b64encode(data).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{base64_img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .block-container,
    [data-testid="stAppViewContainer"],
    .main,[data-testid="stHeader"]{{
            background-color:#fff !important;
        }}
    .block-container,
    [data-testid="stAppViewContainer"],
    .main,
    [data-testid="stToolbar"]
    {{
        background-color: rgba(255,255,255,0) !important;
        box-shadow: 0 2px 24px rgba(0,0,0,0.08) !important;
    }}
    [data-testid="stSidebarContent"] {{
        background-color: rgba(255,255,255,0) !important;
        box-shadow: none !important;
    }}
    /* Generic chat bubble */
    [data-testid="stChatMessageContent"] {{
        max-width: 70%;
        padding: 8px 12px;
        border-radius: 12px;
        margin: 5px 0;
        font-size: 1rem;
    }}

        /* Assistant messages - left */
   /* Assistant messages - left */
    div[data-testid="stChatMessage"].st-chat-message.assistant div[data-testid="stChatMessageContent"] {{
        background-color: #f1f0f0 !important; /* light grey */
        color: black !important;
        margin-right: auto !important;
        text-align: left !important;
        border-radius: 12px 12px 12px 0;
    }}

    /* User messages - right */
    div[data-testid="stChatMessage"].st-chat-message.user div[data-testid="stChatMessageContent"] {{
        background-color: #dcf8c6 !important; /* WhatsApp green */
        color: black !important;
        margin-left: auto !important;
        text-align: right !important;
        border-radius: 12px 12px 0 12px;
    }}

    .st-emotion-cache-1avcm0n,
    .st-emotion-cache-13ejsyy {{
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"] {{
       background: #fff !important;
       color: #222 !important;
       border-radius: 10px !important;
       box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    [data-testid="stChatInput"] input {{
       background: #fff !important;
       color: #222 !important;
       border: none !important;
    }}
    [data-testid="stChatInput"] button {{
       background: #fff !important;
       color: #222 !important;
       border-radius: 50% !important;
       border: 1px solid #eee !important;
    }}
    footer, [data-testid="stChatInput"] {{
        background: #fff !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"] input {{
        background: #fff !important;
        color: #222 !important;
        border-radius: 12px !important;
        border: 1px solid #eaeaea !important;
    }}
    [data-testid="stChatInput"] button {{
        background: #fff !important;
        color: #222 !important;
        border-radius: 50% !important;
        border: 1px solid #eaeaea !important;
    
    
    }}
    [data-testid="chat-history"], .st-emotion-cache-1v0mbdj {{
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
    }}
    .st-emotion-cache-abc123 {{ margin-left: auto !important; margin-right: 0 !important; text-align: right !important; }}
    .st-emotion-cache-def456 {{ margin-left: 0 !important; margin-right: auto !important; text-align: left !important; }}

    .stMainBlockContainer{{background-color: #fff !important; padding: 0rem 1rem 2rem 1rem; margin-top: 6.5rem;}}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Call background function at the top
set_background_local("ladderup background.png")  # Ensure your filename is correct

# Center and enlarge logo
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = get_base64_image("ladderup.png")  # Ensure your filename is correct
if logo_base64:
    st.markdown(
        f'''
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 650px; margin-bottom: 0.2em;height: 300px;
    object-fit: cover;" />
        </div>
        ''',
        unsafe_allow_html=True
    )

# Save login data
def save_user_data_to_excel(user_data, filename='user_data.xlsx'):
    try:
        df = pd.read_excel(filename)
        df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([user_data])
    df.to_excel(filename, index=False)

# Initialize session state ONLY ONCE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ---------------- MAIN PAGE FUNCTION ---------------- #
def show_main_page():   
  

    DATA_FILE = "user_data.csv"

    def save_data(data_dict, recommended_career):
        headers = [
            "user_name", "grade", "curiosity", "free_time_activities",
            "dream_saturday", "strengths", "praise", "work_preference",
            "preference_pace", "favorite_subject", "easiest_subject",
            "project_type", "values", "work_environment", "recommended_career"
        ]
        new_data = {header: data_dict.get(header) for header in headers}
        new_data["recommended_career"] = recommended_career
        df_new = pd.DataFrame([new_data])
        if not os.path.isfile(DATA_FILE):
            df_new.to_csv(DATA_FILE, index=False, header=True, encoding='utf-8')
        else:
            df_new.to_csv(DATA_FILE, index=False, header=False, mode='a', encoding='utf-8')

    # ---- Career database ----
    career_database = {
         
        # STEM (Science, Technology, Engineering, and Mathematics)
        "Software Engineer": "Focuses on logical thinking, problem-solving, and building things with technology. Enjoys coding, creating new apps, and working on analytical challenges. Values creativity, innovation, and seeing a project come to life.",
        "Mechanical Engineer": "A hands-on problem-solver who enjoys fixing things, building, and understanding how machines work. Strengths include attention to small details and applying physics and math to real-world objects. Values stable work and tangible results.",
        "Data Scientist": "Loves finding patterns in large datasets. Enjoys statistics, machine learning, and telling stories with data. Values analytical thinking and making data-driven decisions.",
        "Civil Engineer": "Focuses on designing and overseeing large-scale public works projects like roads, bridges, and dams. Enjoys applying physics and mathematics to create infrastructure that benefits society. Values long-term impact and public safety.",
        "Biomedical Engineer": "Applies engineering principles to solve problems in biology and medicine. Enjoys designing medical devices, diagnostic equipment, and artificial organs. Values innovation and improving healthcare technology.",
        "Aerospace Engineer": "Designs aircraft, spacecraft, satellites, and missiles. Fascinated by flight and space exploration. Enjoys complex physics, aerodynamics, and pushing the boundaries of technology.",
        "Chemical Engineer": "Transforms chemical and biological materials into valuable products. Enjoys chemistry, process design, and large-scale production. Works in industries like manufacturing, pharmaceuticals, and energy.",
        "Electrical Engineer": "Designs and develops electrical systems and electronic devices. Enjoys circuits, power generation, and robotics. Values precision and creating technology that powers the world.",
        "Environmental Engineer": "Uses science and engineering to improve the environment. Enjoys solving problems related to pollution, waste disposal, and public health. Values sustainability and protecting natural resources.",
        "Web Developer": "Builds and maintains websites and web applications. Enjoys coding in languages like HTML, CSS, and JavaScript. Values creating user-friendly and functional digital experiences.",
        "Database Administrator": "Manages and maintains an organization's data. Enjoys organizing information, ensuring data security, and optimizing database performance. Values structure and reliability.",
        "Network Architect": "Designs and builds communication networks for organizations. Enjoys planning and implementing LANs, WANs, and intranets. Values connectivity and security.",
        "Information Security Analyst": "Protects an organization's computer networks and systems. Enjoys identifying vulnerabilities, monitoring for cyber threats, and implementing security measures. Values protecting information.",
        "AI/Machine Learning Engineer": "Develops intelligent systems that can learn from data. Enjoys algorithms, neural networks, and building predictive models. Values innovation and creating cutting-edge technology.",
        "Robotics Engineer": "Designs, builds, and programs robots. Enjoys mechanics, electronics, and computer science. Values creating automated systems that can perform tasks.",
        "Statistician": "An expert in collecting, analyzing, and interpreting data. Enjoys working with statistical models and software to solve problems in various fields. Values objectivity and data-driven insights.",
        "Astrophysicist": "Studies the physical nature of stars and other celestial bodies. Enjoys physics, mathematics, and exploring the mysteries of the universe. Values scientific discovery and cosmic-scale thinking.",
        "Geologist": "Studies the Earth's physical structure and substance. Enjoys fieldwork, analyzing rock formations, and understanding geological processes. Values scientific inquiry and exploring the natural world.",
        "Marine Biologist": "Studies marine organisms and their interactions with the environment. Enjoys fieldwork, conducting research, and working to conserve ocean life. Values scientific discovery and protecting the marine ecosystem.",
        "Microbiologist": "Studies microorganisms such as bacteria, viruses, and fungi. Enjoys laboratory work and research. Values understanding the microscopic world and its impact on health and the environment.",
        "Physicist": "Explores the fundamental principles of energy and matter. Enjoys theoretical modeling and experimental research. Values uncovering the basic laws of the universe.",

        # Creative Arts and Design
        "Creative Writer": "Driven by creativity, storytelling, and the arts. Enjoys reading, writing stories, and has strong attention to detail. Values expressing ideas and creating compelling narratives.",
        "Game Developer": "A blend of creativity and technical skill. Enjoys playing video games, designing new worlds, and problem-solving. Uses technology to build interactive and entertaining experiences. Values innovation and creative expression.",
        "Graphic Designer": "Has a strong eye for aesthetics and visual communication. Enjoys using design software to create logos, websites, and marketing materials. Values creativity and conveying messages through art.",
        "Architect": "Combines artistic vision with technical precision. Enjoys designing buildings, creating blueprints, and seeing their creations come to life. Values both form and function in the built environment.",
        "Interior Designer": "Has a flair for creating functional and beautiful indoor spaces. Enjoys selecting color schemes, furniture, and decor to match a client's vision. Values aesthetics, spatial awareness, and creativity.",
        "Fashion Designer": "Creates clothing and accessories. Enjoys sketching designs, selecting fabrics, and staying ahead of trends. Values creativity, style, and expressing ideas through fashion.",
        "Photographer": "Captures moments and tells stories through images. Enjoys working with cameras, lighting, and composition to create compelling photos. Values creativity and visual storytelling.",
        "Animator": "Brings characters and stories to life through motion. Enjoys drawing, using animation software, and creating visual effects. Values creativity, patience, and storytelling.",
        "UX/UI Designer": "Focuses on making technology easy and enjoyable to use. Enjoys user research, creating wireframes, and designing intuitive interfaces. Values empathy for the user and seamless design.",
        "Art Director": "Manages the visual style and images for creative projects. Enjoys leading creative teams and ensuring a cohesive artistic vision. Values leadership and aesthetic excellence.",
        "Illustrator": "Creates drawings and images for books, magazines, and digital media. Enjoys bringing ideas to life through visual art. Values artistic skill and storytelling.",
        "Musician": "Creates and performs music. Enjoys playing an instrument, singing, or composing. Values emotional expression and connecting with an audience.",
        "Film Director": "Oversees the creative aspects of a film. Enjoys storytelling, working with actors, and guiding a production team. Values artistic vision and leadership.",
        "Video Game Designer": "Designs the core concepts and mechanics of video games. Enjoys brainstorming creative ideas and defining the player experience. Values innovation and interactive entertainment.",
        "Industrial Designer": "Designs consumer products, from cars to electronics. Enjoys combining form and function to create user-friendly and aesthetically pleasing items. Values innovation and problem-solving.",
        "Landscape Architect": "Designs outdoor spaces such as parks, gardens, and campuses. Enjoys combining artistic vision with environmental science. Values creating sustainable and aesthetically pleasing environments.",
        "Sound Engineer": "Works with the technical aspects of sound during recording, mixing, and reproduction. Enjoys using audio equipment to create a specific sonic experience for music, film, or live events. Values technical skill and artistic collaboration.",
        "Art Curator": "Selects and interprets works of art for an exhibition. Enjoys art history, research, and creating compelling narratives through art. Values cultural preservation and education.",
        "Dancer": "Expresses ideas and emotions through bodily movement. Enjoys physical discipline, choreography, and performance. Values artistic expression and athleticism.",
        "Actor": "Portrays characters in performances on stage, in films, or on television. Enjoys embodying different personalities and telling stories. Values empathy and collaboration.",

        # Business and Finance
        "Marketing Manager": "Strategic thinker who understands consumer behavior. Enjoys analyzing market trends, creating campaigns, and using data to drive business growth. Values innovation and achieving measurable results.",
        "Financial Analyst": "Detail-oriented with a strong aptitude for numbers. Enjoys analyzing financial statements, creating forecasts, and advising on investment decisions. Values accuracy and helping others achieve financial goals.",
        "Human Resources Manager": "A people-person who enjoys building a positive work culture. Focuses on recruiting, employee relations, and organizational development. Values fairness, communication, and helping employees thrive.",
        "Accountant": "Meticulous with numbers and financial records. Enjoys preparing financial statements, managing budgets, and ensuring tax compliance. Values accuracy, integrity, and financial order.",
        "Management Consultant": "Solves business problems for clients. Enjoys analyzing organizations, developing strategies, and advising senior leaders. Values strategic thinking and driving change.",
        "Project Manager": "Organizes and leads projects to successful completion. Enjoys planning, managing resources, and communicating with stakeholders. Values leadership and achieving goals on time and within budget.",
        "Supply Chain Manager": "Oversees the entire lifecycle of a product, from procurement to delivery. Enjoys logistics, planning, and optimizing efficiency. Values organization and smooth operations.",
        "Investment Banker": "Advises companies on financial matters, such as mergers and acquisitions. Enjoys high-stakes negotiations and complex financial modeling. Values ambition and financial expertise.",
        "Real Estate Agent": "Assists clients in buying, selling, and renting properties. Enjoys networking, showing homes, and negotiating deals. Values entrepreneurship and helping people find their perfect home.",
        "Market Research Analyst": "Studies market conditions to examine potential sales of a product or service. Enjoys gathering and analyzing data on consumers and competitors. Values providing insights to guide business decisions.",
        "Sales Manager": "Leads a sales team to meet revenue goals. Enjoys coaching, setting targets, and building customer relationships. Values leadership and driving business growth.",
        "Public Relations Specialist": "Manages the public image of a person or organization. Enjoys writing press releases, communicating with the media, and building a positive brand reputation. Values strategic communication.",
        "Entrepreneur": "Starts and runs their own business. Enjoys innovation, taking risks, and building something from the ground up. Values autonomy and creating their own success.",
        "Business Analyst": "Identifies business needs and determines solutions to business problems. Enjoys analyzing processes, data, and systems. Values improving efficiency and effectiveness.",
        "Operations Manager": "Ensures that a business runs smoothly and efficiently. Enjoys overseeing production, inventory, and quality control. Values organization and operational excellence.",
        "Insurance Underwriter": "Evaluates insurance applications to determine risks and premiums. Enjoys analyzing data and making decisions based on risk assessment. Values careful judgment and financial prudence.",
        "Logistics Manager": "Coordinates the storage and transportation of goods. Enjoys planning routes, managing warehouses, and ensuring timely delivery. Values efficiency and organization.",
        "Brand Manager": "Develops and maintains a company's brand identity. Enjoys market research, advertising, and creating a consistent brand message. Values creativity and strategic thinking.",

        # Healthcare
        "Medical Researcher": "Curious about science, medicine, and solving complex puzzles. Enjoys lab work, research, and analytical thinking. Motivated by making a positive impact on health and well-being. Values precision and a stable, secure job environment.",
        "Nurse": "Compassionate and skilled in patient care. Enjoys working in a medical setting, providing direct support to patients, and collaborating with doctors. Values empathy and promoting health and wellness.",
        "Doctor (Physician)": "Diagnoses and treats illnesses and injuries. Enjoys applying medical knowledge to solve patient problems. Values helping people and lifelong learning.",
        "Surgeon": "Performs operations to treat injuries and diseases. Enjoys hands-on, high-stakes work that requires precision and calmness under pressure. Values saving lives and improving patient outcomes.",
        "Dentist": "Diagnoses and treats problems with teeth and gums. Enjoys working with their hands and improving patients' oral health. Values precision and patient care.",
        "Pharmacist": "Detail-oriented and knowledgeable about medications. Enjoys dispensing prescriptions, advising patients on drug interactions, and ensuring medication safety. Values accuracy and patient health.",
        "Physical Therapist": "Helps patients recover from injuries and improve their mobility. Enjoys creating rehabilitation plans, guiding exercises, and seeing patients regain their strength. Values helping others and understanding human anatomy.",
        "Occupational Therapist": "Helps people with injuries, illnesses, or disabilities participate in everyday activities. Enjoys developing personalized treatment plans and finding adaptive solutions. Values helping people achieve independence.",
        "Veterinarian": "Passionate about animal welfare. Enjoys diagnosing and treating animal illnesses, performing surgery, and advising pet owners. Values compassion for animals and scientific knowledge.",
        "Psychologist": "Interested in the human mind and behavior. Enjoys listening to people, conducting therapy sessions, and helping individuals overcome personal challenges. Values empathy and confidentiality.",
        "Psychiatrist": "A medical doctor who specializes in mental health. Enjoys diagnosing and treating mental illnesses, often by prescribing medication. Values a deep understanding of both psychology and biology.",
        "Radiologist": "Interprets medical images like X-rays and MRIs to diagnose diseases. Enjoys detailed analysis and using technology to see inside the human body. Values precision and diagnostic skill.",
        "Anesthesiologist": "Administers anesthesia to patients before, during, and after surgery. Enjoys ensuring patient comfort and safety during medical procedures. Values vigilance and critical-care skills.",
        "Paramedic": "Provides emergency medical care in high-pressure situations. Enjoys responding to 911 calls, assessing patients, and administering life-saving treatments. Values quick thinking and remaining calm under pressure.",
        "Dietitian": "An expert in food and nutrition. Enjoys creating meal plans, educating clients about healthy eating, and helping people achieve their health goals. Values science-based advice and promoting wellness.",
        "Speech-Language Pathologist": "Treats communication and swallowing disorders. Enjoys working with people of all ages to improve their ability to speak and understand. Values helping others connect and communicate.",
        "Chiropractor": "Focuses on diagnosing and treating neuromuscular disorders, with an emphasis on treatment through manual adjustment of the spine. Enjoys hands-on work to relieve pain and improve body function.",
        "Optometrist": "Diagnoses and treats visual problems. Enjoys examining eyes, prescribing glasses or contact lenses, and detecting eye diseases. Values helping people see clearly.",
        "Medical Laboratory Technician": "Performs tests on samples from patients to help diagnose and treat diseases. Enjoys working in a lab and providing critical data for medical teams. Values precision and scientific process.",
        "Genetic Counselor": "Advises individuals and families about genetic conditions. Enjoys explaining complex genetic information and providing emotional support. Values helping people make informed healthcare decisions.",

        # Social and Community Services
        "Social Worker": "Motivated by helping people and making a positive community impact. Strengths include empathy, communication, and being a good listener. Enjoys volunteering and working directly with others to solve real-world problems.",
        "Teacher": "Dedicated to educating and inspiring others. Enjoys creating lesson plans, working with students, and fostering a love of learning. Values patience, communication, and making a difference in the lives of others.",
        "Librarian": "Loves books and organizing information. Enjoys helping people find resources, curating collections, and creating a welcoming environment for learning. Values knowledge and community service.",
        "School Counselor": "Helps students with academic, career, and personal development. Enjoys guiding young people and providing a supportive resource. Values empowering students to succeed.",
        "Urban Planner": "Develops land use plans and programs that help create communities, accommodate population growth, and revitalize physical facilities. Enjoys shaping how cities and towns grow and develop.",
        "Nonprofit Program Manager": "Manages programs that advance a nonprofit's mission. Enjoys working for a cause, organizing projects, and measuring social impact. Values making a positive difference in the world.",
        "Community Organizer": "Brings people together to take action on common concerns. Enjoys empowering communities to create change from the ground up. Values social justice and collective action.",
        "Firefighter": "Responds to fires and other emergencies. Enjoys physical challenges, teamwork, and protecting lives and property. Values bravery and community service.",
        "Police Officer": "Maintains law and order, protects members of the public, and their property. Enjoys serving the community and working in a structured environment. Values justice and public safety.",
        "Recreation Worker": "Designs and leads recreational and leisure activities for groups in agencies or recreation facilities. Enjoys being active and helping others have fun and stay healthy.",

        # Law and Government
        "Lawyer": "A critical thinker with strong argumentation skills. Enjoys legal research, building cases, and advocating for clients. Values justice, fairness, and upholding the law.",
        "Paralegal": "Assists lawyers with legal research and preparing documents. Enjoys organizing information and supporting legal cases. Values attention to detail and the legal process.",
        "Judge": "Presides over legal proceedings in a court of law. Enjoys interpreting the law and ensuring fair trials. Values impartiality and justice.",
        "Foreign Service Officer": "Represents the U.S. abroad as a diplomat. Enjoys international relations, cultural exchange, and public service. Values promoting peace and American interests.",
        "Intelligence Analyst": "Gathers and analyzes information to assess threats to national security. Enjoys research, critical thinking, and solving complex puzzles. Values protecting the country.",
        "Legislative Aide": "Assists a legislator with research, constituent services, and administrative tasks. Enjoys politics and the policymaking process. Values public service and influencing policy.",
        "Lobbyist": "Advocates for the interests of a group or organization to influence policy. Enjoys networking, persuasion, and understanding the legislative process. Values shaping public policy.",

        # Skilled Trades and Hands-On Work
        "Event Planner": "Excels at organization, leadership, and planning. Enjoys managing projects, working with numbers and people. Thrives in dynamic environments and is motivated by bringing an idea to reality, from parties to large corporate functions.",
        "Chef": "Creative and passionate about food. Enjoys experimenting with flavors, creating new recipes, and managing a fast-paced kitchen. Values quality ingredients and providing a memorable dining experience.",
        "Electrician": "A hands-on professional who understands electrical systems. Enjoys installing and maintaining wiring, and troubleshooting technical issues. Values safety and precision in their work.",
        "Plumber": "A practical problem-solver who works with piping and fixtures. Enjoys hands-on work and ensuring that water and drainage systems function correctly. Values providing essential services to the community.",
        "Pilot": "Loves flying and has a strong sense of responsibility. Enjoys navigating aircraft, understanding weather patterns, and ensuring passenger safety. Values precision, calmness under pressure, and travel.",
        "Construction Manager": "A leader who oversees building projects from start to finish. Enjoys coordinating teams, managing schedules, and ensuring that construction meets quality standards. Values leadership and tangible accomplishments.",
        "Carpenter": "Builds and repairs structures made of wood. Enjoys hands-on work, craftsmanship, and creating things with their hands. Values precision and quality construction.",
        "Welder": "Joins metal parts together using heat. Enjoys working with tools and creating strong, durable structures. Values technical skill and precision.",
        "Automotive Mechanic": "Repairs and maintains cars and trucks. Enjoys diagnosing and solving mechanical problems. Values keeping vehicles safe and running smoothly.",
        "HVAC Technician": "Installs and services heating, ventilation, and air conditioning systems. Enjoys working with mechanical and electrical systems to keep people comfortable. Values technical skill and problem-solving.",
        "Farmer/Agricultural Manager": "Manages farms, ranches, and other agricultural establishments. Enjoys working outdoors, cultivating crops or raising animals. Values providing food for the community.",
        "Surveyor": "Makes precise measurements to determine property boundaries. Enjoys working outdoors and using technology like GPS and GIS. Values accuracy and mapping the world.",
        "Machinist": "Sets up and operates machine tools to produce precision parts. Enjoys working with their hands and creating precise metal components. Values technical skill and attention to detail.",
        "Forester": "Manages forests for conservation and economic purposes. Enjoys working outdoors and applying scientific principles to maintain healthy forest ecosystems. Values sustainability and the environment.",

        # Communication and Media
        "Journalist": "Curious and driven to uncover the truth. Enjoys interviewing sources, writing articles, and reporting on current events. Values objectivity, storytelling, and informing the public.",
        "Technical Writer": "Simplifies complex technical information for a general audience. Enjoys writing manuals, help guides, and instructional materials. Values clarity, accuracy, and helping others understand technology.",
        "Copywriter": "Writes text for the purpose of advertising or other forms of marketing. Enjoys being creative with words to persuade and inform. Values effective communication.",
        "Editor": "Reviews and revises content for publication. Enjoys improving the quality of writing and ensuring it meets standards. Values clarity, consistency, and accuracy.",
        "Social Media Manager": "Manages an organization's social media presence. Enjoys creating content, engaging with audiences, and analyzing social media trends. Values building an online community.",
        "Broadcast Journalist": "Reports news for television or radio. Enjoys being on camera or on air, and delivering news in a compelling way. Values clear communication and connecting with a broad audience.",
        "Interpreter/Translator": "Converts information from one language to another. Enjoys mastering languages and facilitating communication between people who speak different languages. Values cultural understanding.",

        # Other
        "Forensic Scientist": "Collects and analyzes physical evidence from crime scenes. Enjoys lab work, detailed analysis, and applying scientific principles to legal investigations. Values precision and contributing to justice.",
        "Conservator": "Preserves and restores artifacts and works of art. Enjoys hands-on work, detailed analysis, and using scientific techniques to protect cultural heritage. Values history, art, and meticulous craftsmanship.",
        "Archivist": "Appraises, edits, and maintains permanent records and historically valuable documents. Enjoys organizing information and preserving history for future generations. Values cultural heritage and research.",
        "Sommelier": "A wine expert who advises customers on wine pairings in a restaurant. Enjoys the sensory experience of wine tasting and sharing their knowledge with others. Values expertise and providing a great dining experience.",
        "Brewmaster": "Oversees the brewing process at a brewery. Enjoys combining science and art to create different styles of beer. Values craftsmanship and creativity in brewing.",
        "Meteorologist": "Studies the atmosphere and forecasts the weather. Enjoys analyzing data from weather stations and models to predict atmospheric conditions. Values helping people prepare for the weather.",
        "Cartographer": "Creates maps. Enjoys combining geography, technology, and design to represent spatial information visually. Values accuracy and clear communication of geographic data."
    
    }

    def get_recommendation(user_data):
        user_profile = ". ".join(filter(None, [
            user_data.get("free_time_activities"),
            user_data.get("dream_saturday"),
            user_data.get("strengths"),
            user_data.get("praise"),
            user_data.get("favorite_subject"),
            user_data.get("project_type"),
            user_data.get("values")
        ]))
        if not user_profile.strip():
            return "Not enough information to make a recommendation.", 0.0
        careers = list(career_database.keys())
        career_descriptions = list(career_database.values())
        documents = [user_profile] + career_descriptions
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        best_match_index = cosine_similarities.argmax()
        best_match_score = cosine_similarities[best_match_index]
        recommended_career = careers[best_match_index]
        if best_match_score < 0.1:
            return "An exciting new path you'll discover!", best_match_score
        return recommended_career, best_match_score

    # ---- UI rendering ----
    st.markdown(
        """
        <h1 style='text-align:center; font-size:3.5em; color:#FFA726; font-family:Montserrat, Arial, sans-serif; font-weight:700; margin-top:0; margin-bottom:0.2em;'>
            Navigate the future with<br>AI-guided career consultancy
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='text-align:center;'>
            <span style='color:#1976d2; font-weight:700; font-size:1.3em;'>
                Map strengths to opportunities with machine-learning recommendations and expert consultancy.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "step" not in st.session_state:
        st.session_state.step = "start"
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}

    if st.session_state.step == "start":
        user_name = st.session_state.get("user_name", "there")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Great to meet you, {user_name}! To get started, what grade are you in?"
    })
        st.session_state.step = "get_grade"


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    questions = {
        "get_name": ("user_name", "Great to meet you, {}! To get started, what grade are you in?", "get_grade"),
        "get_grade": ("grade", "What are you most curious about right now?", "get_curiosity"),
        "get_curiosity": ("curiosity", "What activities do you do for fun? (e.g., reading, video games, sports)", "get_activities"),
        "get_activities": ("free_time_activities", "Describe your ideal Saturday. What would you do?", "get_saturday"),
        "get_saturday": ("dream_saturday", "What are your greatest strengths?", "get_strengths"),
        "get_strengths": ("strengths", "What's a skill a teacher or family member has praised you for?", "get_praise"),
        "get_praise": ("praise", "Do you prefer working alone or in a team?", "get_work_pref"),
        "get_work_pref": ("work_preference", "Are you a big-picture thinker or detail-oriented?", "get_pace"),
        "get_pace": ("preference_pace", "What's your favorite subject and why?", "get_fav_subject"),
        "get_fav_subject": ("favorite_subject", "And which subject comes easiest to you?", "get_easy_subject"),
        "get_easy_subject": ("easiest_subject", "What kind of school projects do you enjoy most?", "get_project_type"),
        "get_project_type": ("project_type", "What is most important to you in a future job? (e.g., money, helping others)", "get_values"),
        "get_values": ("values", "Finally, do you prefer working mainly indoors or outdoors?", "get_environment"),
    }

    if user_prompt := st.chat_input("Type your message here..."):
        st.chat_message("user").markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        current_step = st.session_state.step
        
        with st.chat_message("assistant"):
            response_container = st.empty()
            
            if current_step in questions:
                key, next_question_format, next_step = questions[current_step]
                st.session_state.user_data[key] = user_prompt
                response = next_question_format.format(user_prompt) if "{}" in next_question_format else next_question_format
                st.session_state.step = next_step

            elif current_step == "get_environment":
                st.session_state.user_data["work_environment"] = user_prompt
                st.session_state.step = "finished"
                
                with st.spinner("Analyzing your profile with our ML model..."):
                    recommended_career, score = get_recommendation(st.session_state.user_data)
                
                response = f"""
                Thank you for sharing that. After analyzing your profile, I have a recommendation for you.

                Based on your interests and strengths, a great potential career path to explore is **{recommended_career}**.
                (Confidence Score: {score:.2f})

                ---
                **Why this might be a good fit:** My analysis suggests your profile has a strong alignment with the core attributes of this career, considering your combined interests in `{st.session_state.user_data.get('free_time_activities', 'various topics')}` and your strengths like `{st.session_state.user_data.get('strengths', 'your unique skills')}`.

                Remember, this is a data-driven starting point. I encourage you to research this field further!

                *Your recommendation has been saved to `user_data.csv`. Refresh the page to start over.*
                """
                save_data(st.session_state.user_data, recommended_career)
            
            else:
                response = "Our chat is complete! Please refresh the page if you'd like to start a new recommendation."

            response_container.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})



    # ---------------- LOGIN LOGIC ---------------- #
if not st.session_state.logged_in:
    st.markdown(
        """
        <h1 style='text-align: center; font-family: "Montserrat", sans-serif; font-weight: 700; color: #BD664D;'>
           Your Professional Journey Awaits 
        </h1>
        """,
        unsafe_allow_html=True
    )
    name = st.text_input("Enter your name:", key="login_name")
    email = st.text_input("Enter your email:", key="login_email")
    if st.button("Submit", key="login_submit"):
        user_data = {"Name": name, "Email": email}
        save_user_data_to_excel(user_data)
        st.session_state.user_name = name
        st.session_state.logged_in = True
        st.rerun()
else:
    show_main_page()
    
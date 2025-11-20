import os

# # FIX: Prevent HuggingFace from creating symlinks on Windows
# os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

import streamlit as st
from PIL import Image
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from schema import Profile
from config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
import os 
import docling
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

icon = Image.open("D:/VRNeXGen/resume/final/logo.png")

st.set_page_config(
    page_title = "VRNeXGen",
    page_icon = icon,
    layout = "wide",
)

st.markdown(
    """
    <h1 style='font-size: 46px; display: flex; align-items: center;'>
        <span style='color:#800000;'>VR</span>NeXGen
    </h1>
    <h8>Modernize 🔺 Automate 🔺 Innovate</h8>
    """,
    unsafe_allow_html = True
)

st.markdown("""
<style>
.box {
    padding: 18px;
    border-radius: 12px;
    margin: 15px 0;
    background: #f1f5f9;
    border-left: 5px solid #2563eb;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}
.title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)



@st.dialog("Duplicate Email Found")
def show_overwrite_dialog(email, data, csv_file):
    st.write(f"An entry with email **{email}** already exists in the database.")
    st.write("What would you like to do?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Overwrite Existing"):
            df = pd.read_csv(csv_file)
            df = df[df["email_id"] != email]  # remove old
            df_new = pd.DataFrame([data])
            df = pd.concat([df, df_new], ignore_index=True)
            df.to_csv(csv_file, index = False)
            st.success(f"Your resume for {email} has been overwritten successfully!")
            st.rerun()

    with col2:
        if st.button("Cancel"):
            # df_new = pd.DataFrame([data])  
            df = pd.read_csv(csv_file)
            st.warning("The current process has been cancelled.")
            st.rerun()
                
tab1, tab2 = st.tabs(
    [
        "📃Resume Upload", 
        "📋Filter Resume", 
        #"👩🏻‍💻Manual Upload"
    ]
)

csv_file = "resume_output.csv"

with tab1:
    st.header("Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type = ["pdf", "docx"]
    )
    if uploaded_file:
        st.success("📄Resume Uploaded")

        if st.button("Convert"):
            with st.spinner("Extracting Information..."):
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                
                # loader = DoclingLoader(file_path=temp_path, export_type=ExportType.MARKDOWN)
                loader = DoclingLoader(
                    file_path=temp_path,
                 
                    export_type=ExportType.MARKDOWN
                )

                docs = loader.load()
                resume_text = docs[0].page_content
               


            with st.spinner("Generating Insights..."):
                llm = ChatGoogleGenerativeAI(
                    model = "gemini-2.5-flash-lite",
                    temperature = 0,
                    google_api_key = settings.google_api_key,
                )

                structured_llm = llm.with_structured_output(
                    schema = Profile
                )
                response = structured_llm.invoke(
                    resume_text
                )

            # st.json(response.model_dump_json(indent = 5 ))

            data = response.model_dump()

            st.markdown(f"""
            <div class="box">
                <div class="title">👤 Personal Details</div>
                <p><b>Name:</b> {data.get('fullname')}</p>
                <p><b>Email:</b> {data.get('email_id')}</p>
                <p><b>Phone:</b> {data.get('phone_number')}</p>
                <p><b>Designation:</b> {data.get('designation')}</p>
                <p><b>Current Location:</b> {data.get('current_location')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""               
            <div class="box">
                <div class="title">💻 Technical Skills</div>
                    
            <div class="box">
                <div class="title">💻 Programming Languages</div>
                    {"".join([f"<span style='background:#e0e7ff;padding:6px 12px;margin:4px;border-radius:8px;display:inline-block;'>{lang}</span>"
                    for lang in data["technical_skills"][0]["programming_languages"]])}
                </div>
                
                 """, 
                unsafe_allow_html=True)
            st.markdown(f"""     
            <div class="box">
                <div class="title">💻 Libraries or Frameworks</div>
                    {"".join([f"<span style='background:#e0e7ff;padding:6px 12px;margin:4px;border-radius:8px;display:inline-block;'>{lang}</span>"
                    for lang in data["technical_skills"][0]["libraries_or_frameworks"]])}
            </div>
                """, 
                unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="box">
                <div class="title">💻 Other Tools</div>
                    {"".join([f"<span style='background:#e0e7ff;padding:6px 12px;margin:4px;border-radius:8px;display:inline-block;'>{lang}</span>"
                    for lang in data["technical_skills"][0]["other_tools"]])}
            </div>
            
             """, 
                unsafe_allow_html=True)
            st.markdown(f"""
            <div class="box">
                <div class="title">💻 Interpersonal Skills</div>
                    {"".join([f"<span style='background:#e0e7ff;padding:6px 12px;margin:4px;border-radius:8px;display:inline-block;'>{lang}</span>"
                    for lang in data["interpersonal_skills"]])}
                
            </div>
                """, 
                unsafe_allow_html=True)
            
            
            st.markdown(f"""
            <div class="box">
                <div class="title">👩🏻‍💻 Working Details</div>
                <p><b>Year of Experience:</b> {data.get('year_of_experience')}</p>
                <p><b>Current CTC:</b> {data.get('current_ctc')}</p>
                <p><b>Current Company:</b> {data.get('current_company')}</p>
                <p><b>Expected CTC:</b> {data.get('expected_ctc')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="box">
                <div class="title">🌐 Links</div>
                <p><b>LinkedIn URL:</b> {data.get('linkedin_url')}</p>
                <p><b>GitHub URL:</b> {data.get('github_url')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="box">
                <div class="title">📄 Certifications</div>
                <p><b>Certifications:</b> {data.get('certifications')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="box">
                <div class="title">📃 Summary</div>
                <p><b>Summary:</b> {data.get('summary')}</p>
            </div>
            """, unsafe_allow_html=True)
  
            st.markdown(f"""
            <div class="box">
                <div class="title">👩‍💻 Portfolio </div>
                <p><b>Portfolio Project URL:</b> {data.get('portfolio_project_url')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            
            st.session_state["resume_data"] = data
            os.remove(temp_path)

    if "resume_data" in st.session_state:
        if st.button("Save"):
            data = st.session_state["resume_data"]
            
            tech = data.get("technical_skills", [])
            if isinstance(tech, list) and len(tech) > 0:
                tech = tech[0]  # take first dict from list
            else:
                tech = {}

            prog_langs = tech.get("programming_languages", []) or []
            frameworks = tech.get("libraries_or_frameworks", []) or []
            tools = tech.get("other_tools", []) or []

            data["skills"] = list(set(prog_langs + frameworks + tools))
                        
            df_new = pd.DataFrame([data])
            # csv_file = "resume_output.csv"
            
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)

                # Check if email exists
                if not df[df['email_id'] == data['email_id']].empty:
                    # Trigger the dialog box
                    show_overwrite_dialog(data['email_id'], data, csv_file)
                else:
                    df_new.to_csv(csv_file, mode = 'a', header = False, index = False)
                    st.success("📄Resume data successfully saved")
                    st.rerun()
            # else:
            #     df_new.to_csv(csv_file, index = False)
            #     st.success("📄Resume data successfully saved")



with tab2:
    data = pd.read_csv(csv_file)

    df = pd.DataFrame(data)

    st.title("🔍Skills Filtering ")

    # skill_details = df['skills'].unique().tolist()
    skill_data = df["skills"].apply(lambda x: eval(x) if isinstance(x, str) else x)
    skill_list = []
    for skills in skill_data:
        for skill in skills:
            skill_list.append(skill)
            
    all_skill_details = sorted(set(skill_list))

    selected_skills = st.multiselect("Select one or more skills", all_skill_details)

    if not selected_skills:
        filtered_df = df
        
    else:
        filtered_df = df[df['skills'].apply(lambda skill_set: all(skill in skill_set for skill in selected_skills))]
        # filtered_df = df[df['skills'].apply(lambda skill_set: bool(set(skill_set) & set(selected_skills)))]

    st.dataframe(filtered_df)


# with tab3:    

#     with st.form("my_form", clear_on_submit = True):
#         st.write("Resume details")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             fullname = st.text_input("Fullname:")
#             email_id = st.text_input("Email ID:")
#             designation = st.text_input("Designation:")
#             libraries_or_frameworks = st.text_area("Libraries or Frameworks:")
#             interpersonal_skills = st.text_area("Interpersonal Skills:")
#             current_ctc = st.text_input("Current CTC:")
#             expected_ctc = st.text_input("Expected CTC:")
#             github_url = st.text_input("GitHub URL:")
#             summary = st.text_area("summary:")
                
#         with col2:
            
#             phone_number = st.text_input("Phone Number:")
#             current_location = st.text_input("Current Location:")
#             programming_languages = st.text_area("Programming Languages:")
#             other_tools = st.text_area("Other Tools:")
#             year_of_experience = st.text_input("Year Of Experience:")
#             current_company = st.text_input("Current Company:")
#             linkedin_url = st.text_input("LinkedIn URL:")
#             portfolio_project_urls = st.text_input("Portfolio Project URL:")
#             certifications = st.text_area("Certifications:")

#         # Every form must have a submit button.
#         submit = st.form_submit_button("Submit")
        
#     if submit:
        
#         if not all([fullname, phone_number, email_id, programming_languages]):
#             st.error("Fill all the details")
#         else:
#             # csv_file = "resume_output.csv"

#             if os.path.exists(csv_file):
#                 df = pd.read_csv(csv_file)
#             else:
#                 df = pd.DataFrame(
#                     columns=[
#                         "fullname",
#                         "email_id", 
#                         "phone_number", 
#                         "current_location", 
#                         "designation", 
#                         "technical_skills", 
#                         "interpersonal_skills", 
#                         "year_of_experience", 
#                         "current_ctc",
#                         "current_company", 
#                         "expected_ctc", 
#                         "linkedin_url", 
#                         "github_url",
#                         "portfolio_project_urls",
#                         "summary",
#                         "certifications", 
#                         "skills"
#                     ]
#                 )

#             # Clean up and split all skills properly
#             # all_skills = []
#             # for skill_group in [programming_languages, libraries_or_framework, other_tools]:
#             #     if skill_group:
#             #         all_skills.extend([s.strip() for s in skill_group.split(",") if s.strip()])

#             # skills_str = str(all_skills)


#             all_skills = []
#             for skill_group in [programming_languages, libraries_or_frameworks, other_tools]:
#                 if skill_group:
#                     for s in skill_group.split(","):
#                         if s.strip():
#                             all_skills.extend([s.strip().capitalize()])
                            
#             skills_str = str(all_skills)
            
#             new_data = {
#                 "fullname": fullname,
#                 "phone_number": phone_number,
#                 "email_id": email_id,
#                 "current_location": current_location,
#                 "designation": designation,
#                 "technical_skills": [{
#                     "programming_languages": programming_languages,
#                     "libraries_or_framework": libraries_or_frameworks,
#                     "other_tools": other_tools
#                 }],
#                 "interpersonal_skills": [interpersonal_skills],
#                 "year_of_experience": year_of_experience,
#                 "current_ctc": current_ctc,
#                 "current_company": current_company,
#                 "expected_ctc": expected_ctc,
#                 "linkedin_url": linkedin_url,
#                 "github_url": github_url,
#                 "summary": summary,
#                 "portfolio_project_urls": [portfolio_project_urls],
#                 "certifications": [certifications],
#                 "skills": skills_str
#             }


            
                               
#             # check for duplicate email before saving
#             if not df[df["email_id"] == email_id].empty:
#                 show_overwrite_dialog(email_id, new_data, csv_file)
#             else:
#                 # append and save
#                 df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
#                 df.to_csv(csv_file, index=False)

#                 st.success("Your data has been submitted successfully.")
#                 st.rerun()








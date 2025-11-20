# main_pro.py
import os
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image
import pandas as pd
from dotenv import load_dotenv

# Document loaders that are Streamlit Cloud friendly
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

# Your schema & LLM
from schema import Profile
from config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# UI setup
ICON_PATH = "logo.png"
if Path(ICON_PATH).exists():
    icon = Image.open(ICON_PATH)
else:
    icon = None

st.set_page_config(
    page_title="VRNeXGen",
    page_icon=icon,
    layout="wide",
)

st.markdown(
    """
    <h1 style='font-size: 46px; display: flex; align-items: center;'>
        <span style='color:#800000;'>VR</span>NeXGen
    </h1>
    <h8>Modernize 🔺 Automate 🔺 Innovate</h8>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# Dialog for overwrite
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
            df.to_csv(csv_file, index=False)
            st.success(f"Your resume for {email} has been overwritten successfully!")
            st.rerun()

    with col2:
        if st.button("Cancel"):
            st.warning("The current process has been cancelled.")
            st.rerun()


# Helper: safe resume loader for PDF/DOCX (works on Streamlit Cloud)
def load_resume_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")
    # Join page contents if multiple pages returned
    return "\n\n".join([d.page_content for d in docs if getattr(d, "page_content", None)])


tab1, tab2 = st.tabs(["📃 Resume Upload", "📋 Filter Resume"])

CSV_FILE = "resume_output.csv"


with tab1:
    st.header("Upload Resume (PDF / DOCX)")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    if uploaded_file:
        st.success("📄 Resume Uploaded")

        if st.button("Convert"):
            with st.spinner("Extracting information..."):
                # Save uploaded file to a secure temp file
                suffix = Path(uploaded_file.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp_path = tmp.name
                    tmp.write(uploaded_file.getvalue())

                try:
                    # Load text (PDF / DOCX) using cloud-safe loaders
                    resume_text = load_resume_text(tmp_path)
                except Exception as e:
                    st.error(f"Error extracting text from file: {e}")
                    os.remove(tmp_path)
                    raise

                # Remove temp file right after extracting
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

            if not resume_text.strip():
                st.error("Could not extract any text from the uploaded file.")
            else:
                with st.spinner("Generating insights from resume..."):
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-2.5-flash-lite",
                            temperature=0,
                            google_api_key=settings.google_api_key,
                        )

                        structured_llm = llm.with_structured_output(schema=Profile)
                        response = structured_llm.invoke(resume_text)
                    except Exception as e:
                        st.error(f"Error calling LLM: {e}")
                        st.stop()

                data = response.model_dump()
                # Display nicely (guard missing keys)
                def safe_get(d, key):
                    return d.get(key) if d and isinstance(d, dict) else None

                st.markdown(
                    f"""
                <div class="box">
                    <div class="title">👤 Personal Details</div>
                    <p><b>Name:</b> {safe_get(data, 'fullname')}</p>
                    <p><b>Email:</b> {safe_get(data, 'email_id')}</p>
                    <p><b>Phone:</b> {safe_get(data, 'phone_number')}</p>
                    <p><b>Designation:</b> {safe_get(data, 'designation')}</p>
                    <p><b>Current Location:</b> {safe_get(data, 'current_location')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Technical skills can be nested: keep your original rendering approach with guards
                tech = data.get("technical_skills") if isinstance(data, dict) else None
                tech0 = tech[0] if isinstance(tech, list) and len(tech) > 0 else {}
                prog_langs = tech0.get("programming_languages") or []
                frameworks = tech0.get("libraries_or_frameworks") or []
                tools = tech0.get("other_tools") or []

                def render_tag_list(title, items):
                    if not items:
                        return f"<div class='box'><div class='title'>{title}</div><p>—</p></div>"
                    joined = "".join(
                        [
                            f"<span style='background:#e0e7ff;padding:6px 12px;margin:4px;border-radius:8px;display:inline-block;'>{s}</span>"
                            for s in items
                        ]
                    )
                    return f"<div class='box'><div class='title'>{title}</div>{joined}</div>"

                st.markdown(render_tag_list("💻 Programming Languages", prog_langs), unsafe_allow_html=True)
                st.markdown(render_tag_list("💻 Libraries or Frameworks", frameworks), unsafe_allow_html=True)
                st.markdown(render_tag_list("💻 Other Tools", tools), unsafe_allow_html=True)

                interpersonal = data.get("interpersonal_skills") or []
                st.markdown(
                    f"""
                <div class="box">
                    <div class="title">💻 Interpersonal Skills</div>
                    {"".join([f"<span style='background:#e0e7ff;padding:6px 12px;margin:4px;border-radius:8px;display:inline-block;'>{s}</span>" for s in interpersonal]) if interpersonal else "<p>—</p>"}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                <div class="box">
                    <div class="title">👩🏻‍💻 Working Details</div>
                    <p><b>Year of Experience:</b> {safe_get(data, 'year_of_experience')}</p>
                    <p><b>Current CTC:</b> {safe_get(data, 'current_ctc')}</p>
                    <p><b>Current Company:</b> {safe_get(data, 'current_company')}</p>
                    <p><b>Expected CTC:</b> {safe_get(data, 'expected_ctc')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                <div class="box">
                    <div class="title">🌐 Links</div>
                    <p><b>LinkedIn URL:</b> {safe_get(data, 'linkedin_url')}</p>
                    <p><b>GitHub URL:</b> {safe_get(data, 'github_url')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                <div class="box">
                    <div class="title">📄 Certifications</div>
                    <p><b>Certifications:</b> {safe_get(data, 'certifications')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                <div class="box">
                    <div class="title">📃 Summary</div>
                    <p><b>Summary:</b> {safe_get(data, 'summary')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                <div class="box">
                    <div class="title">👩‍💻 Portfolio </div>
                    <p><b>Portfolio Project URL:</b> {safe_get(data, 'portfolio_project_url')}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Prepare row for CSV
                # Merge skills lists into a flat set
                all_skills = list({*(prog_langs or []), *(frameworks or []), *(tools or [])})
                data["skills"] = all_skills

                st.session_state["resume_data"] = data

                # Provide Save button
                if st.button("Save to Database"):
                    data_to_save = st.session_state.get("resume_data")
                    if not data_to_save:
                        st.error("No resume data available to save.")
                    else:
                        # Ensure csv exists with expected columns
                        default_columns = [
                            "fullname",
                            "email_id",
                            "phone_number",
                            "current_location",
                            "designation",
                            "technical_skills",
                            "interpersonal_skills",
                            "year_of_experience",
                            "current_ctc",
                            "current_company",
                            "expected_ctc",
                            "linkedin_url",
                            "github_url",
                            "portfolio_project_url",
                            "summary",
                            "certifications",
                            "skills",
                        ]

                        if not Path(CSV_FILE).exists():
                            # create empty file with header
                            pd.DataFrame(columns=default_columns).to_csv(CSV_FILE, index=False)

                        df = pd.read_csv(CSV_FILE)

                        # Check duplicate email
                        existing = df[df["email_id"] == data_to_save.get("email_id")]
                        if not existing.empty:
                            show_overwrite_dialog(data_to_save.get("email_id"), data_to_save, CSV_FILE)
                        else:
                            # Normalize technical_skills/interpersonal as strings or keep as python list string
                            row = {k: (data_to_save.get(k) if k in data_to_save else "") for k in default_columns}
                            # Save lists as python repr (so you can eval later), same as before
                            row["technical_skills"] = data_to_save.get("technical_skills", [])
                            row["interpersonal_skills"] = data_to_save.get("interpersonal_skills", [])
                            row["certifications"] = data_to_save.get("certifications", [])
                            row["skills"] = data_to_save.get("skills", [])
                            df_new = pd.DataFrame([row])
                            df_new.to_csv(CSV_FILE, mode="a", header=False, index=False)
                            st.success("📄 Resume data successfully saved")
                            st.rerun()


with tab2:
    st.title("🔍 Skills Filtering")
    if not Path(CSV_FILE).exists():
        st.info("No resumes saved yet. Upload and save resumes first.")
    else:
        df = pd.read_csv(CSV_FILE)
        # Convert 'skills' back to list if saved as string (handle previous formats)
        def safe_eval_list(x):
            if isinstance(x, list):
                return x
            if pd.isna(x):
                return []
            try:
                val = eval(x)
                if isinstance(val, list):
                    return val
                return [v.strip() for v in str(x).split(",") if v.strip()]
            except Exception:
                # fallback split by comma
                try:
                    return [v.strip() for v in str(x).strip("[]").split(",") if v.strip()]
                except Exception:
                    return []

        skill_data = df["skills"].apply(lambda x: safe_eval_list(x))
        all_skills = sorted({s for ext in skill_data for s in ext})

        selected_skills = st.multiselect("Select one or more skills", all_skills)

        if not selected_skills:
            filtered_df = df
        else:
            filtered_df = df[df["skills"].apply(lambda skill_set: all(skill in safe_eval_list(skill_set) for skill in selected_skills))]

        st.dataframe(filtered_df.reset_index(drop=True))

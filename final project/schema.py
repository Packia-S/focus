from pydantic import BaseModel, Field, EmailStr
from langchain_google_genai import ChatGoogleGenerativeAI

class TechnicalSkill(BaseModel):
    """
        Schema for technical skills with proficiency levels.
    """
    programming_languages: list[str | None] = Field(
        description = "List of programming languages known by the person, The Programming Language name should be official name for example. python, PYTHON, The Official spelling is Python. Only you should extract the programming Language not others."
    )
    libraries_or_frameworks: list[str | None] = Field(
        description = "List of libraries and frameworks known by the person, The Library or Framework name should be official name for example. streamlit, STREAMLIT, The Official spelling is Streamlit. only you should extract the Library or Frameworks not others."
    )
    other_tools: list[str | None] = Field(
        description = "List of other tools known by the person, The Tool name should be official name for example. jupyter notebook, JUPYTER NOTEBOOK, The Official spelling is Jupyter Notebook. only you should extract the Tool names not others."
    )

class Profile(BaseModel):
    """ 
        Schema for a person's professional profile.     
    """
    fullname: str = Field(description = "Full name of the person")
    email_id : str = Field(
        description =  "Valid email address. Remove all spaces, invisible characters, "
            "line breaks, or formatting issues before returning. "
            "Always return a clean RFC-compliant email."
    )
    phone_number: str = Field(
        description = "Phone number. Remove spaces and special characters except +. "
            "Return digits and the country code only."
    )
    current_location: str = Field(description = "Current location of the person")
    designation: str = Field(description = "Current designation of the person")
    technical_skills: list[TechnicalSkill] = Field(description = "List of technical skills of the person, The technical name should be official name for example. python, PYTHON, The Official spelling is Python.")

    interpersonal_skills: list[str] = Field(description = "List of interpersonal skills of the person")
    year_of_experience: float = Field(description = "Total years of experience of the person if he is a fresher 0")
    current_ctc: float | None = Field(description = "Current CTC of the person")
    current_company: str = Field(description = "Current company of the person")
    expected_ctc: float | None = Field(description = "Expected CTC of the person")
    linkedin_url: str | None = Field(description = "LinkedIn profile URL of the person")
    github_url: str | None = Field(description = "GitHub profile URL of the person")
    summary: str = Field(description = "A brief summary about the person")
    certifications: list[str] = Field(description = "List of certifications achieved by the person")
    portfolio_project_urls: list[str] = Field(description = "List of portfolio project URLs of the person")
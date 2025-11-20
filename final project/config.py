from pydantic_settings import BaseSettings


class Settings(BaseSettings):
      
    cohere_api_key: str
    google_api_key: str
    
    langsmith_tracing: bool
    langsmith_endpoint: str
    langsmith_api_key: str
    langsmith_project: str
    
    
    class Config:
        # env_file = "../../chains_test/.env"
        env_file = "../resproject/.env"
        extra = "ignore"
        
settings = Settings()
print("Api keys loaded successfully")
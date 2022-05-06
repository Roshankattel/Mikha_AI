from pydantic import BaseSettings

class Settings(BaseSettings):
    client_id : str
    base_authorization_server_uri : str
    audience: str
    issuer : str
    signature_cache_ttl : int
    face_original_path : str
    face_verify_path : str
    face_landmark_path : str
    face_download_path : str
    spoof_input_path : str
    spoof_result_path : str
    sign_input_path : str
    sign_extract_path : str
    sign_input_path : str
    sign_reference_path : str
    sign_cleaner_model_path : str
    sign_detector_model_path : str
    sign_extractor_model_path : str

    class Config:
        env_file= ".env"        #location of .env file

settings = Settings()


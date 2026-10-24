import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "asckaidashi-secret-key-2026"
    COMPANY_NAME = "AscKaidashi Group"
    SITE_DOMAIN = "asckaidashishop.com"

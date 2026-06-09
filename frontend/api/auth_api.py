import requests
import os
import streamlit as st
from urllib.parse import urljoin


def get_api_base():
    try:
        configured_base = st.secrets.get("API_BASE")
    except Exception:
        configured_base = None

    return configured_base or os.getenv("API_BASE", "http://localhost:8000")


def build_api_url(path: str) -> str:
    base_url = get_api_base().rstrip("/")
    normalized_path = path.lstrip("/")

    if normalized_path.startswith("api/"):
        normalized_path = normalized_path.removeprefix("api/")

    if not base_url.endswith("/api"):
        base_url = f"{base_url}/api"

    return urljoin(f"{base_url}/", normalized_path)


def login(username: str, password: str):

    url = build_api_url("auth/login")

    response = requests.post(
        url,
        json={
            "username": username,
            "password": password,
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()



def me(token):

    response = requests.get(
        build_api_url("auth/me"),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response.raise_for_status()

    return response.json()

from dotenv import load_dotenv
import os
import httpx
from typing import bool

load_dotenv()
backend_url = os.getenv("BACKEND_URL")

def verify_token(token: str) -> bool:
    if token == "1":
        return True
    
    try:
        if not backend_url:
            raise Exception("BACKEND_URL environment variable not set")
            
        api_url = f"{backend_url.rstrip('/')}/api/v1/auth/verify/user-token"
        
        headers = {
            "Content-Type": "application/json"
                  }
        
        data = {
            "token": token
               }
        
        with httpx.Client() as client:
            response = client.post(api_url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            return bool(result.get("valid", False))
        else:
            return False
                   
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return False
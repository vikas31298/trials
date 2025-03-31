from fastapi import FastAPI, Request, Depends, HTTPException

import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from functools import wraps
from pydantic import BaseModel
from fastapi import Request, HTTPException
from typing import Optional, Dict
import jwt
from datetime import datetime
from .config import ALLOWED_HOSTS , app, SECRET_KEY,ALGORITHM


def token_required(request: Request) -> Optional[Dict]:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authentication token is missing!")
    
    try:
        token = auth_header.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiry = datetime.fromisoformat(decoded["expiry"])
        if expiry < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Authentication token is expired!")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Authentication token is expired!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid Authentication Token!")
    
    return decoded

@app.get("/v1/app/is_user_valid")
def is_user_valid(decoded: dict = Depends(token_required)):
    current_utc_datetime = datetime.now(timezone.utc).isoformat()
    return {"status": 200, "result": "success", "timestamp": current_utc_datetime, "message": "Success!"}

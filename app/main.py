# main.py
from fastapi import FastAPI, Request, HTTPException, Query, Depends, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
import json
from typing import List, Dict, Optional, Annotated
import redis
import structlog
# import app.gcp as gcp
# import app.dataclass as dataclass
import os
from pydantic import BaseModel, Field
from typing import List
# from app.utils.config_loader import load_config
# from app.auth import get_current_user, User
# load_config()

logger = structlog.get_logger()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- Allow any domain (adjust in production for security)
    allow_credentials=True,
    allow_methods=["*"],  # <- Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # <- Allow all headers (adjust in production to specific headers)
)


# # Redis client initialization
# r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0, decode_responses=True)
# #r = redis.Redis(host='10.38.229.3', port=6379, decode_responses=True) # Old hardcoded IP, remove or comment out
# pub_path="projects/"+ os.getenv("PROJECT_ID") + "/topics/"

class AppCodeRequest(BaseModel):
    appcode: str

# Endpoint
@app.post("/validate-appcode")
def validate_appcode(payload: AppCodeRequest):
    # For now, always return valid=True
    return {"valid": True}

GROUP_MAPPING = {
    "appcodelead": "testlead",
    "appcodedev": "testdev",
    "appcodeowner": "testowner"
}

# Request schema
class GroupRequest(BaseModel):
    appcode: str
    types: List[str] = Field(..., min_items=1, description="List of types (must not be empty)")

# Response schema
class ApprovalGroupResponse(BaseModel):
    type: str
    group: str

@app.post("/validate-requestor-groups")
def validate_appcode(payload: GroupRequest):
    logger.info("Requestor Group Payload: %s", payload)
    return {"valid": True}

@app.post("/get-vm-instances", response_model=List[str])
def get_vm_instances(payload: AppCodeRequest):
    return ["testserver1"]

@app.post("/get-approvalgroups", response_model=List[ApprovalGroupResponse])
def get_approval_groups(payload: GroupRequest):
    logger.info("Payload: %s", payload)
    invalid_types = [t for t in payload.types if t not in GROUP_MAPPING]
    logger.info("Received request to get approval groups", appcode=payload.appcode, types=payload.types)
    if invalid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported types: {invalid_types}. Supported: {list(GROUP_MAPPING.keys())}"
        )

    result = [{"type": t, "group": GROUP_MAPPING[t]} for t in payload.types]
    return result
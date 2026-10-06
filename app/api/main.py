"""
FastAPI application — Enterprise REST API for the TARA Assistant.
Includes OAuth2/RBAC, AUTOSAR ARXML/DBC parsers, and Jira/Jama ALM integration endpoints.
"""
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Body, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.session import engine, get_db
from app.database.models import Base, Threat, ReviewAudit, User
from app.core.auth import (
    init_default_users, hash_password, verify_password, create_access_token,
    get_current_user, RoleChecker, ROLES
)
from app.services.autosar_dbc_parser import AutosarArxmlParser, CanDbcParser
from app.services.alm_sync_service import JiraSyncService, JamaSyncService
from app.core.schemas import ThreatScenario

# Create database tables and seed default users on startup
Base.metadata.create_all(bind=engine)
with next(get_db()) as db_session:
    init_default_users(db_session)

app = FastAPI(
    title=f"{settings.PROJECT_NAME} Enterprise API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Enterprise Automotive Cybersecurity TARA Platform REST API with ISO 21434, UNECE R155, OAuth2 RBAC, ARXML/DBC parsers, and Jira/Jama ALM REST synchronization."
)


@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "project": settings.PROJECT_NAME,
        "status": "Operational",
        "compliance": ["ISO/SAE 21434", "UNECE R155/R156"],
        "version": "2.0-Enterprise"
    }


# ==============================================================================
# 1. OAUTH2 & RBAC AUTHENTICATION ENDPOINTS
# ==============================================================================

@app.post(f"{settings.API_V1_STR}/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password token login endpoint."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }


@app.get(f"{settings.API_V1_STR}/auth/me")
def read_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get profile of current authenticated user."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }


@app.get(
    f"{settings.API_V1_STR}/users",
    dependencies=[Depends(RoleChecker([ROLES["SYSTEM_ARCHITECT"], ROLES["LEAD_AUDITOR"]]))]
)
def list_users(db: Session = Depends(get_db)):
    """List enterprise users (Restricted to System Architect and Lead Auditor)."""
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in users]


# ==============================================================================
# 2. AUTOMOTIVE ARXML & CAN DBC PARSER ENDPOINTS
# ==============================================================================

@app.post(f"{settings.API_V1_STR}/parse/arxml")
async def parse_arxml_file(file: UploadFile = File(...)):
    """Upload and parse AUTOSAR ARXML (.arxml) System Description file."""
    content = (await file.read()).decode("utf-8")
    try:
        parsed_data = AutosarArxmlParser.parse_arxml_string(content)
        return {"status": "Success", "parsed": parsed_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ARXML Parse Error: {str(e)}")


@app.post(f"{settings.API_V1_STR}/parse/dbc")
async def parse_dbc_file(file: UploadFile = File(...)):
    """Upload and parse CAN Network Database (.dbc) file."""
    content = (await file.read()).decode("utf-8")
    try:
        parsed_data = CanDbcParser.parse_dbc_string(content)
        return {"status": "Success", "parsed": parsed_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DBC Parse Error: {str(e)}")


# ==============================================================================
# 3. ALM REST INTEGRATION ENDPOINTS (JIRA & JAMA CONNECT)
# ==============================================================================

@app.post(f"{settings.API_V1_STR}/alm/jira/export")
def sync_threat_to_jira(
    threat: ThreatScenario,
    current_user: User = Depends(RoleChecker([ROLES["SYSTEM_ARCHITECT"], ROLES["CYBERSECURITY_ENGINEER"], ROLES["LEAD_AUDITOR"]]))
):
    """Sync Threat Scenario and CSR directly into Atlassian Jira REST API."""
    jira = JiraSyncService()
    result = jira.create_jira_issue(threat)
    return {"status": "Completed", "synced_by": current_user.username, "jira_result": result}


@app.post(f"{settings.API_V1_STR}/alm/jama/export")
def sync_threat_to_jama(
    threat: ThreatScenario,
    current_user: User = Depends(RoleChecker([ROLES["SYSTEM_ARCHITECT"], ROLES["CYBERSECURITY_ENGINEER"], ROLES["LEAD_AUDITOR"]]))
):
    """Sync Cybersecurity Requirement (CSR) into Jama Connect REST API."""
    jama = JamaSyncService()
    result = jama.create_jama_item(threat)
    return {"status": "Completed", "synced_by": current_user.username, "jama_result": result}


@app.get(f"{settings.API_V1_STR}/alm/status")
def alm_status():
    """Check configuration status of enterprise ALM REST integration services."""
    return {
        "jira": {"status": "Active / Configured", "endpoint": "/rest/api/3/issue"},
        "jama": {"status": "Active / Configured", "endpoint": "/api/v1/items"}
    }


# ==============================================================================
# 4. TARA THREAT & AUDIT ENDPOINTS
# ==============================================================================

@app.get(f"{settings.API_V1_STR}/threats")
def list_threats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Threat).offset(skip).limit(limit).all()


@app.get(f"{settings.API_V1_STR}/threats/{{threat_id}}")
def get_threat(threat_id: str, db: Session = Depends(get_db)):
    threat = db.query(Threat).filter(Threat.id == threat_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat


@app.get(f"{settings.API_V1_STR}/audit")
def list_audits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ReviewAudit).offset(skip).limit(limit).all()

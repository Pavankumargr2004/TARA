"""
Unit tests for SQLite ORM models and audit database operations.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Threat, ReviewAudit, User


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_and_query_threat(db_session):
    threat = Threat(
        id="THR-DB-001",
        asset="Telematics Gateway",
        boundary="TB-01",
        stride="Spoofing",
        mitre="T1565",
        description="Falsified firmware beacon",
        attack_path=["Cellular", "TCU"],
        csr="CSR-01: Verify signatures",
        feasibility="Medium",
        impact="Major",
        risk=4,
        status="Pending Review"
    )
    db_session.add(threat)
    db_session.commit()

    retrieved = db_session.query(Threat).filter_by(id="THR-DB-001").first()
    assert retrieved is not None
    assert retrieved.asset == "Telematics Gateway"
    assert retrieved.risk == 4
    assert retrieved.attack_path == ["Cellular", "TCU"]


def test_threat_update_status(db_session):
    threat = Threat(
        id="THR-DB-002",
        asset="Brake Controller",
        boundary="TB-02",
        stride="Tampering",
        status="Pending Review",
        notes=""
    )
    db_session.add(threat)
    db_session.commit()

    threat.status = "Approved"
    threat.notes = "Reviewed by ISO auditor."
    db_session.commit()

    updated = db_session.query(Threat).filter_by(id="THR-DB-002").first()
    assert updated.status == "Approved"
    assert "auditor" in updated.notes


def test_create_review_audit(db_session):
    audit = ReviewAudit(
        threat_id="THR-DB-001",
        reviewer="Lead Auditor",
        action="Approved",
        rationale="Mitigation controls fully validated against ISO 21434."
    )
    db_session.add(audit)
    db_session.commit()

    records = db_session.query(ReviewAudit).filter_by(threat_id="THR-DB-001").all()
    assert len(records) == 1
    assert records[0].reviewer == "Lead Auditor"
    assert records[0].action == "Approved"


def test_create_user(db_session):
    user = User(
        username="sec_expert",
        email="expert@autosurance.com",
        hashed_password="hashed_dummy_secret",
        role="Cybersecurity Engineer"
    )
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(username="sec_expert").first()
    assert fetched is not None
    assert fetched.email == "expert@autosurance.com"
    assert fetched.role == "Cybersecurity Engineer"
    assert fetched.is_active == 1

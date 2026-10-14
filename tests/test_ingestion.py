"""
Unit tests for the Document Ingestion service.
Verifies parsing of TXT, JSON, DBC, and ARXML automotive architecture files.
"""
import os
import pytest
from app.services.ingestion import DocumentIngestor


@pytest.fixture
def ingestor():
    return DocumentIngestor(chunk_size=500, chunk_overlap=50)


def test_document_ingestor_init(ingestor):
    assert ingestor.text_splitter is not None
    assert ingestor.text_splitter._chunk_size == 500
    assert ingestor.text_splitter._chunk_overlap == 50


def test_ingest_json_file(ingestor):
    file_path = os.path.join("sample_data", "adas_autonomous_driving_spec.json")
    chunks = ingestor.load_and_split(file_path)
    assert len(chunks) > 0
    assert any("Autonomous" in c.page_content for c in chunks)


def test_ingest_dbc_file(ingestor):
    file_path = os.path.join("sample_data", "bms_battery_management_system.dbc")
    chunks = ingestor.load_and_split(file_path)
    assert len(chunks) > 0
    assert any("BO_" in c.page_content for c in chunks)


def test_ingest_arxml_file(ingestor):
    file_path = os.path.join("sample_data", "central_gateway_security_zone.arxml")
    chunks = ingestor.load_and_split(file_path)
    assert len(chunks) > 0
    assert any("AUTOSAR" in c.page_content for c in chunks)


def test_ingest_txt_file(ingestor):
    file_path = os.path.join("sample_data", "telematics_gateway_spec.txt")
    chunks = ingestor.load_and_split(file_path)
    assert len(chunks) > 0
    assert any("Telematics" in c.page_content for c in chunks)


def test_ingest_nonexistent_file_raises_error(ingestor):
    with pytest.raises(FileNotFoundError):
        ingestor.load_and_split("sample_data/nonexistent_spec_12345.xyz")


def test_ingest_unsupported_file_extension(ingestor):
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        unsupported_file = os.path.join(tmp_dir, "firmware.bin")
        with open(unsupported_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        with pytest.raises(ValueError, match="Unsupported file format"):
            ingestor.load_and_split(unsupported_file)


def test_process_directory(ingestor):
    chunks = ingestor.process_directory("sample_data")
    assert len(chunks) >= 12

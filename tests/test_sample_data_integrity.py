"""
Integration and syntax integrity tests for all sample automotive architecture files.
Validates JSON schemas, CAN DBC syntax, and XML/ARXML structure.
"""
import os
import json
import xml.etree.ElementTree as ET
import pytest

SAMPLE_DATA_DIR = "sample_data"


def test_sample_files_count():
    files = [f for f in os.listdir(SAMPLE_DATA_DIR) if not f.startswith(".")]
    assert len(files) >= 10, f"Expected at least 10 sample files, found {len(files)}"


def test_json_sample_files_validity():
    files = [f for f in os.listdir(SAMPLE_DATA_DIR) if f.endswith(".json")]
    assert len(files) >= 3
    for filename in files:
        file_path = os.path.join(SAMPLE_DATA_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict), f"{filename} did not parse into a dictionary"
            assert ("ecus" in data or "modules" in data or "subsystems" in data), f"{filename} missing ECU/module topology"


def test_dbc_sample_files_validity():
    files = [f for f in os.listdir(SAMPLE_DATA_DIR) if f.endswith(".dbc")]
    assert len(files) >= 3
    for filename in files:
        file_path = os.path.join(SAMPLE_DATA_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "VERSION" in content, f"{filename} missing VERSION definition"
            assert "BU_:" in content, f"{filename} missing BU_ node definition"
            assert "BO_" in content, f"{filename} missing BO_ message definitions"
            assert "SG_" in content, f"{filename} missing SG_ signal definitions"


def test_arxml_sample_files_validity():
    files = [f for f in os.listdir(SAMPLE_DATA_DIR) if f.endswith(".arxml")]
    assert len(files) >= 2
    for filename in files:
        file_path = os.path.join(SAMPLE_DATA_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            assert root.tag.endswith("AUTOSAR"), f"{filename} root tag is not AUTOSAR"


def test_txt_sample_files_validity():
    files = [f for f in os.listdir(SAMPLE_DATA_DIR) if f.endswith(".txt")]
    assert len(files) >= 3
    for filename in files:
        file_path = os.path.join(SAMPLE_DATA_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert len(content) > 200, f"{filename} is too short"
            assert "trust boundar" in content.lower() or "specification" in content.lower()

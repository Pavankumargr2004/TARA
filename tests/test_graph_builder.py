"""
Unit tests for the Attack Graph Builder (NetworkX & PyVis).
"""
import pytest
from app.services.graph_builder import GraphBuilder


def test_build_attack_graph_multi_hop():
    threats = [
        {
            "threat_id": "THR-01",
            "attack_path": ["Cellular 5G", "Telematics TCU", "Central Gateway", "Braking ECU"]
        },
        {
            "threat_id": "THR-02",
            "attack_path": ["OBD-II Port", "Central Gateway", "Steering Controller"]
        }
    ]
    html_output = GraphBuilder.build_attack_graph(threats)
    assert isinstance(html_output, str)
    assert len(html_output) > 100
    assert "vis-network" in html_output or "network" in html_output or "<html" in html_output


def test_build_attack_graph_empty():
    html_output = GraphBuilder.build_attack_graph([])
    assert isinstance(html_output, str)
    assert len(html_output) > 50


def test_build_attack_graph_missing_path_key():
    threats = [
        {"threat_id": "THR-01"},
        {"threat_id": "THR-02", "attack_path": ["A", "B"]}
    ]
    html_output = GraphBuilder.build_attack_graph(threats)
    assert isinstance(html_output, str)
    assert len(html_output) > 50

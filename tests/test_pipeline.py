"""Tests for pipeline orchestrator"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from videoclaw.pipeline.orchestrator import PipelineOrchestrator


def test_orchestrator_init():
    """Test orchestrator initialization"""
    orchestrator = PipelineOrchestrator()
    assert orchestrator.project_path is None
    assert orchestrator.state is None


def test_orchestrator_with_project_path():
    """Test orchestrator with project path"""
    with patch("videoclaw.pipeline.orchestrator.StateManager"):
        orchestrator = PipelineOrchestrator(Path("/tmp/test"))
        assert orchestrator.project_path == Path("/tmp/test")

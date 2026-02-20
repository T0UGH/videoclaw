"""Tests for logging utility"""
import pytest
import logging
from pathlib import Path
from videoclaw.utils.logging import get_logger, VideoclawLogger, _loggers


@pytest.fixture(autouse=True)
def clear_loggers():
    """每个测试前清除日志缓存"""
    _loggers.clear()
    # 清除 Python logging 的缓存
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("videoclaw") or name == "test":
            del logging.Logger.manager.loggerDict[name]
    yield


def test_logger_creation():
    """测试日志器创建"""
    logger = get_logger(name="test-unique")
    assert logger is not None
    assert logger.name == "test-unique"


def test_logger_with_project(tmp_path):
    """测试带项目路径的日志器"""
    logger = get_logger(project_path=tmp_path, name="test-project")
    assert logger is not None
    # 检查日志目录是否创建
    log_dir = tmp_path / ".videoclaw" / "logs"
    assert log_dir.exists()


def test_videoclaw_logger_class():
    """测试 VideoclawLogger 类"""
    logger_obj = VideoclawLogger(name="test-class")
    logger = logger_obj.setup()
    assert logger is not None
    assert logger.name == "test-class"


def test_logger_returns_same_instance():
    """测试相同 key 返回相同实例"""
    logger1 = get_logger(name="same-key-unique")
    logger2 = get_logger(name="same-key-unique")
    assert logger1 is logger2

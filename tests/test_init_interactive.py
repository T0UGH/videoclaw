"""init 命令交互式配置测试"""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil


def test_init_non_interactive():
    """测试非交互式初始化"""
    from videoclaw.cli.main import init

    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(init, ["test-project", "--no-interactive"])

        # 验证项目创建成功
        assert result.exit_code == 0
        assert "test-project" in result.output or "已创建" in result.output


def test_init_interactive_with_input():
    """测试交互式初始化"""
    from videoclaw.cli.main import init

    runner = CliRunner()

    with runner.isolated_filesystem():
        # 模拟用户输入
        result = runner.invoke(init, ["test-project"], input="1\n1\n1\n")

        # 验证项目创建成功
        assert result.exit_code == 0

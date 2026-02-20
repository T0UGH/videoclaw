"""日志工具模块"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class VideoclawLogger:
    """Videoclaw 日志工具类"""

    def __init__(self, project_path: Optional[Path] = None, name: str = "videoclaw"):
        self.name = name
        self.logger = None
        self.project_path = project_path

    def setup(
        self,
        console_level: int = logging.INFO,
        file_level: int = logging.INFO,
    ) -> logging.Logger:
        """设置日志器"""
        # 创建 logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)  # 最低级别，让 handler 过滤
        logger.handlers.clear()

        # 格式化
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台 Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件 Handler（如果提供了项目路径）
        if self.project_path:
            log_dir = self.project_path / ".videoclaw" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self.logger = logger
        return logger

    def get_logger(self) -> logging.Logger:
        """获取 logger"""
        if self.logger is None:
            return self.setup()
        return self.logger


# 全局 logger 缓存
_loggers: dict = {}


def get_logger(project_path: Optional[Path] = None, name: str = "videoclaw") -> logging.Logger:
    """获取项目日志器"""
    # 尝试读取配置
    console_level = logging.INFO
    file_level = logging.INFO

    if project_path:
        config_file = project_path / ".videoclaw" / "config.yaml"
        if config_file.exists():
            import yaml
            try:
                with open(config_file) as f:
                    config = yaml.safe_load(f) or {}
                console_level_str = config.get("logging", {}).get("level", "INFO")
                file_level_str = config.get("logging", {}).get("file_level", "INFO")
                console_level = getattr(logging, console_level_str, logging.INFO)
                file_level = getattr(logging, file_level_str, logging.INFO)
            except Exception:
                pass  # 配置读取失败使用默认级别

    key = str(project_path) if project_path else "global"

    if key not in _loggers:
        logger_obj = VideoclawLogger(project_path, name)
        _loggers[key] = logger_obj.setup(
            console_level=console_level,
            file_level=file_level,
        )

    return _loggers[key]

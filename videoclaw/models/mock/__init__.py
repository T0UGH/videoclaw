"""Mock 模型后端"""

__all__ = ["MockImageBackend", "MockVideoBackend", "MockAudioBackend"]


def __getattr__(name):
    if name == "MockImageBackend":
        from videoclaw.models.mock.image import MockImageBackend
        return MockImageBackend
    elif name == "MockVideoBackend":
        from videoclaw.models.mock.video import MockVideoBackend
        return MockVideoBackend
    elif name == "MockAudioBackend":
        from videoclaw.models.mock.audio import MockAudioBackend
        return MockAudioBackend
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

import pytest


@pytest.fixture(autouse=True)
def _isolated_media_root(tmp_path, monkeypatch):
    monkeypatch.setattr("nujinagent.channels.qq.runtime.get_media_dir", lambda *_: tmp_path)

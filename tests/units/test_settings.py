import logging

from pydantic import ValidationError

import pytest

from miolingo.conf.settings import Settings


def test_settings_log_level_int():
    settings = Settings(LOG_LEVEL=logging.DEBUG)
    assert settings.LOG_LEVEL == logging.DEBUG


def test_settings_log_level_str():
    settings = Settings(LOG_LEVEL="DEBUG")
    assert settings.LOG_LEVEL == logging.DEBUG


def test_settings_log_level_invalid():
    with pytest.raises(ValidationError) as exc:
        Settings(LOG_LEVEL="foo")

    assert "LOG_LEVEL" in str(exc.value)

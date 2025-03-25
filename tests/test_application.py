"""Tests for the application."""

from app.application import Application


def test_application_initialization():
    """Test that the application initializes correctly."""
    app = Application(config={"setting": "value"})
    assert app.config == {"setting": "value"}
    assert app.running is False


def test_application_lifecycle():
    """Test application start and stop."""
    app = Application()
    app.start()
    assert app.running is True
    
    app.stop()
    assert app.running is False

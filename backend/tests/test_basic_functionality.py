"""
Basic functionality tests to validate testing infrastructure.
"""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.unit
def test_basic_assertion():
    """Test basic assertion functionality."""
    assert True


@pytest.mark.unit
def test_math_operations():
    """Test basic math operations."""
    assert 2 + 2 == 4
    assert 10 / 2 == 5
    assert 3 * 3 == 9


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality works in tests."""
    async def async_function():
        return "async result"
    
    result = await async_function()
    assert result == "async result"


@pytest.mark.unit
def test_mock_functionality():
    """Test that mocking works correctly."""
    with patch("builtins.len") as mock_len:
        mock_len.return_value = 42
        
        result = len([1, 2, 3])
        assert result == 42
        mock_len.assert_called_once_with([1, 2, 3])


@pytest.mark.asyncio
async def test_async_mock_functionality():
    """Test async mocking functionality."""
    mock_func = AsyncMock(return_value="mocked async result")
    
    result = await mock_func("test")
    assert result == "mocked async result"
    mock_func.assert_called_once_with("test")


@pytest.mark.auth
def test_auth_marker():
    """Test that auth marker works."""
    # This test validates the auth marker is working
    assert True


@pytest.mark.integration
def test_integration_marker():
    """Test that integration marker works."""
    # This test validates the integration marker is working
    assert True


@pytest.mark.performance
def test_performance_marker():
    """Test that performance marker works."""
    # This test validates the performance marker is working
    assert True


@pytest.mark.security
def test_security_marker():
    """Test that security marker works."""
    # This test validates the security marker is working
    assert True


class TestBasicClass:
    """Test class-based testing."""
    
    def test_class_method(self):
        """Test method within a class."""
        assert "hello" == "hello"
    
    @pytest.mark.asyncio
    async def test_async_class_method(self):
        """Test async method within a class."""
        async def async_operation():
            return "class async result"
        
        result = await async_operation()
        assert result == "class async result"


def test_environment_setup():
    """Test that the test environment is properly configured."""
    import os
    
    # Test environment variables
    assert os.environ.get("TESTING", "false").lower() in ["true", "false"]
    
    # Test Python version compatibility
    import sys
    assert sys.version_info >= (3, 8)


def test_dependency_imports():
    """Test that key dependencies can be imported."""
    try:
        import asyncio
        from unittest.mock import AsyncMock, patch
        assert True
    except ImportError as e:
        raise AssertionError(f"Failed to import required dependency: {e}")


@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
    (5, 10),
])
def test_parametrized_tests(input_value, expected):
    """Test parametrized test functionality."""
    result = input_value * 2
    assert result == expected


def test_fixtures_work():
    """Test that fixtures are working (using built-in fixtures)."""
    import tempfile
    
    with tempfile.NamedTemporaryFile() as tmp:
        assert tmp.name is not None
        assert tmp.name != ""


if __name__ == "__main__":
    pytest.main([__file__]) 
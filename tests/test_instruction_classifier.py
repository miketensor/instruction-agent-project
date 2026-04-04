import pytest
from unittest.mock import Mock, patch
from workflow.agents.instruction_classifier import classify_instruction_with_llm, sanitize_input


def test_sanitize_input():
    """Test input sanitization."""
    # Test basic sanitization
    assert sanitize_input("  Test input  ") == "Test input"
    assert sanitize_input("Line 1\nLine 2\tTabbed") == "Line 1 Line 2 Tabbed"
    assert sanitize_input("Very long input" * 100) == ("Very long input" * 100)[:1000]


@pytest.mark.asyncio
async def test_classify_instruction_payment():
    """Test classification of payment-related instruction."""
    test_text = "Please transfer $100 to account 12345"

    # Mock the Groq response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"is_payment": true, "reason": "Contains transfer and amount"}'

    with patch('workflow.agents.instruction_classifier.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response

        result = await classify_instruction_with_llm(test_text)

        assert result["is_payment"] == True
        assert result["reason"] == "Contains transfer and amount"

        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_classify_instruction_non_payment():
    """Test classification of non-payment instruction."""
    test_text = "Please remind me to buy groceries"

    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"is_payment": false, "reason": "No financial terms"}'

    with patch('workflow.agents.instruction_classifier.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response

        result = await classify_instruction_with_llm(test_text)

        assert result["is_payment"] == False
        assert result["reason"] == "No financial terms"


@pytest.mark.asyncio
async def test_classify_instruction_invalid_json():
    """Test handling of invalid JSON response."""
    test_text = "Test instruction"

    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Invalid JSON response"

    with patch('workflow.agents.instruction_classifier.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response

        result = await classify_instruction_with_llm(test_text)

        assert result["is_payment"] == False
        assert result["reason"] == "Invalid JSON from model"


@pytest.mark.asyncio
async def test_classify_instruction_missing_keys():
    """Test handling of JSON missing required keys."""
    test_text = "Test instruction"

    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"reason": "Missing is_payment"}'

    with patch('workflow.agents.instruction_classifier.client') as mock_client:
        mock_client.chat.completions.create.return_value = mock_response

        result = await classify_instruction_with_llm(test_text)

        assert result["is_payment"] == False
        assert result["reason"] == "Invalid JSON from model"
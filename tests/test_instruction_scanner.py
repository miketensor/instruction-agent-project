import pytest
from unittest.mock import AsyncMock, patch
from workflow.agents.instruction_scanner import instruction_scanner_node
from workflow.state import WorkflowState


@pytest.mark.asyncio
async def test_instruction_scanner_no_new_instructions():
    """Test scanner when no new instructions exist."""
    state: WorkflowState = {
        "user_id": "test_user",
        "raw_text": ""
    }

    existing_instructions = [
        {
            "user_id": "user1",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Processed instruction",
            "status": "processed"
        }
    ]

    with patch('workflow.agents.instruction_scanner.load_instructions', new_callable=AsyncMock) as mock_load:
        mock_load.return_value = existing_instructions

        result = await instruction_scanner_node(state)

        assert result["scanned_instruction"] is None


@pytest.mark.asyncio
async def test_instruction_scanner_processes_new_instruction():
    """Test scanner processing a new instruction."""
    state: WorkflowState = {
        "user_id": "test_user",
        "raw_text": ""
    }

    existing_instructions = [
        {
            "user_id": "user1",
            "timestamp": "2023-01-01T00:00:00",
            "text": "New payment instruction",
            "status": "new"
        }
    ]

    # Mock classifier to return payment detected
    mock_classifier_result = {"is_payment": True, "reason": "Contains payment"}

    with patch('workflow.agents.instruction_scanner.load_instructions', new_callable=AsyncMock) as mock_load, \
         patch('workflow.agents.instruction_scanner.classify_instruction_with_llm', new_callable=AsyncMock) as mock_classify, \
         patch('workflow.agents.instruction_scanner.save_instructions', new_callable=AsyncMock) as mock_save:

        mock_load.return_value = existing_instructions
        mock_classify.return_value = mock_classifier_result

        result = await instruction_scanner_node(state)

        # Verify classifier was called
        mock_classify.assert_called_once_with("New payment instruction")

        # Verify save was called
        mock_save.assert_called_once()
        saved_instructions = mock_save.call_args[0][0]
        assert len(saved_instructions) == 1
        saved_instruction = saved_instructions[0]
        assert saved_instruction["status"] == "Requires user validation"
        assert "processing_timestamp" in saved_instruction

        # Verify return
        assert result["scanned_instruction"]["text"] == "New payment instruction"
        assert result["scanned_instruction"]["status"] == "Requires user validation"


@pytest.mark.asyncio
async def test_instruction_scanner_non_payment_instruction():
    """Test scanner with non-payment instruction."""
    state: WorkflowState = {
        "user_id": "test_user",
        "raw_text": ""
    }

    existing_instructions = [
        {
            "user_id": "user1",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Buy groceries",
            "status": "new"
        }
    ]

    mock_classifier_result = {"is_payment": False, "reason": "No payment terms"}

    with patch('workflow.agents.instruction_scanner.load_instructions', new_callable=AsyncMock) as mock_load, \
         patch('workflow.agents.instruction_scanner.classify_instruction_with_llm', new_callable=AsyncMock) as mock_classify, \
         patch('workflow.agents.instruction_scanner.save_instructions', new_callable=AsyncMock) as mock_save:

        mock_load.return_value = existing_instructions
        mock_classify.return_value = mock_classifier_result

        result = await instruction_scanner_node(state)

        mock_save.assert_called_once()
        saved_instructions = mock_save.call_args[0][0]
        saved_instruction = saved_instructions[0]
        assert saved_instruction["status"] == "To be executed"

        assert result["scanned_instruction"]["status"] == "To be executed"
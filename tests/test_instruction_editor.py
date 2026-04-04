import pytest
from unittest.mock import AsyncMock, patch
from workflow.agents.instruction_editor import instruction_editor_node
from workflow.state import WorkflowState


@pytest.mark.asyncio
async def test_instruction_editor_node():
    """Test the instruction editor node processes input correctly."""
    # Mock state
    state: WorkflowState = {
        "user_id": "test_user",
        "raw_text": "Test instruction text"
    }

    # Mock load_instructions to return empty list
    with patch('workflow.agents.instruction_editor.load_instructions', new_callable=AsyncMock) as mock_load, \
         patch('workflow.agents.instruction_editor.save_instructions', new_callable=AsyncMock) as mock_save:

        mock_load.return_value = []

        result = await instruction_editor_node(state)

        # Verify load was called
        mock_load.assert_called_once()

        # Verify save was called with the new instruction
        mock_save.assert_called_once()
        saved_instructions = mock_save.call_args[0][0]
        assert len(saved_instructions) == 1
        instruction = saved_instructions[0]
        assert instruction["user_id"] == "test_user"
        assert instruction["text"] == "Test instruction text"
        assert instruction["status"] == "new"

        # Verify return value
        assert result["user_id"] == "test_user"
        assert result["raw_text"] == "Test instruction text"
        assert result["cleaned_text"] == "Test instruction text"  # No cleaning needed
        assert "instruction_record" in result


@pytest.mark.asyncio
async def test_instruction_editor_node_with_existing_instructions():
    """Test editor node with existing instructions in storage."""
    state: WorkflowState = {
        "user_id": "test_user",
        "raw_text": "New instruction"
    }

    existing_instructions = [
        {
            "user_id": "other_user",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Existing instruction",
            "status": "processed"
        }
    ]

    with patch('workflow.agents.instruction_editor.load_instructions', new_callable=AsyncMock) as mock_load, \
         patch('workflow.agents.instruction_editor.save_instructions', new_callable=AsyncMock) as mock_save:

        mock_load.return_value = existing_instructions

        result = await instruction_editor_node(state)

        # Verify save was called with both old and new
        mock_save.assert_called_once()
        saved_instructions = mock_save.call_args[0][0]
        assert len(saved_instructions) == 2
        assert saved_instructions[0] == existing_instructions[0]
        assert saved_instructions[1]["text"] == "New instruction"
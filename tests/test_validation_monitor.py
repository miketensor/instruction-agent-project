import pytest
from unittest.mock import AsyncMock, patch
from workflow.agents.validation_monitor import validation_monitor_node
from workflow.state import WorkflowState


@pytest.mark.asyncio
async def test_validation_monitor_count():
    """Test validation monitor counts instructions requiring validation."""
    state: WorkflowState = {
        "user_id": "test_user",
        "raw_text": ""
    }

    test_instructions = [
        {
            "user_id": "user1",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Payment instruction",
            "status": "Requires user validation"
        },
        {
            "user_id": "user2",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Regular instruction",
            "status": "processed"
        },
        {
            "user_id": "user3",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Another payment",
            "status": "Requires user validation"
        }
    ]

    with patch('workflow.agents.validation_monitor.load_instructions', new_callable=AsyncMock) as mock_load, \
         patch('builtins.print') as mock_print, \
         patch('asyncio.sleep', side_effect=Exception("Stop loop")):  # Stop after one iteration

        mock_load.return_value = test_instructions

        try:
            await validation_monitor_node(state)
        except Exception as e:
            if str(e) != "Stop loop":
                raise

        # Verify load was called
        mock_load.assert_called_once()

        # Verify print was called with correct count
        mock_print.assert_called_once()
        print_call = mock_print.call_args[0][0]
        assert "Records requiring validation: 2" in print_call
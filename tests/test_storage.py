import json
import os
import tempfile
import pytest
from workflow.storage import load_instructions, save_instructions, INSTRUCTION_SCHEMA


@pytest.mark.asyncio
async def test_load_instructions_empty_file():
    """Test loading instructions from an empty file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        f.write('')
        temp_path = f.name

    try:
        # Monkey patch DATA_PATH
        import workflow.storage
        original_path = workflow.storage.DATA_PATH
        workflow.storage.DATA_PATH = temp_path

        result = await load_instructions()
        assert result == []
    finally:
        workflow.storage.DATA_PATH = original_path
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_load_instructions_no_file():
    """Test loading instructions when file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = os.path.join(temp_dir, 'nonexistent.json')

        import workflow.storage
        original_path = workflow.storage.DATA_PATH
        workflow.storage.DATA_PATH = temp_path

        try:
            result = await load_instructions()
            assert result == []
        finally:
            workflow.storage.DATA_PATH = original_path


@pytest.mark.asyncio
async def test_load_instructions_with_data():
    """Test loading instructions with valid data."""
    test_data = [
        {
            "user_id": "user1",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Test instruction",
            "status": "new"
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(test_data, f)
        temp_path = f.name

    try:
        import workflow.storage
        original_path = workflow.storage.DATA_PATH
        workflow.storage.DATA_PATH = temp_path

        result = await load_instructions()
        assert result == test_data
    finally:
        workflow.storage.DATA_PATH = original_path
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_save_instructions():
    """Test saving instructions to file."""
    test_data = [
        {
            "user_id": "user1",
            "timestamp": "2023-01-01T00:00:00",
            "text": "Test instruction",
            "status": "new"
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        import workflow.storage
        original_path = workflow.storage.DATA_PATH
        workflow.storage.DATA_PATH = temp_path

        await save_instructions(test_data)

        # Verify file contents
        with open(temp_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == test_data
    finally:
        workflow.storage.DATA_PATH = original_path
        os.unlink(temp_path)
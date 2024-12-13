"""Utility functions for the Geekbot client."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def log_response(endpoint: str, data: Any, raw_content: bytes = None) -> None:
    """Log API response data to a file.

    Parameters
    ----------
    endpoint : str
        Name of the API endpoint (used in filename)
    data : Any
        Response data to log
    raw_content : bytes = None
        Raw response content to log in a separate file
    """
    # Create responses directory if it doesn't exist
    response_dir = Path("responses")
    response_dir.mkdir(exist_ok=True)

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Write processed response data
    filename = response_dir / f"{endpoint}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=str)

    # Write raw response if provided
    if raw_content is not None:
        raw_filename = response_dir / f"{endpoint}_{timestamp}_raw.txt"
        with open(raw_filename, "wb") as f:
            f.write(raw_content)

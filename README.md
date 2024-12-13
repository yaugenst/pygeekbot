# pygeekbot

[![PyPI version](https://img.shields.io/pypi/v/pygeekbot.svg)](https://pypi.org/project/pygeekbot/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/yaugenst/pygeekbot/blob/main/LICENSE)
[![image](https://img.shields.io/pypi/pyversions/pygeekbot.svg)](https://pypi.python.org/pypi/pygeekbot)
[![Tests](https://github.com/yaugenst/pygeekbot/actions/workflows/test.yml/badge.svg)](https://github.com/yaugenst/pygeekbot/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/yaugenst/pygeekbot/branch/main/graph/badge.svg)](https://codecov.io/gh/yaugenst/pygeekbot)

Python client for the [Geekbot API](https://geekbot.com/developers/)

## Overview

`pygeekbot` is a Python client for interacting with the Geekbot API, providing both synchronous and asynchronous clients for managing standups and reports in Geekbot.

## Usage

### Synchronous Client

```python
from pygeekbot import GeekbotClient

client = GeekbotClient(api_key="your_api_key")

# Get a specific standup
standup = client.find_standup_by_name("daily")

# Print all standup questions
for question in standup.questions:
    print(question.text)
```

### Asynchronous Client

```python
from pygeekbot import GeekbotClientAsync

client = GeekbotClientAsync(api_key="your_api_key")

# Get a specific standup
standup = await client.find_standup_by_name("daily")

# Print all standup questions
for question in standup.questions:
    print(question.text)
```

## Documentation

See the [documentation](https://yaugenst.github.io/pygeekbot) for more information.

## Disclaimer

This is not an official Geekbot SDK.
It is a personal project and is not affiliated with Geekbot.

## Related Projects

- [Official Geekbot API](https://geekbot.com/developers/)
- [geekbot-api-py](https://github.com/andrewthetechie/geekbot-api-py)

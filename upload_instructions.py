#!/usr/bin/env python3
"""
Upload script for notification-sound-windows package to PyPI.

This script provides instructions and commands for uploading the package to PyPI.
"""

print("""
=== Notification Sound Windows - PyPI Upload Instructions ===

Your package has been successfully built and is ready for upload!

Built files:
- notification_sound_windows-0.1.0-py3-none-any.whl
- notification_sound_windows-0.1.0.tar.gz

To upload to PyPI:

1. First, create accounts on PyPI and Test PyPI:
   - PyPI: https://pypi.org/account/register/
   - Test PyPI: https://test.pypi.org/account/register/

2. Generate API tokens:
   - PyPI: https://pypi.org/manage/account/#api-tokens
   - Test PyPI: https://test.pypi.org/manage/account/#api-tokens

3. Upload to Test PyPI first (recommended):
   python -m twine upload --repository testpypi dist/*
   
   When prompted for username, enter: __token__
   When prompted for password, enter your Test PyPI API token

4. Test installation from Test PyPI:
   pip install --index-url https://test.pypi.org/simple/ notification-sound-windows

5. If everything works, upload to PyPI:
   python -m twine upload dist/*
   
   When prompted for username, enter: __token__
   When prompted for password, enter your PyPI API token

6. Install from PyPI:
   pip install notification-sound-windows

Package Information:
- Name: notification-sound-windows
- Version: 0.1.0
- Description: Windows notification sound player for MCP servers

The package is now ready for distribution!
""")

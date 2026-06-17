from pathlib import Path

"""
Export the path to the Bootstrap templates directory.

The PATH variable can be used in the TEMPLATES setting of the Django project to
include the Bootstrap templates in the template search path.
"""

PATH = Path(__file__).resolve().parent

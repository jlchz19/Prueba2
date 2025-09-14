#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

print("Testing imports...")

try:
    from flask import Flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print(f"✗ Flask import failed: {e}")

try:
    from flask_sqlalchemy import SQLAlchemy
    print("✓ Flask-SQLAlchemy imported successfully")
except ImportError as e:
    print(f"✗ Flask-SQLAlchemy import failed: {e}")

try:
    from reportlab.lib.pagesizes import letter, A4
    print("✓ ReportLab imported successfully")
except ImportError as e:
    print(f"✗ ReportLab import failed: {e}")

try:
    from email.mime.text import MIMEText
    print("✓ Email modules imported successfully")
except ImportError as e:
    print(f"✗ Email modules import failed: {e}")

try:
    import pandas as pd
    print("✓ Pandas imported successfully")
except ImportError as e:
    print(f"✗ Pandas import failed: {e}")

print("\nImport test completed!")

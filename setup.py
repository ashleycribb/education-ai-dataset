#!/usr/bin/env python3
"""
Setup script for Education AI Dataset & AITA System
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_syntax():
    """Check syntax of all Python files"""
    print("🔄 Checking Python syntax...")
    python_files = list(Path('.').glob('**/*.py'))
    errors = []

    for file in python_files:
        if 'venv' in str(file) or '__pycache__' in str(file):
            continue
        try:
            subprocess.run([sys.executable, '-m', 'py_compile', str(file)],
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            errors.append(f"  {file}: {e.stderr.decode()}")

    if errors:
        print("❌ Syntax errors found:")
        for error in errors:
            print(error)
        return False
    else:
        print("✅ All Python files have valid syntax")
        return True

def install_dependencies():
    """Install Python dependencies"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False

    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def create_directories():
    """Create necessary directories"""
    directories = [
        'adapters/reading_explorer_pilot1',
        'adapters/eco_explorer_pilot1',
        'logs',
        'data/processed',
        'models'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Created necessary directories")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Education AI Dataset & AITA System")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check syntax
    if not check_syntax():
        print("\n⚠️  Syntax errors found. Please fix them before continuing.")
        sys.exit(1)

    # Create directories
    create_directories()

    # Install dependencies
    print("\n📦 Installing dependencies...")
    if install_dependencies():
        print("✅ Dependencies installed successfully")
    else:
        print("❌ Failed to install some dependencies")
        print("   You may need to install them manually:")
        print("   pip install -r requirements.txt")

    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Install Model Context Protocol if needed:")
    print("   # pip install modelcontextprotocol")
    print("\n2. Run the AITA service:")
    print("   python aita_interaction_service.py")
    print("\n3. Run the teacher dashboard:")
    print("   streamlit run teacher_dashboard_main.py")
    print("\n4. Run the student frontend:")
    print("   streamlit run student_frontend_streamlit.py")

    print("\n⚠️  Note: You'll need to provide model weights and adapters separately")

if __name__ == "__main__":
    main()
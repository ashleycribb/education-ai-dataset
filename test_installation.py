#!/usr/bin/env python3
"""
Test script to verify the Education AI Dataset installation
"""

import sys
import importlib
from pathlib import Path

def test_import(module_name, description=""):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} {description} - {e}")
        return False

def test_file_syntax(file_path):
    """Test if a Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            compile(f.read(), file_path, 'exec')
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Education AI Dataset Installation")
    print("=" * 50)
    
    # Test core dependencies
    print("\n📦 Testing Core Dependencies:")
    core_deps = [
        ("torch", "- PyTorch for ML models"),
        ("transformers", "- Hugging Face Transformers"),
        ("fastapi", "- FastAPI web framework"),
        ("streamlit", "- Streamlit for dashboards"),
        ("pandas", "- Data processing"),
        ("pydantic", "- Data validation"),
    ]
    
    core_success = 0
    for module, desc in core_deps:
        if test_import(module, desc):
            core_success += 1
    
    # Test optional dependencies
    print("\n📦 Testing Optional Dependencies:")
    optional_deps = [
        ("peft", "- Parameter Efficient Fine-Tuning"),
        ("datasets", "- Hugging Face Datasets"),
        ("trl", "- Transformer Reinforcement Learning"),
        ("accelerate", "- Model acceleration"),
        ("bs4", "- BeautifulSoup for web scraping"),
        ("requests", "- HTTP requests"),
    ]
    
    optional_success = 0
    for module, desc in optional_deps:
        if test_import(module, desc):
            optional_success += 1
    
    # Test MCP dependencies (likely to fail)
    print("\n📦 Testing MCP Dependencies (may fail):")
    mcp_deps = [
        ("modelcontextprotocol", "- Model Context Protocol"),
    ]
    
    mcp_success = 0
    for module, desc in mcp_deps:
        if test_import(module, desc):
            mcp_success += 1
    
    # Test main application files
    print("\n🐍 Testing Main Application Files:")
    main_files = [
        "aita_interaction_service.py",
        "model_loader_utils.py",
        "moderation_service.py",
        "dashboard_data_manager.py",
        "teacher_dashboard_main.py",
        "student_frontend_streamlit.py",
    ]
    
    syntax_success = 0
    for file_path in main_files:
        if Path(file_path).exists():
            if test_file_syntax(file_path):
                print(f"✅ {file_path} - syntax OK")
                syntax_success += 1
            else:
                print(f"❌ {file_path} - syntax error")
        else:
            print(f"❌ {file_path} - file not found")
    
    # Test SDK imports (without MCP)
    print("\n🔌 Testing SDK Modules (may have import issues):")
    try:
        sys.path.append('.')
        from k12_mcp_client_sdk.xapi_utils import create_interaction_xapi_statement
        print("✅ k12_mcp_client_sdk.xapi_utils - basic functions available")
        sdk_success = 1
    except ImportError:
        print("❌ k12_mcp_client_sdk - MCP dependencies missing")
        sdk_success = 0
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Core Dependencies: {core_success}/{len(core_deps)} ✅")
    print(f"Optional Dependencies: {optional_success}/{len(optional_deps)} ✅")
    print(f"MCP Dependencies: {mcp_success}/{len(mcp_deps)} ✅")
    print(f"Main Files Syntax: {syntax_success}/{len(main_files)} ✅")
    print(f"SDK Modules: {sdk_success}/1 ✅")
    
    total_tests = len(core_deps) + len(optional_deps) + len(mcp_deps) + len(main_files) + 1
    total_success = core_success + optional_success + mcp_success + syntax_success + sdk_success
    
    print(f"\nOverall: {total_success}/{total_tests} tests passed ({total_success/total_tests*100:.1f}%)")
    
    if core_success == len(core_deps) and syntax_success == len(main_files):
        print("\n🎉 Core functionality should work!")
        print("💡 Install missing optional dependencies as needed")
        if mcp_success == 0:
            print("⚠️  MCP functionality will be limited without modelcontextprotocol")
    else:
        print("\n⚠️  Some core components are missing or have issues")
        print("   Run: pip install -r requirements.txt")
    
    return total_success == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
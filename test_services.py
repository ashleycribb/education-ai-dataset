#!/usr/bin/env python3
"""
Test script to verify that the main services can initialize
"""

import sys
import os
from pathlib import Path

def test_fastapi_service():
    """Test if the FastAPI service can initialize"""
    print("🔄 Testing FastAPI service initialization...")
    try:
        # Import the service without running it
        import aita_interaction_service
        print("✅ FastAPI service imports successfully")

        # Check if the app object exists
        if hasattr(aita_interaction_service, 'app'):
            print("✅ FastAPI app object created")
            return True
        else:
            print("❌ FastAPI app object not found")
            return False
    except Exception as e:
        print(f"❌ FastAPI service failed to import: {e}")
        return False

def test_streamlit_dashboard():
    """Test if the Streamlit dashboard can be imported"""
    print("🔄 Testing Streamlit dashboard...")
    try:
        # Test teacher dashboard
        import teacher_dashboard_main
        print("✅ Teacher dashboard imports successfully")

        # Test student frontend
        import student_frontend_streamlit
        print("✅ Student frontend imports successfully")

        return True
    except Exception as e:
        print(f"❌ Streamlit components failed: {e}")
        return False

def test_model_utilities():
    """Test if model utilities work"""
    print("🔄 Testing model utilities...")
    try:
        from model_loader_utils import DefaultLogger, DummySLM

        # Test logger
        logger = DefaultLogger()
        logger.info("Test log message")
        print("✅ DefaultLogger works")

        # Test dummy model
        import torch
        device = torch.device("cpu")
        dummy_model = DummySLM(device=device, tokenizer=None)
        # Create dummy input tensor
        dummy_input = torch.tensor([[1, 2, 3]], dtype=torch.long)
        response = dummy_model.generate(dummy_input, max_new_tokens=10, eos_token_id=2, pad_token_id=0)
        print("✅ DummySLM works")

        return True
    except Exception as e:
        print(f"❌ Model utilities failed: {e}")
        return False

def test_data_manager():
    """Test if data manager works"""
    print("🔄 Testing data manager...")
    try:
        import dashboard_data_manager
        print("✅ Dashboard data manager imports successfully")
        return True
    except Exception as e:
        print(f"❌ Data manager failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Service Initialization")
    print("=" * 50)

    tests = [
        ("FastAPI Service", test_fastapi_service),
        ("Streamlit Dashboard", test_streamlit_dashboard),
        ("Model Utilities", test_model_utilities),
        ("Data Manager", test_data_manager),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("📊 Service Test Summary:")
    passed = sum(results)
    total = len(results)

    for i, (test_name, _) in enumerate(tests):
        status = "✅" if results[i] else "❌"
        print(f"{status} {test_name}")

    print(f"\nOverall: {passed}/{total} services working ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All services can initialize successfully!")
        print("💡 You can now try running the services:")
        print("   python aita_interaction_service.py")
        print("   streamlit run teacher_dashboard_main.py")
        print("   streamlit run student_frontend_streamlit.py")
    else:
        print("\n⚠️  Some services have initialization issues")
        print("   Check the error messages above for details")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
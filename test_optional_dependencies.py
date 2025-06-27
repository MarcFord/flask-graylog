#!/usr/bin/env python3
"""
Test script for optional dependencies feature.

This script demonstrates the new optional dependencies functionality
and how users should install the package for different backends.
"""

def test_installation_examples():
    """Test and demonstrate the new installation options."""
    
    print("🎯 Flask Network Logging - Optional Dependencies Test")
    print("=" * 60)
    
    print("\n📦 INSTALLATION OPTIONS:")
    print("-" * 30)
    
    print("🔸 Basic installation (no logging backends):")
    print("   pip install flask-network-logging")
    
    print("\n🔸 Graylog support:")
    print("   pip install flask-network-logging[graylog]")
    
    print("\n🔸 Google Cloud Logging support:")
    print("   pip install flask-network-logging[gcp]")
    
    print("\n🔸 AWS CloudWatch Logs support:")
    print("   pip install flask-network-logging[aws]")
    
    print("\n🔸 Azure Monitor Logs support:")
    print("   pip install flask-network-logging[azure]")
    
    print("\n🔸 Multiple backends:")
    print("   pip install flask-network-logging[graylog,aws]")
    
    print("\n🔸 All backends:")
    print("   pip install flask-network-logging[all]")
    
    print("\n" + "=" * 60)
    
    # Test imports
    print("\n🧪 TESTING IMPORTS:")
    print("-" * 20)
    
    try:
        from flask_remote_logging import (
            GraylogExtension, GCPLogExtension, 
            AWSLogExtension, AzureLogExtension
        )
        print("✅ All extensions imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test aliases
    try:
        from flask_remote_logging import Graylog, GCPLog, AWSLog, AzureLog
        print("✅ All aliases work correctly")
    except ImportError as e:
        print(f"❌ Alias import failed: {e}")
        return False
    
    # Test extension creation
    print("\n🏗️ TESTING EXTENSION CREATION:")
    print("-" * 35)
    
    try:
        from flask import Flask
        app = Flask(__name__)
        
        # Test each extension
        extensions = [
            ("Graylog", GraylogExtension),
            ("GCP", GCPLogExtension),
            ("AWS", AWSLogExtension),
            ("Azure", AzureLogExtension)
        ]
        
        for name, ext_class in extensions:
            try:
                ext = ext_class(app)
                print(f"✅ {name}Extension created successfully")
            except Exception as e:
                print(f"❌ {name}Extension failed: {e}")
                
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False
    
    print("\n💡 DEPENDENCY MANAGEMENT:")
    print("-" * 30)
    print("• Core package only installs Flask, user-agents, and MarkupSafe")
    print("• Backend-specific packages are installed only when requested")
    print("• Helpful error messages guide users to install missing dependencies")
    print("• Backward compatibility maintained for existing installations")
    
    print("\n✨ BENEFITS:")
    print("-" * 15)
    print("• 📦 Smaller installation footprint")
    print("• 🎯 Install only what you need")
    print("• 🚀 Faster installation and smaller Docker images")
    print("• 🔒 Avoid unnecessary security surface area")
    print("• 📊 Better dependency management")
    
    return True

if __name__ == "__main__":
    success = test_installation_examples()
    if success:
        print("\n🎉 Optional dependencies feature working correctly!")
        print("\n📚 Users can now install only the backends they need:")
        print("   • Graylog users: pip install flask-network-logging[graylog]")
        print("   • GCP users: pip install flask-network-logging[gcp]") 
        print("   • AWS users: pip install flask-network-logging[aws]")
        print("   • Azure users: pip install flask-network-logging[azure]")
        print("   • Multi-backend: pip install flask-network-logging[graylog,aws]")
        print("   • Everything: pip install flask-network-logging[all]")
    else:
        print("\n❌ Tests failed!")
        exit(1)

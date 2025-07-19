#!/usr/bin/env python3

"""
Simple test to verify our configuration changes
"""

def test_lm_studio_config():
    """Test that LM Studio configuration is correct"""
    
    # Test 1: Check if config.py has correct defaults
    with open('config/config.py', 'r') as f:
        config_content = f.read()
        
    # Check LM Studio is default provider
    assert 'LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "lmstudio")' in config_content
    print("✅ LM Studio is now the default LLM provider")
    
    # Check LM Studio uses correct IP
    assert 'LMSTUDIO_API_BASE = os.environ.get("LMSTUDIO_API_BASE", "http://192.168.1.98:1234/v1")' in config_content
    print("✅ LM Studio default URL updated to 192.168.1.98:1234/v1")
    
    # Test 2: Check if API presets are ordered correctly
    with open('app/api/llm_providers.py', 'r') as f:
        api_content = f.read()
    
    # Find the presets array
    start_idx = api_content.find('presets = [')
    end_idx = api_content.find(']', start_idx)
    presets_section = api_content[start_idx:end_idx]
    
    # Check that LMStudio preset comes first
    lmstudio_idx = presets_section.find('"provider": "lmstudio"')
    openai_idx = presets_section.find('"provider": "openai"')
    
    assert lmstudio_idx < openai_idx, "LMStudio preset should be listed first"
    print("✅ LM Studio preset is listed first in API")
    
    # Check LMStudio preset uses correct URL
    assert 'http://192.168.1.98:1234/v1' in presets_section
    print("✅ LM Studio preset uses correct URL")

def test_login_flow_changes():
    """Test that login flow changes are implemented"""
    
    with open('frontend/src/App.tsx', 'r') as f:
        app_content = f.read()
    
    # Check that PostAuthProof is only shown on URL parameter
    assert 'urlParams.get(\'health\') === \'true\'' in app_content
    print("✅ PostAuthProof is only shown when health parameter is present")
    
    # Check that login doesn't set sessionStorage flag
    assert 'sessionStorage.setItem(\'just_logged_in\', \'true\')' not in app_content
    print("✅ Login no longer forces health check")

def test_ui_modernization():
    """Test that UI has been modernized"""
    
    with open('frontend/tailwind.config.js', 'r') as f:
        tailwind_content = f.read()
    
    # Check for new color palette
    assert 'neutral:' in tailwind_content
    assert 'accent:' in tailwind_content
    print("✅ Modern color palette (neutral/accent) added")
    
    with open('frontend/src/index.css', 'r') as f:
        css_content = f.read()
    
    # Check for Inter font
    assert 'Inter' in css_content
    print("✅ Inter font added for modern typography")
    
    # Check for improved focus styles
    assert 'focus-visible' in css_content
    print("✅ Improved focus styles implemented")

def test_main_layout_changes():
    """Test that main layout includes health status menu"""
    
    with open('frontend/src/components/layout/MainLayout.tsx', 'r') as f:
        layout_content = f.read()
    
    # Check for health status menu item
    assert 'Health Status' in layout_content
    assert 'HeartIcon' in layout_content
    print("✅ Health Status menu item added")
    
    # Check that health view is handled
    assert "activeView === 'health'" in layout_content
    print("✅ Health view properly routed in main layout")

if __name__ == "__main__":
    print("🔍 Testing BigShot UI Overhaul changes...\n")
    
    try:
        test_lm_studio_config()
        print()
        test_login_flow_changes()
        print()
        test_ui_modernization()
        print()
        test_main_layout_changes()
        
        print("\n🎉 All tests passed! UI Overhaul implementation is correct.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
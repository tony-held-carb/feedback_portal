#!/usr/bin/env python3
"""
Test script to verify Unicode handling fixes work correctly.
"""

def test_unicode_print():
    """Test that Unicode characters can be printed safely."""
    
    # Test cases with Unicode characters that were causing issues
    test_cases = [
        "✅ Playwright setup is working correctly!",
        "❌ Unknown browser: chromium",
        "🎉 Playwright migration completed successfully!",
        "⚠️ Important: Please close any files before uploading",
        "📋 Clipboard content",
        "📄 Document content",
        "📝 Notes content"
    ]
    
    print("Testing Unicode print handling...")
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"Test {i}: {test_case}")
        except UnicodeEncodeError:
            safe_text = test_case.encode('ascii', 'replace').decode('ascii')
            print(f"Test {i}: {safe_text} (encoded safely)")
    
    print("Unicode test completed!")

if __name__ == "__main__":
    test_unicode_print() 
#!/usr/bin/env python3
"""
Script to verify spaCy model installation and functionality
Run this during Docker build to ensure models are properly installed
"""

import sys
import spacy
import logging

def verify_spacy_model(model_name: str = "en_core_web_sm") -> bool:
    """Verify spaCy model is properly installed and functional"""
    try:
        print(f"Loading spaCy model: {model_name}")
        nlp = spacy.load(model_name)
        
        # Test with sample text
        test_text = "This is a test document for spaCy model verification."
        doc = nlp(test_text)
        
        # Basic checks
        assert len(doc) > 0, "Document processing failed"
        assert doc[0].text == "This", "Token extraction failed"
        
        # Check if model has required components
        components = nlp.pipe_names
        print(f"Model components: {components}")
        
        # Test spaCy Layout compatibility
        try:
            from spacy_layout import spaCyLayout
            layout = spaCyLayout(nlp)
            print("spaCy Layout integration successful")
        except Exception as e:
            print(f"Warning: spaCy Layout integration failed: {e}")
            return False
        
        print(f"✓ spaCy model '{model_name}' verified successfully")
        return True
        
    except Exception as e:
        print(f"✗ spaCy model verification failed: {e}")
        return False

if __name__ == "__main__":
    model_name = sys.argv[1] if len(sys.argv) > 1 else "en_core_web_sm"
    success = verify_spacy_model(model_name)
    sys.exit(0 if success else 1)

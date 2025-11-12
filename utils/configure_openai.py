#!/usr/bin/env python3
"""
Simple script to configure OpenAI API key for the resume builder.
"""

import os
from pathlib import Path

def configure_openai():
    """Interactive configuration for OpenAI API key."""
    print("🎖️ Operation MOS - OpenAI Configuration")
    print("=" * 50)
    print()
    
    env_file = Path(".env")
    
    # Read existing .env if it exists
    existing_config = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_config[key.strip()] = value.strip()
    
    print("Current configuration:")
    print(f"  AI Provider: {existing_config.get('AI_PROVIDER', 'mock')}")
    print(f"  AI Model: {existing_config.get('AI_MODEL', 'gpt-4o-mini')}")
    
    current_key = existing_config.get('OPENAI_API_KEY', '')
    if current_key and current_key != 'your_openai_api_key_here':
        masked_key = current_key[:7] + '...' + current_key[-4:] if len(current_key) > 20 else '***'
        print(f"  API Key: {masked_key} (configured)")
    else:
        print(f"  API Key: Not configured")
    
    print()
    print("To use OpenAI's GPT models for better AI-generated content:")
    print("  1. Get your API key from: https://platform.openai.com/api-keys")
    print("  2. Enter it below (or press Enter to skip)")
    print()
    
    api_key = input("Enter your OpenAI API key (or press Enter to use mock AI): ").strip()
    
    if api_key:
        # Update configuration
        existing_config['OPENAI_API_KEY'] = api_key
        existing_config['AI_PROVIDER'] = 'openai'
        existing_config['AI_MODEL'] = existing_config.get('AI_MODEL', 'gpt-4o-mini')
        
        # Write .env file
        with open(env_file, 'w') as f:
            f.write("# AI Configuration\n")
            f.write(f"OPENAI_API_KEY={existing_config['OPENAI_API_KEY']}\n")
            f.write(f"AI_PROVIDER={existing_config['AI_PROVIDER']}\n")
            f.write(f"AI_MODEL={existing_config['AI_MODEL']}\n")
            f.write("\n# Application Settings\n")
            f.write(f"LOG_LEVEL={existing_config.get('LOG_LEVEL', 'INFO')}\n")
            f.write(f"REDACT_PII={existing_config.get('REDACT_PII', 'True')}\n")
        
        print()
        print("✅ Configuration saved!")
        print(f"   Provider: openai")
        print(f"   Model: {existing_config['AI_MODEL']}")
        print()
        print("Testing OpenAI connection...")
        
        # Test the configuration
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
                max_tokens=5
            )
            print("✅ OpenAI connection successful!")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify OpenAI connection: {e}")
            print("   Please check your API key and try again.")
    else:
        # Configure for mock AI
        existing_config['AI_PROVIDER'] = 'mock'
        
        with open(env_file, 'w') as f:
            f.write("# AI Configuration\n")
            f.write(f"OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write(f"AI_PROVIDER=mock\n")
            f.write(f"AI_MODEL=gpt-4o-mini\n")
            f.write("\n# Application Settings\n")
            f.write(f"LOG_LEVEL={existing_config.get('LOG_LEVEL', 'INFO')}\n")
            f.write(f"REDACT_PII={existing_config.get('REDACT_PII', 'True')}\n")
        
        print()
        print("✅ Configuration saved!")
        print("   Provider: mock (template-based AI)")
        print("   You can configure OpenAI later by running this script again.")
    
    print()
    print("You can now start the application with: bash start_streamlit.sh")

if __name__ == "__main__":
    configure_openai()

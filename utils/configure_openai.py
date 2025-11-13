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
    # First check environment variables and (if available) Streamlit secrets
    env_api_key = os.getenv('OPENAI_API_KEY') or os.getenv('openai_api_key')
    env_ai_provider = os.getenv('AI_PROVIDER') or os.getenv('ai_provider')
    env_ai_model = os.getenv('AI_MODEL') or os.getenv('ai_model')

    # Try to read Streamlit secrets if running in that environment
    st_secrets = {}
    try:
        import streamlit as _st

        # st.secrets behaves like a dict
        st_secrets = _st.secrets or {}
    except Exception:
        st_secrets = {}

    secrets_api_key = st_secrets.get('OPENAI_API_KEY') or st_secrets.get('openai_api_key')
    secrets_ai_provider = st_secrets.get('AI_PROVIDER') or st_secrets.get('ai_provider')
    secrets_ai_model = st_secrets.get('AI_MODEL') or st_secrets.get('ai_model')

    # Prefer explicit environment variables, then Streamlit secrets, then existing .env
    api_key = env_api_key or secrets_api_key or existing_config.get('OPENAI_API_KEY', '')
    ai_provider = env_ai_provider or secrets_ai_provider or existing_config.get('AI_PROVIDER', 'mock')
    ai_model = env_ai_model or secrets_ai_model or existing_config.get('AI_MODEL', 'gpt-4o-mini')

    # If configuration is available from env/secrets, show and exit (non-interactive)
    if api_key or ai_provider:
        # Update existing_config with detected values so calling code can persist if desired
        existing_config['OPENAI_API_KEY'] = api_key or existing_config.get('OPENAI_API_KEY', 'your_openai_api_key_here')
        existing_config['AI_PROVIDER'] = ai_provider or existing_config.get('AI_PROVIDER', 'mock')
        existing_config['AI_MODEL'] = ai_model or existing_config.get('AI_MODEL', 'gpt-4o-mini')

        print('\nDetected configuration from environment / Streamlit secrets:')
        print(f"  AI Provider: {existing_config.get('AI_PROVIDER')}")
        print(f"  AI Model: {existing_config.get('AI_MODEL')}")
        if existing_config.get('OPENAI_API_KEY') and existing_config.get('OPENAI_API_KEY') != 'your_openai_api_key_here':
            masked_key = existing_config['OPENAI_API_KEY'][:7] + '...' + existing_config['OPENAI_API_KEY'][-4:] if len(existing_config['OPENAI_API_KEY']) > 20 else '***'
            print(f"  API Key: {masked_key} (from env/secrets)")
        else:
            print("  API Key: Not configured")

        print('\nNo interactive prompt because configuration was detected. If you want to re-run the interactive setup, unset relevant env vars or remove secrets and run this script locally.')
        return

    # Fallback to interactive prompt when no environment/secrets detected
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
            f.write(f"REDACT_PII={existing_config.get('REDACT_PII', 'False')}\n")
        
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
            f.write(f"REDACT_PII={existing_config.get('REDACT_PII', 'False')}\n")
        
        print()
        print("✅ Configuration saved!")
        print("   Provider: mock (template-based AI)")
        print("   You can configure OpenAI later by running this script again.")
    
    print()
    print("You can now start the application with: bash start_streamlit.sh")

if __name__ == "__main__":
    configure_openai()

# OpenAI API Key Setup Guide

## Quick Setup

To use case generation, you need to configure your OpenAI API key. Here are three ways to do it:

## Option 1: Using .env File (Recommended)

1. Create a `.env` file in the project root directory:
   ```
   C:\Users\liyic\OneDrive\Desktop\MGT 802 LLM\mgt-802\.env
   ```

2. Add the following line to the `.env` file:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. Restart the Django development server

## Option 2: Environment Variable (Windows)

1. Open PowerShell as Administrator
2. Set the environment variable:
   ```powershell
   [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
   ```
3. Restart your terminal and Django server

## Option 3: Environment Variable (Temporary - Current Session Only)

In your current PowerShell terminal:
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
python manage.py runserver
```

## Getting Your API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)
5. **Important**: Save it immediately - you won't be able to see it again!

## Verify Setup

After setting up, try generating a case. If you see an error, check:
- The API key is correct (starts with `sk-`)
- The `.env` file is in the project root
- You've restarted the Django server after adding the key

## Security Notes

- **Never commit your `.env` file to Git** (it's already in `.gitignore`)
- Don't share your API key publicly
- The `.env` file should only contain your local development keys

## Troubleshooting

### "OPENAI_API_KEY not found" Error

1. Check that the `.env` file exists in the project root
2. Verify the key is on a single line: `OPENAI_API_KEY=sk-...`
3. Make sure there are no extra spaces or quotes
4. Restart the Django server

### "Invalid API Key" Error

1. Verify your key is correct
2. Check your OpenAI account has credits
3. Ensure the key hasn't been revoked

### Still Having Issues?

Check the Django console output for detailed error messages. The error will show exactly what's missing.


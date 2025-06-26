# Claude Code Conversation Analysis Pipeline

A tool to systematically analyze Claude Code conversation logs and generate intelligent summaries.

## Usage

Run the Python script to process all conversations:
```bash
python conversation_summarizer.py
```

## Structure

- **conversation_summarizer.py** - Main processing script
- **summaries/** - Generated markdown summaries (gitignored)
- **processed_conversations.json** - Tracking file (gitignored)

## Output

The script reads JSONL conversation files from `/Users/vladgheorghe/.claude/projects/` and creates:
- Individual summary files in `summaries/`
- Comprehensive analysis of tasks completed and Claude Code tools used
- Tracking to avoid reprocessing conversations
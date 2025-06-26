---
title: "Analyze Claude Code Conversations"
description: "Systematically analyze all Claude Code conversation logs and generate intelligent summaries"
version: "2.0"
author: "Claude Code Generic Pipeline"
---

# Analyze Claude Code Conversations

You are tasked with analyzing Claude Code conversation history to create comprehensive summaries of what was accomplished and how Claude Code helped.

## Your Mission

Systematically process ALL conversations in the user's Claude projects directory and generate intelligent summaries focusing on:

1. **What specific tasks were completed**
2. **What problems were solved** 
3. **How Claude Code's tools and capabilities were used**
4. **The overall outcome/value delivered**

## Step-by-Step Process

### 1. Initial Setup
```bash
# First, detect the Claude projects directory dynamically
CLAUDE_PROJECTS_DIR="$HOME/.claude/projects"
if [ ! -d "$CLAUDE_PROJECTS_DIR" ]; then
  # Try alternative common locations
  CLAUDE_PROJECTS_DIR="$HOME/.config/claude/projects"
  if [ ! -d "$CLAUDE_PROJECTS_DIR" ]; then
    echo "Please specify your Claude projects directory location"
    exit 1
  fi
fi

# Explore the full directory structure
ls -la "$CLAUDE_PROJECTS_DIR"
```

### 2. Initialize Tracking
Create `processed_conversations.json` to track which conversations you've analyzed:
```json
[]
```

### 3. Use Task Agents for Batch Processing
**CRITICAL:** Don't process conversations one-by-one. Use Task agents to handle entire projects:

```
Task(
  description="Analyze [PROJECT-NAME] conversations", 
  prompt="Read and analyze ALL conversation files in the specified project directory and create intelligent summaries.

  For EACH conversation file (.jsonl), provide:
  - Project context and goals
  - Specific tasks completed
  - Problems solved  
  - Claude Code tools used
  - Value delivered

  Files to analyze: [LIST ALL .jsonl FILES FOUND IN THE PROJECT]
  
  This is critical - analyze EVERY conversation file, not just summaries."
)
```

### 4. Process in Logical Batches

Group projects by complexity and type:

**Batch 1: Major Projects (typically 5+ conversations each)**
- Identify projects with the most conversation files
- These are usually core development projects or long-term initiatives

**Batch 2: Development Tools (typically 2-4 conversations each)**
- Projects related to development tooling, automation, or infrastructure
- Build systems, deployment tools, testing frameworks

**Batch 3: Experimental/Sandbox Projects (typically 1-3 conversations each)**
- Projects with "sandbox", "test", "experiment" in the name
- Proof of concept and exploratory work

**Batch 4: Miscellaneous Projects (variable conversation count)**
- Repository management and setup projects
- One-off utilities and scripts
- Documentation and configuration projects

### 5. Create Summary Files

For each project/batch, create `summary_[project-name].md` with this structure:

```markdown
# [Project Name]: Claude Code Conversation Analysis

## Overview
[Brief project description based on conversation content]

## Individual Conversation Summaries

### Conversation N: [Generated Title Based on Content]
**File:** `[conversation-id].jsonl`

**Tasks Completed:**
- [Specific accomplishment 1]
- [Specific accomplishment 2]

**Problems Solved:**
- [Problem and solution description]

**Claude Code Tools Used:**
- [Tool]: [How it was used and impact]
- [Tool]: [How it was used and impact]

**Value Delivered:**
[Quantifiable impact and benefits]

## Overall Project Impact
[High-level value summary across all conversations]
```

### 6. Update Tracking After Each Batch

After processing each batch, update `processed_conversations.json` with full paths:
```json
[
  "[CLAUDE_PROJECTS_DIR]/[project-dir]/[file1].jsonl",
  "[CLAUDE_PROJECTS_DIR]/[project-dir]/[file2].jsonl"
]
```

### 7. Quality Control

Ensure complete coverage:
- Count total conversations across all project directories
- Count entries in tracking file
- Verify numbers match
- Check for any missed or empty project directories

## Dynamic Success Criteria

✅ **Complete Coverage:** All conversations in the projects directory analyzed  
✅ **Intelligent Analysis:** Focus on business value, not just tool usage  
✅ **Systematic Tracking:** Every conversation file recorded with full path  
✅ **Structured Output:** Summary files for all project groups  
✅ **Replicable Process:** Works for any user's Claude projects directory  

## Estimated Time Investment
- Setup and discovery: 10-20 minutes
- Batch processing: 15-60 minutes (depends on conversation volume)  
- Quality control: 10-15 minutes
- **Total: Varies based on conversation volume (typically 35-95 minutes)**

## Critical Success Patterns

**DO:**
- Use Task agents for batch processing (group 15-30 conversations per agent)
- Focus on what was accomplished and value delivered
- Track at the individual conversation file level
- Process in logical project groupings based on discovered structure
- Dynamically adapt to the user's actual project structure

**DON'T:**
- Process conversations individually 
- Only extract metadata/basic statistics
- Make assumptions about project names or structure
- Process randomly without understanding the project relationships

## Dynamic Path Detection

The script will automatically:
1. Check `$HOME/.claude/projects` first (most common location)
2. Fall back to `$HOME/.config/claude/projects` if needed
3. Prompt user for custom location if neither exists
4. Adapt all subsequent processing to the discovered path

---

$ARGUMENTS

Begin with: "I'll analyze your Claude Code conversation history systematically. Let me start by discovering your Claude projects directory and exploring the structure."
#!/usr/bin/env python3
"""
Claude Code Conversation Summarizer

This script processes Claude Code conversation logs (.jsonl files) and creates
summaries focusing on what was accomplished and how Claude Code helped.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re
from datetime import datetime

class ConversationSummarizer:
    def __init__(self, projects_dir: str, output_dir: str):
        self.projects_dir = Path(projects_dir)
        self.output_dir = Path(output_dir)
        self.processed_file = self.output_dir / "processed_conversations.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Load processed conversations list
        self.processed = self._load_processed()
    
    def _load_processed(self) -> List[str]:
        """Load list of already processed conversation files."""
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_processed(self):
        """Save updated list of processed conversations."""
        with open(self.processed_file, 'w') as f:
            json.dump(self.processed, f, indent=2)
    
    def _parse_jsonl_conversation(self, file_path: Path) -> Dict[str, Any]:
        """Parse a JSONL conversation file and extract key information."""
        messages = []
        project_path = ""
        summary_title = ""
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        
                        # Extract summary title if present
                        if entry.get("type") == "summary":
                            summary_title = entry.get("summary", "")
                        
                        # Extract project path from first user message
                        if entry.get("type") == "user" and not project_path:
                            project_path = entry.get("cwd", "")
                        
                        # Extract messages
                        if "message" in entry:
                            msg = entry["message"]
                            if msg.get("role") in ["user", "assistant"]:
                                content = ""
                                if isinstance(msg.get("content"), str):
                                    content = msg["content"]
                                elif isinstance(msg.get("content"), list):
                                    # Handle structured content (text + tool_use)
                                    text_parts = []
                                    for part in msg["content"]:
                                        if part.get("type") == "text":
                                            text_parts.append(part.get("text", ""))
                                        elif part.get("type") == "tool_use":
                                            # Extract tool usage info
                                            tool_name = part.get("name", "")
                                            if tool_name:
                                                text_parts.append(f"[Used {tool_name} tool]")
                                    content = " ".join(text_parts)
                                
                                messages.append({
                                    "role": msg["role"],
                                    "content": content,
                                    "timestamp": entry.get("timestamp", "")
                                })
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return {}
        
        return {
            "file_path": str(file_path),
            "project_path": project_path,
            "summary_title": summary_title,
            "messages": messages,
            "message_count": len(messages)
        }
    
    def _extract_project_name(self, project_path: str) -> str:
        """Extract a clean project name from the project path."""
        if not project_path:
            return "Unknown Project"
        
        # Remove common prefixes and get the last meaningful part
        path_parts = project_path.strip("/").split("/")
        if path_parts:
            project_name = path_parts[-1]
            # Clean up common prefixes/suffixes
            project_name = project_name.replace("-", " ").replace("_", " ")
            return project_name.title()
        
        return "Unknown Project"
    
    def _identify_accomplishments(self, messages: List[Dict]) -> List[str]:
        """Identify what was accomplished based on conversation messages."""
        accomplishments = []
        
        # Keywords that indicate completion or success
        success_patterns = [
            r"completed|finished|done|successful|working|fixed|implemented|created|built|deployed",
            r"installed|configured|set up|established|generated|processed",
            r"saved|committed|pushed|merged|updated|modified|improved"
        ]
        
        # Tool usage patterns that indicate work being done
        tool_patterns = [
            r"\[Used (\w+) tool\]",
            r"running|executing|creating|writing|editing|reading|searching"
        ]
        
        for msg in messages:
            if msg["role"] == "assistant":
                content = msg["content"].lower()
                
                # Look for completion indicators
                for pattern in success_patterns:
                    if re.search(pattern, content):
                        # Extract the sentence containing the accomplishment
                        sentences = content.split(".")
                        for sentence in sentences:
                            if re.search(pattern, sentence):
                                accomplishments.append(sentence.strip().capitalize())
                                break
        
        # Remove duplicates and empty strings
        accomplishments = list(set([acc for acc in accomplishments if acc]))
        
        return accomplishments[:5]  # Limit to top 5 accomplishments
    
    def _identify_claude_code_help(self, messages: List[Dict]) -> List[str]:
        """Identify how Claude Code specifically helped."""
        help_provided = []
        
        # Tool usage tracking
        tools_used = set()
        for msg in messages:
            if msg["role"] == "assistant":
                tool_matches = re.findall(r"\[Used (\w+) tool\]", msg["content"])
                tools_used.update(tool_matches)
        
        if tools_used:
            help_provided.append(f"Used {len(tools_used)} different tools: {', '.join(sorted(tools_used))}")
        
        # Analysis of first user message to understand the initial ask
        if messages:
            first_user_msg = next((msg for msg in messages if msg["role"] == "user"), None)
            if first_user_msg:
                content = first_user_msg["content"].lower()
                if "help" in content or "create" in content or "build" in content:
                    help_provided.append("Provided step-by-step assistance with implementation")
                if "debug" in content or "fix" in content or "error" in content:
                    help_provided.append("Helped debug and fix issues")
                if "setup" in content or "configure" in content:
                    help_provided.append("Assisted with setup and configuration")
        
        # Count assistant responses to gauge interaction level
        assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
        if len(assistant_messages) > 10:
            help_provided.append("Provided extensive interactive assistance")
        elif len(assistant_messages) > 5:
            help_provided.append("Provided detailed guidance and support")
        
        return help_provided
    
    def _generate_summary(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the conversation."""
        if not conversation_data or not conversation_data.get("messages"):
            return {}
        
        project_name = self._extract_project_name(conversation_data["project_path"])
        accomplishments = self._identify_accomplishments(conversation_data["messages"])
        claude_help = self._identify_claude_code_help(conversation_data["messages"])
        
        # Get conversation metadata
        first_msg = conversation_data["messages"][0] if conversation_data["messages"] else {}
        last_msg = conversation_data["messages"][-1] if conversation_data["messages"] else {}
        
        summary = {
            "project_name": project_name,
            "project_path": conversation_data["project_path"],
            "conversation_file": conversation_data["file_path"],
            "summary_title": conversation_data.get("summary_title", ""),
            "message_count": conversation_data["message_count"],
            "accomplishments": accomplishments,
            "claude_code_help": claude_help,
            "timestamp_start": first_msg.get("timestamp", ""),
            "timestamp_end": last_msg.get("timestamp", ""),
            "generated_at": datetime.now().isoformat()
        }
        
        return summary
    
    def process_all_conversations(self):
        """Process all conversations in the projects directory."""
        summaries = []
        
        # Walk through all project directories
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            print(f"Processing project: {project_dir.name}")
            
            # Process each JSONL file in the project directory
            for jsonl_file in project_dir.glob("*.jsonl"):
                file_path_str = str(jsonl_file)
                
                # Skip if already processed
                if file_path_str in self.processed:
                    print(f"  Skipping already processed: {jsonl_file.name}")
                    continue
                
                print(f"  Processing: {jsonl_file.name}")
                
                # Parse the conversation
                conversation_data = self._parse_jsonl_conversation(jsonl_file)
                
                if conversation_data and conversation_data.get("messages"):
                    # Generate summary
                    summary = self._generate_summary(conversation_data)
                    
                    if summary:
                        summaries.append(summary)
                        
                        # Save individual summary
                        summary_filename = f"summary_{jsonl_file.stem}.json"
                        summary_path = self.output_dir / summary_filename
                        
                        with open(summary_path, 'w') as f:
                            json.dump(summary, f, indent=2)
                        
                        print(f"    Saved summary: {summary_filename}")
                
                # Mark as processed
                self.processed.append(file_path_str)
        
        # Save updated processed list
        self._save_processed()
        
        # Save all summaries in one file
        all_summaries_path = self.output_dir / "all_summaries.json"
        with open(all_summaries_path, 'w') as f:
            json.dump(summaries, f, indent=2)
        
        print(f"\nProcessed {len(summaries)} new conversations")
        print(f"All summaries saved to: {all_summaries_path}")
        
        return summaries

def main():
    projects_dir = "/Users/vladgheorghe/.claude/projects"
    output_dir = "/Users/vladgheorghe/code/claude-code-summaries/summaries"
    
    summarizer = ConversationSummarizer(projects_dir, output_dir)
    summaries = summarizer.process_all_conversations()
    
    # Print a brief report
    print(f"\n=== SUMMARY REPORT ===")
    print(f"Total conversations processed: {len(summaries)}")
    
    if summaries:
        projects = set(s["project_name"] for s in summaries)
        print(f"Projects involved: {len(projects)}")
        
        print(f"\nProjects:")
        for project in sorted(projects):
            count = len([s for s in summaries if s["project_name"] == project])
            print(f"  - {project}: {count} conversation(s)")

if __name__ == "__main__":
    main()
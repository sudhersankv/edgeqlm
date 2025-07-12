"""
Command Generator Module
Handles qlm CLI with sessionless and context-aware modes
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
import pyperclip

import config
from src.utils import setup_logger, truncate_text

logger = setup_logger(__name__)


class CommandSession:
    """Represents a command generation session with context"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.context_entries = []
        self.working_directory = os.getcwd()
        self.environment_info = self._get_environment_info()
        
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get current environment information"""
        return {
            'pwd': self.working_directory,
            'platform': sys.platform,
            'shell': os.environ.get('SHELL', os.environ.get('COMSPEC', 'unknown')),
            'user': os.environ.get('USER', os.environ.get('USERNAME', 'unknown')),
            'path': os.environ.get('PATH', '').split(os.pathsep)[:5],  # First 5 path entries
        }
    
    def add_context_entry(self, prompt: str, generated_command: str, success: bool = True):
        """Add a context entry to the session"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'generated_command': generated_command,
            'success': success,
            'working_directory': os.getcwd()
        }
        
        self.context_entries.append(entry)
        self.last_used = datetime.now()
        
        # Keep only recent entries
        if len(self.context_entries) > config.QLM_CONTEXT_MAX_ENTRIES:
            self.context_entries = self.context_entries[-config.QLM_CONTEXT_MAX_ENTRIES:]
    
    def get_context_summary(self) -> str:
        """Get a summary of recent context for the LLM"""
        if not self.context_entries:
            return ""
        
        recent_entries = self.context_entries[-10:]  # Last 10 entries
        
        context_parts = [
            f"Session Context (Working Directory: {self.working_directory}):",
            f"Platform: {self.environment_info['platform']}, Shell: {self.environment_info['shell']}",
            "\nRecent Commands:"
        ]
        
        for entry in recent_entries:
            context_parts.append(f"- Prompt: {truncate_text(entry['prompt'], 80)}")
            context_parts.append(f"  Generated: {truncate_text(entry['generated_command'], 80)}")
            context_parts.append(f"  Directory: {entry['working_directory']}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        expiry_time = self.last_used + timedelta(seconds=config.QLM_SESSION_TIMEOUT)
        return datetime.now() > expiry_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat(),
            'context_entries': self.context_entries,
            'working_directory': self.working_directory,
            'environment_info': self.environment_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandSession':
        """Create session from dictionary"""
        session = cls(data['session_id'])
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.last_used = datetime.fromisoformat(data['last_used'])
        session.context_entries = data['context_entries']
        session.working_directory = data['working_directory']
        session.environment_info = data['environment_info']
        return session


class CommandGenerator:
    """Handles command generation using Ollama"""
    
    def __init__(self):
        self.sessions: Dict[str, CommandSession] = {}
        self.current_session_id = None
        self.sessions_file = config.DATA_DIR / "command_sessions.json"
        
        # Load existing sessions
        self.load_sessions()
    
    def generate_command(self, prompt: str, use_context: bool = False) -> str:
        """Generate a command based on the prompt"""
        try:
            # Build the full prompt
            full_prompt = self._build_prompt(prompt, use_context)
            
            # Call Ollama API
            response = self._call_ollama(full_prompt)
            
            if response:
                # Extract command from response
                command = self._extract_command(response)
                
                # Add to session context if using context
                if use_context and self.current_session_id:
                    session = self.get_or_create_session(self.current_session_id)
                    session.add_context_entry(prompt, command)
                    self.save_sessions()
                
                return command
            else:
                return "# Error: Failed to generate command"
                
        except Exception as e:
            logger.error(f"Error generating command: {e}")
            return f"# Error: {str(e)}"
    
    def _build_prompt(self, user_prompt: str, use_context: bool = False) -> str:
        """Build the full prompt for the LLM"""
        system_prompt = """You are a coding assistant that generates shell commands, git commands, and EDA tool commands.

Your task is to generate ONLY the command(s) that would accomplish the user's request. Do not include explanations, comments, or additional text unless specifically asked.

Guidelines:
1. Generate practical, executable commands
2. Use common command-line tools and EDA tools
3. For multi-step operations, separate commands with newlines
4. Include necessary flags and options
5. Use appropriate file paths and extensions
6. For EDA tools, assume common tools like VCS, Quartus, Vivado, etc.

Format your response as the raw command(s) only."""

        context_info = ""
        if use_context and self.current_session_id:
            session = self.get_or_create_session(self.current_session_id)
            context_info = session.get_context_summary()
        
        # Add current directory context
        current_dir = os.getcwd()
        env_context = f"\nCurrent Directory: {current_dir}\nPlatform: {sys.platform}\n"
        
        full_prompt = f"{system_prompt}\n{env_context}{context_info}\nUser Request: {user_prompt}"
        
        return full_prompt
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Make API call to Ollama"""
        try:
            url = f"{config.OLLAMA_BASE_URL}/api/generate"
            
            payload = {
                "model": config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=config.OLLAMA_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    def _extract_command(self, response: str) -> str:
        """Extract command from LLM response"""
        if not response:
            return "# Error: Empty response"
        
        # Remove common prefixes and clean up
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                # Remove common prefixes
                for prefix in ['$ ', '> ', '>>> ', 'Command: ', 'command: ']:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                
                if line:
                    cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines) if cleaned_lines else response.strip()
    
    def get_or_create_session(self, session_id: str) -> CommandSession:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = CommandSession(session_id)
        
        session = self.sessions[session_id]
        
        # Update working directory
        session.working_directory = os.getcwd()
        
        return session
    
    def start_context_session(self, session_id: str = None) -> str:
        """Start a new context session"""
        if session_id is None:
            session_id = f"session_{int(time.time())}"
        
        self.current_session_id = session_id
        session = self.get_or_create_session(session_id)
        
        logger.info(f"Started context session: {session_id}")
        return session_id
    
    def end_context_session(self):
        """End the current context session"""
        if self.current_session_id:
            logger.info(f"Ended context session: {self.current_session_id}")
            self.current_session_id = None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        # Clean up expired sessions
        self.cleanup_expired_sessions()
        
        return [
            {
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'last_used': session.last_used.isoformat(),
                'context_entries_count': len(session.context_entries),
                'working_directory': session.working_directory
            }
            for session in self.sessions.values()
        ]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Removed expired session: {session_id}")
        
        if expired_sessions:
            self.save_sessions()
    
    def save_sessions(self):
        """Save sessions to file"""
        try:
            data = {
                'sessions': {
                    session_id: session.to_dict()
                    for session_id, session in self.sessions.items()
                },
                'current_session_id': self.current_session_id
            }
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def load_sessions(self):
        """Load sessions from file"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load sessions
                for session_id, session_data in data.get('sessions', {}).items():
                    self.sessions[session_id] = CommandSession.from_dict(session_data)
                
                # Load current session ID
                self.current_session_id = data.get('current_session_id')
                
                logger.info(f"Loaded {len(self.sessions)} command sessions")
                
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.sessions = {}
            self.current_session_id = None


def main():
    """Main CLI function for qlm command"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='QLM - Command Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  qlm compile verilog testbench tb_axi
  qlm -c run regression for uart flow with coverage
  qlm git commit all changes with message "fix bug"
  qlm --list-sessions
  qlm --end-session
        """
    )
    
    parser.add_argument('prompt', nargs='*', help='Command generation prompt')
    parser.add_argument('-c', '--context', action='store_true', 
                       help='Use session context')
    parser.add_argument('--list-sessions', action='store_true',
                       help='List active sessions')
    parser.add_argument('--end-session', action='store_true',
                       help='End current context session')
    parser.add_argument('--session-id', type=str,
                       help='Specific session ID to use')
    parser.add_argument('--no-copy', action='store_true',
                       help='Don\'t copy result to clipboard')
    
    args = parser.parse_args()
    
    generator = CommandGenerator()
    
    # Handle session management commands
    if args.list_sessions:
        sessions = generator.list_sessions()
        if sessions:
            print("\nActive Sessions:")
            for session in sessions:
                print(f"  {session['session_id']}: {session['context_entries_count']} entries")
                print(f"    Last used: {session['last_used']}")
                print(f"    Directory: {session['working_directory']}")
                print()
        else:
            print("No active sessions")
        return
    
    if args.end_session:
        generator.end_context_session()
        generator.save_sessions()
        print("Context session ended")
        return
    
    # Generate command
    if not args.prompt:
        parser.print_help()
        return
    
    prompt = ' '.join(args.prompt)
    
    # Set up session if using context
    if args.context:
        session_id = args.session_id or "default"
        generator.start_context_session(session_id)
    
    # Generate command
    print(f"Generating command for: {prompt}")
    command = generator.generate_command(prompt, use_context=args.context)
    
    # Copy to clipboard unless disabled
    if not args.no_copy:
        try:
            pyperclip.copy(command)
            print(f"\nGenerated & copied to clipboard:")
        except Exception as e:
            print(f"\nGenerated (copy failed: {e}):")
    else:
        print(f"\nGenerated:")
    
    print(command)
    
    # Save sessions if using context
    if args.context:
        generator.save_sessions()


if __name__ == "__main__":
    main() 
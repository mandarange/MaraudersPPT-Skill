import re
import yaml
from typing import Tuple, Dict, Any, Optional
from .contract import InputContract, Audience, Goal, Tone, CutPolicy

class MarkdownParser:
    """Parses Markdown with YAML Frontmatter and segments by H2."""
    
    FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

    @staticmethod
    def parse_frontmatter(content: str) -> Tuple[InputContract, str]:
        """Extracts YAML frontmatter and returns (InputContract, remaining_content)."""
        match = MarkdownParser.FRONTMATTER_RE.match(content)
        
        # Default values
        contract_data = {}
        remaining_content = content
        
        if match:
            try:
                frontmatter_raw = match.group(1)
                contract_data = yaml.safe_load(frontmatter_raw) or {}
                remaining_content = content[match.end():]
            except Exception as e:
                print(f"Warning: Failed to parse YAML frontmatter: {e}")
        
        # Map raw YAML data to InputContract
        # Handle enums and types
        audience = Audience(contract_data.get('audience', 'team'))
        goal = Goal(contract_data.get('goal', 'inform'))
        tone = Tone(contract_data.get('tone', 'calm'))
        cut_policy = CutPolicy(contract_data.get('cut_policy', 'balanced'))
        
        contract = InputContract(
            source_md="", # To be filled by caller
            audience=audience,
            goal=goal,
            time_minutes=int(contract_data.get('time_minutes', 15)),
            slide_budget=contract_data.get('slide_budget', 'auto'),
            tone=tone,
            cut_policy=cut_policy
        )
        
        return contract, remaining_content

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Removes markdown tokens from display text (Phase 1.2)."""
        # Remove heading markers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove list markers
        text = re.sub(r'^[ \t]*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[ \t]*\d+\.\s+', '', text, flags=re.MULTILINE)
        # Remove code fences and backticks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`', '', text)
        # Handle links: [text](url) -> text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        return text.strip()

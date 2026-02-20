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
        text = re.sub(r'```\w*\n?', '', text)
        text = re.sub(r'`', '', text)
        # Handle links: [text](url) -> text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        return text.strip()

    @staticmethod
    def split_by_h2(content: str) -> Dict[str, str]:
        """Segments markdown content by H2 headers.
        Returns a dict mapping section title (e.g. '## Background') to its full text block.
        """
        # Split by ## at the start of a line
        sections = re.split(r'^(##\s+.*)$', content, flags=re.MULTILINE)
        
        parsed_sections = {}
        # First element is usually content before the first H2 (like H1 title)
        if sections and sections[0].strip():
            parsed_sections['__pre_h2__'] = sections[0].strip()
            
        for i in range(1, len(sections), 2):
            h2_title = sections[i].strip()
            # The next element in split is the content of this H2
            h2_content = sections[i+1].strip() if i+1 < len(sections) else ""
            parsed_sections[h2_title] = h2_content
            
        return parsed_sections

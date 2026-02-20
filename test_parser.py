import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.parser import MarkdownParser
from core.contract import InputContract, Audience, Goal, Tone, CutPolicy

def test_frontmatter_parsing():
    sample_md = """---
audience: executive
goal: persuade
time_minutes: 20
tone: bold
cut_policy: ruthless
---
# Title
## Section 1
Content with **bold** and [link](http://example.com).
"""
    parser = MarkdownParser()
    contract, content = parser.parse_frontmatter(sample_md)
    
    print(f"Audience: {contract.audience}")
    print(f"Goal: {contract.goal}")
    print(f"Time: {contract.time_minutes} min")
    print(f"Slide Budget: {contract.slide_budget}")
    print(f"Tone: {contract.tone}")
    print(f"Cut Policy: {contract.cut_policy}")
    
    assert contract.audience == Audience.EXECUTIVE
    assert contract.goal == Goal.PERSUADE
    assert contract.time_minutes == 20
    assert contract.slide_budget == 30 # 20 * 1.5
    assert contract.tone == Tone.BOLD
    assert contract.cut_policy == CutPolicy.RUTHLESS
    
    sanitized = parser.sanitize_text(content)
    print(f"Sanitized Content:\n{sanitized}")
    assert "Title" in sanitized
    assert "Section 1" in sanitized
    assert "link" in sanitized
    assert "http://example.com" not in sanitized

if __name__ == "__main__":
    try:
        test_frontmatter_parsing()
        print("\n✅ Test Passed!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)

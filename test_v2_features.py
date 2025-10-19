#!/usr/bin/env python3
"""Quick test of V2 features."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.autogen_research.config import Config, ModelConfig
from src.autogen_research.teams import ResearchTeam

print("=" * 80)
print("Testing AutoGen Research Assistant V2 Features")
print("=" * 80)

# Create enhanced team with tools
print("\n1. Creating Enhanced Research Team with tools...")
config = Config(
    model=ModelConfig(
        model_type="ollama",
        model_name="llama3.2",
        temperature=0.7,
    )
)

team = ResearchTeam(config=config, enable_tools=True)
print("✓ Team created with web_search and calculator tools")

# Test with a simple calculation task
print("\n2. Testing Calculator Tool...")
print("Task: Calculate 25 * 4 + 10")
print("-" * 80)

try:
    messages, stats = team.run("Calculate: 25 * 4 + 10", use_dynamic_routing=True, verbose=False)

    print("\n✓ Task completed!")
    print("\n📊 Token Statistics:")
    print(f"   Input tokens:  {stats['input_tokens']}")
    print(f"   Output tokens: {stats['output_tokens']}")
    print(f"   Total tokens:  {stats['total_tokens']}")
    print(f"   Estimated cost: ${stats['estimated_cost']:.4f}")

    print(f"\n📝 Messages received: {len(messages)}")
    print(f"   Agents used: {stats.get('message_count', len(messages))}")

    # Show last message (likely from Critic with TERMINATE)
    if messages and hasattr(messages[-1], "content"):
        print("\n📄 Final message preview:")
        content = str(messages[-1].content)[:200]
        print(f"   {content}...")

except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nNote: This requires Ollama to be running with llama3.2 model.")
    print("Start Ollama with: ollama serve")
    print("Pull model with: ollama pull llama3.2")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)
print("\nNext steps:")
print("1. Try more complex queries with web_search()")
print("2. Test API endpoints with authentication")
print("3. Check QUICK_START_V2.md for more examples")

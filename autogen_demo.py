"""
Multi-Agent Customer Support System using AutoGen

This demo showcases a customer support system with multiple specialized agents:
- Triage Agent: Categorizes customer inquiries
- Technical Support Agent: Handles technical issues
- Billing Agent: Handles billing and payment questions
- Manager Agent: Coordinates responses and provides final answers
"""

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Ollama model client (make sure you've run `ollama pull llama3.2`)
model_client = OpenAIChatCompletionClient(
    model="llama3.2",
    api_key="ollama",  # Ollama doesn't need a real API key
    base_url="http://localhost:11434/v1",
    model_info={
        "family": "unknown",
        "vision": False,
        "function_calling": True,
        "json_output": True,
    },
)

# 1. Triage Agent - Categorizes customer inquiries
triage_agent = AssistantAgent(
    name="TriageAgent",
    description="Analyzes and categorizes customer inquiries",
    system_message="""You are a triage specialist. Your job is to:
1. Analyze customer inquiries
2. Categorize them as: TECHNICAL, BILLING, or GENERAL
3. Provide a brief summary of the issue
4. Pass to the next agent in line

Keep your response concise and structured.""",
    model_client=model_client,
)

# 2. Technical Support Agent
tech_support = AssistantAgent(
    name="TechSupport",
    description="Handles technical support issues",
    system_message="""You are a technical support specialist. You handle:
- Software installation and configuration issues
- Bug reports and troubleshooting
- API and integration questions
- System requirements and compatibility

Provide clear, step-by-step solutions. If you need more information, ask specific questions.""",
    model_client=model_client,
)

# 3. Billing Agent
billing_agent = AssistantAgent(
    name="BillingAgent",
    description="Handles billing and payment questions",
    system_message="""You are a billing specialist. You handle:
- Payment and invoice questions
- Subscription changes and cancellations
- Refund requests
- Pricing inquiries

Be empathetic and provide clear information about billing policies.""",
    model_client=model_client,
)

# 4. Manager Agent - Coordinates and finalizes responses
manager = AssistantAgent(
    name="Manager",
    description="Coordinates responses and provides final answer",
    system_message="""You are the customer support manager. Your role:
1. Review the conversation between triage and specialists
2. Ensure the customer's question is fully answered
3. Provide a final, comprehensive response
4. End with "TERMINATE" when the issue is resolved

Be professional, friendly, and ensure customer satisfaction.""",
    model_client=model_client,
)

# Create termination condition
termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(12)

# Create a round-robin team
team = RoundRobinGroupChat(
    participants=[triage_agent, tech_support, billing_agent, manager],
    termination_condition=termination,
)

# Example customer inquiries to test the system
customer_inquiries = [
    "My API key isn't working after I updated to the latest version. I keep getting a 401 error.",
    "I was charged twice for my subscription this month. Can I get a refund for the duplicate charge?",
    "What are the system requirements for running your software on Mac?",
]

async def run_support_demo(inquiry_index=0):
    """Run a customer support simulation with the selected inquiry."""
    print(f"\n{'='*80}")
    print(f"CUSTOMER SUPPORT DEMO - Inquiry #{inquiry_index + 1}")
    print(f"{'='*80}\n")

    inquiry = customer_inquiries[inquiry_index]
    print(f"Customer Question: {inquiry}\n")
    print(f"{'-'*80}\n")

    # Run the team
    stream = team.run_stream(task=inquiry)

    # Print messages as they arrive
    async for message in stream:
        if hasattr(message, 'source'):
            print(f"\n[{message.source}]:")
        if hasattr(message, 'content'):
            print(message.content)

    print(f"\n{'='*80}")
    print("Support session completed!")
    print(f"{'='*80}\n")

async def main():
    """Main entry point."""
    # Run a demo with the first inquiry (technical issue)
    # Change the index (0, 1, or 2) to test different types of inquiries
    await run_support_demo(inquiry_index=0)

    # Uncomment below to test all inquiries sequentially
    # for i in range(len(customer_inquiries)):
    #     await run_support_demo(inquiry_index=i)
    #     print("\n\n")

if __name__ == "__main__":
    asyncio.run(main())

from typing import Dict

PROMPT_TEMPLATES: Dict[str, str] = {
    "latestresults": """Extract the latest financial results for {company_name} and present it in a well formatted manner. Use Exactly the template below.

Revenue: (JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

Expenses:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

EBITDA:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

PBT:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

PAT:(JUST NUMBER)
Y-o-Y: (ONLY PERCENTAGE)
Q-o-Q: (ONLY PERCENTAGE)

Operating Profit Margins:(ONLY PERCENTAGE)
Current Operating Profit Margin: (ONLY PERCENTAGE)
Last Quarter Operating Profit Margin: (ONLY PERCENTAGE)
Last Year Operating Profit Margin: (ONLY PERCENTAGE)

Net Profit Margins:(ONLY PERCENTAGE)
Current Net Profit Margin: (ONLY PERCENTAGE)
Last Quarter Net Profit Margin: (ONLY PERCENTAGE)
Last Year Net Profit Margin:(ONLY PERCENTAGE) """,

    "orderbook": """Extract the latest order book for {company_name}. Present the information in the following format:

Latest Order book value (Date: )
QoQ Growth:
YoY Growth:

Details about the Orderbook:
• 
• 
• 

Additional Information:
- Current Capacity
- Approximate timeline to complete current order book""",

    "transcriptsummary": """Using the documents provided, give me the summary of the latest transcript for {company_name}. Limit your answer to 5 bullet points and give more qualitative answers than quantitative answers (provide actual numbers wherever possible). You can also include quotations where you deem important.

Using your reasoning, you can also label some bullet points as important if you think they're important for the company's future outlook.

Here is the template for the output:

"Here is the summary of the latest transcript:

Company Executive Name and Position:
Interview Done by:

- IMP: ---
- -----" """,

    "futureoutlook": """Using the documents provided:

Tell me the overall future outlook of {company_name}. Give your response in a very structured and categorized manner. Keep each line very concise.""",

    "nextresultdate": """Using information provided in the documents and sources from the web, find out when {company_name} will give the results next.

if the next result date is not present, then look back and see when did they give the same quarter results last year, and show that as the estimate.

Template of the output:
"Next Result Date (For Quarter ---): "
or
"Estimated Result Date (For Quarter ---, based on past):"

Only give the required template answer, don't explain yourself""",

    "general_market": """Use your market knowledge and the provided context to answer questions about the Indian equities market. Be concise and accurate.
Focus on providing data-driven responses using reliable financial sources. Include relevant market statistics when available.
Use Indian currency (₹) and number formats (lakhs, crores) appropriately.

Context: {context}
Question: {question}

Provide a structured, clear response with factual information."""
}

# List of available standard prompts
STANDARD_PROMPTS = ["latestresults", "orderbook", "transcriptsummary", "futureoutlook", "nextresultdate"]
from typing import Dict

REPORT_TEMPLATES: Dict[str, str] = {
    "company_full_name": """What is the full registered name of {company_name}? Provide only the complete official company name, nothing else.

Output:
{{company_full_name}}""",

    "current_price": """What is the current stock price of {company_name} from NSE/BSE? Provide only the number, no currency symbol or text. You can add commas to the number if needed.

    GIVE ONLY THE NUMBER with COMMAS, NOTHING ELSE
Output:
{{current_price}}""",

    "current_marketcap": """What is the current market capitalization of {company_name} in Crores? Provide only the number, no currency or text. Round to nearest whole number. You can add commas to the number if needed.
GIVE ONLY THE NUMBER IN CRORES. DONT EVEN MENTION CRORES.
Output:
{{current_marketcap}}""",

    "business_model": """Summarize the business model of {company_name} in a concise manner with 4 bullet points (max 20 words each). Do not mention the company name in these bullet points.

Output:
{{business_model}}""",

    "key_metrics": """Provide the key metrics for {company_name} in the below format:

P/E: [number]
ROCE (%): [number]
ROE (%): [number]
Book value: [number]
Debt/Equity: [number]
Div Yield (%): [number]

Do not explain each terminology to the user. Double check if the values are accurate. Provide numbers only, no text explanations. ONLY THE HEADER AND THE NUMBER PLEASE!!!

Output:
{{key_metrics}}""",

    "competitors": """List down the three closest competitors to {company_name}. Give the positioning of the companies in the industry and one sentence about its financial standing along with its unique selling point (max 25 words per competitor). Include at least one competitors from public markets.

Output:
{{competitors}}""",

    "future_outlook": """Using the documents provided:

Tell me the overall future outlook of {company_name}. Give your response in a very structured and categorized manner. Keep each line very concise (maximum 15 words per point).

Output:
{{future_outlook}}""",

    "news": """Provide the latest significant news and updates about {company_name} from reliable sources. Focus on material developments that could impact the company's performance. List exactly 3 updates, maximum 20 words each.

Output:
{{news}}"""
} 
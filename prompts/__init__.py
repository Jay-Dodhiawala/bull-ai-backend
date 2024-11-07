from typing import Dict
from .report_templates import REPORT_TEMPLATES
from .standard_prompts import PROMPT_TEMPLATES

# Combine all templates
ALL_TEMPLATES = {
    **PROMPT_TEMPLATES,
    **REPORT_TEMPLATES
}
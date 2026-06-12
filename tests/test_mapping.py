import json

from genai_hub.mapping.transformer import DataTransformer


def test_crm_ticket_to_prompt():
    ticket = {"customer_name": "Test AG", "subject": "Help", "description": "Issue", "priority": "high"}
    prompt = DataTransformer.crm_ticket_to_prompt(ticket)
    assert "Test AG" in prompt
    assert "Help" in prompt


def test_llm_json_to_crm_update():
    llm_output = json.dumps({"suggested_response": "Danke", "confidence": 0.9})
    result = DataTransformer.llm_json_to_crm_update(llm_output, "TKT-1")
    assert result["id"] == "TKT-1"
    assert result["ai_suggested_reply"] == "Danke"


def test_llm_json_to_erp_order():
    llm_output = json.dumps({"extracted_order": {"sku": "SKU-A100", "quantity": 5}})
    result = DataTransformer.llm_json_to_erp_order(llm_output, "CUST-1")
    assert result["lines"][0]["sku"] == "SKU-A100"
    assert result["lines"][0]["quantity"] == 5

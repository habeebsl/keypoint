import json
import re

import markdown
from decouple import config
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

client = genai.Client(api_key=config("GEMINI_API_KEY"))

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

md = markdown.Markdown()

PARSER = 'html.parser'

def remove_markdown_with_spacing(text):
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, PARSER)  
    for element in soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        element.insert_before("\n")
        element.insert_after("\n")

    return soup.get_text()

def escape_and_replace_in_html(pattern, replacement_func, html_content):
    soup = BeautifulSoup(html_content, PARSER)
    text_nodes = soup.find_all(string=True)
    
    for text_node in text_nodes:
        if text_node.parent.name in ['code', 'pre']:
            continue

        original_text = text_node.string
        if not original_text:
            continue

        new_text = re.sub(pattern, replacement_func, original_text)
        if new_text != original_text:
            text_node.replace_with(BeautifulSoup(new_text, PARSER))
    
    return str(soup)
    

def highlight_content(original_text, json_response):
    html_text = md.convert(original_text)
    response = json.loads(json_response)
    result = html_text
    
    for paragraph in response.get("paragraphs", []):
        pattern = re.escape(paragraph)
        result = escape_and_replace_in_html(
            pattern,
            lambda m: f'<div class="highlight-paragraph">{m.group(0)}</div>',
            result
        )

    for sentence in response.get("sentences", []):
        pattern = re.escape(sentence)
        result = escape_and_replace_in_html(
            pattern,
            lambda m: f'<span class="highlight-sentence">{m.group(0)}</span>',
            result
        )
    
    for word in response.get("words", []):
        pattern = rf'\b{re.escape(word)}\b'
        result = escape_and_replace_in_html(
            pattern,
            lambda m: f'<mark class="highlight-word" data-term="{m.group(0)}">{m.group(0)}</mark>',
            result
        )
    
    return result


def get_response(text):
    with open(r"home/prompts/key_content.txt", "r", encoding="utf-8") as file:
        instructions = file.read()

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=instructions
            ),
            contents=remove_markdown_with_spacing(text)
        )

        print(response.text)
        return highlight_content(original_text=text, json_response=response.text)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

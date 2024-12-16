import json
import re
import html

from decouple import config
import google.generativeai as genai

genai.configure(api_key=config('GEMINI_API_KEY'))

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}


def escape_and_replace(pattern, replacement, text):
	return re.sub(pattern, lambda m: replacement(m.group(0)), text)

def highlight_content(original_text, json_response):
	response = json.loads(json_response)
	text = html.escape(original_text)

	sentences = response.get("sentences", [])
	paragraphs = response.get("paragraphs", [])
	words = response.get("words", [])


	for sentence in sentences:
		sentence_escaped = html.escape(sentence)
		text = escape_and_replace(
			re.escape(sentence_escaped), 
			lambda m: f'<span class="highlight-sentence">{m}</span>', 
			text
		)

	for paragraph in paragraphs:
		paragraph_escaped = html.escape(paragraph)
		text = escape_and_replace(
			re.escape(paragraph_escaped), 
			lambda m: f'<p class="highlight-paragraph">{m}</p>', 
			text
		)

	for word in words:
		word_escaped = html.escape(word)
		text = escape_and_replace(
			rf'\b{re.escape(word_escaped)}\b', 
			lambda m: f'<mark class="highlight-word" data-term="{m}">{m}</mark>', 
			text
		)

	return text

def get_response(text):
	with open(r"home/prompts/key_content.txt", "r", encoding="utf-8") as file:
		instructions = file.read()

	model = genai.GenerativeModel(
		model_name="gemini-1.5-pro",
		generation_config=generation_config,
		system_instruction=instructions,
	)
	response = model.generate_content(text)
	print(response.text)
	return highlight_content(original_text=text, json_response=response.text)
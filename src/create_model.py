import requests

url = "http://localhost:11434/api/create"

# Define the content of your Modelfile
modelfile_content = (
    r"""
FROM C:\mistral_llm\dolphin-2.7-mixtral-8x7b.Q2_K.gguf

TEMPLATE """
    + r"""{{ if .System }}system
{{ .System }}
{{ end }}{{ if .Prompt }}user
{{ .Prompt }}
{{ end }}assistant
"""
    + r"""

SYSTEM You are a helpful and friendly assistant. Answer the user's questions to the best of your ability.
"""
)

# Define the request payload
data = {
    "name": "dolphin-2.7-mixtral-8x7b",
    "modelfile": modelfile_content.strip(),  # Strip any extra leading/trailing whitespace
}

# Send the request to create the model
response = requests.post(url, json=data)

# Check the response status
if response.status_code == 200:
    print("Model created successfully!")
else:
    print("Failed to create model:", response.text)

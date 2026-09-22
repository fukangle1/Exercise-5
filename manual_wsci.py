from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    ##Use only the files that are relevant to the question.
    "knowledge/wifi_setup.txt",
    "knowledge/password_changes.txt",
    "knowledge/service_status.txt"
]


context = ""

## Write a for loop to go through all the files in selected_files and read their contents into the context variable.
for file_path in selected_files:
    with open(file_path, "r") as f:
        context += f.read()
        context += "\n\n"


## Call Qwen with the student's question and the context you created above.
response = chat(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": "You are a university IT support assistant. Answer the student's question using the context below.\n\nContext:\n" + context},
        {"role": "user", "content": question}
    ]
)


print(
    "Context characters:",
    len(context)
)
print(response["message"]["content"])
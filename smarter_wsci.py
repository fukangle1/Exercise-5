from pathlib import Path
from ollama import chat
import json



question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## WRITE ##
service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "wi_fi status": "operational",
    "wi-fi_check": True
}

## Create two separated states
diagnostic_context = {
    "problem": question,
    "device": "Windows laptop",
    "wifi_status": "operational"
}

report_context = {
    "total_wifi_cases": 37,
    "resolved_cases": 29,
    "unresolved_cases": 8
}

# use qwen to classify the question
classify_response = chat(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": "Classify the user question. Reply with only one word: diagnostic or report."},
        {"role": "user", "content": question}
    ]
)

category = classify_response.message.content.strip().lower()

if "report" in category:
    state = report_context
else:
    state = diagnostic_context

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

with open("state.json", "r") as file:
    state = json.load(file)

print(state)


## SELECT CONTEXT FILES BASED ON QUESTION
## Create the function that takes the student's question, takes some keywords and chooses the relevant files from the knowledge base. Return a list of the selected files.
## For example, if the question has the kyeword "print" or "printer", then the function should return the file "knowledge/printer_setup.txt" in a list.
def select_context(question):
    q = question.lower()
    selected = []
    
    # check the wifi
    if "wifi" in q or "wi-fi" in q or "network" in q:
        selected.append("knowledge/wifi_setup.txt")
    
    # check the password
    if "password" in q:
        selected.append("knowledge/password_changes.txt")
    
    # check the status
    if "status" in q or "operational" in q:
        selected.append("knowledge/service_status.txt")
    
    return selected


selected_files = select_context(question)

## READ SELECTED FILES and add their contents to the context variable.
context = ""
for file_path in selected_files:
    with open(file_path, "r") as f:
        context += f.read()
        context += "\n\n"


## 
## COMPRESS CONTEXT
## Add logic to compress the context from above by calling Qwen with "context" and the "question" as the parameter
## The response from Qwen should be the compressed context. Store it in a variable called "compressed_context" 

def compress_context(context, question):
    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": "Compress this context. Keep only the stuff that helps answer the question. Keep the important steps."},
            {"role": "user", "content": "Question:\n" + question + "\n\nContext:\n" + context}
        ]
    )
    return response["message"]["content"]


compressed_context = compress_context(context, question)

## Print the length of the compressed context
print(len(compressed_context))

## Now, call Qwen again with the compressed context and the student's question. Store the response in a variable called "response" and print the response from Qwen.
## Ensure the model produces a structured output 
response = chat(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": "You are a university IT support assistant. Use ONLY the compressed context and state below to answer the question. Give a clear, step-by-step answer.\n\nCompressed context:\n" + compressed_context + "\n\nState:\n" + json.dumps(state)},
        {"role": "user", "content": question}
    ]
)


print(response.message.content)

## WRITE the above output in an artifact called "state"
state["answer"] = response.message.content

with open("state.json", "w") as file:
    json.dump(state, file, indent=2)

## Update the rest of the code so that it uses the "state" artifact as part of the context. 
## It is important to ensure that the model uses only the relevant parts from the "state" artifact and not the entire artifact.
## For this, you may have to think of a good structure for the "state" artifact and how to use it in the context.



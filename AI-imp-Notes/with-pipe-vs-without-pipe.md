import os
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# ==============================================================================
# 0. SETUP COMPONENTS
# ==============================================================================
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert tutor. Provide brief, single-sentence explanations.",
        ),
        ("human", "Explain the concept: {topic}"),
    ]
)

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.2,
)

parser = StrOutputParser()

raw_user_input = {"topic": "Photosynthesis"}


# ==============================================================================
# APPROACH 1: WITHOUT PIPE (Manual Step-by-Step Invocation)
# This reveals exactly what data type enters and leaves each component.
# ==============================================================================
print("=== APPROACH 1: WITHOUT PIPE ===")

# --- STEP 1: Prompt Template ---
# INPUT FORMAT:
#   Type: dict
#   Value: {"topic": "Photosynthesis"}
step1_output = prompt.invoke(raw_user_input)

# OUTPUT FORMAT:
#   Type: ChatPromptValue (implements PromptValue)
#   Internal representation: [
#       SystemMessage(content="You are an expert tutor..."),
#       HumanMessage(content="Explain the concept: Photosynthesis")
#   ]
print("\n[Step 1 - Prompt Output Type]:", type(step1_output))
print(
    "[Step 1 - Prompt Output Representation]:\n", step1_output.to_messages()
)


# --- STEP 2: Chat Model ---
# INPUT FORMAT:
#   Type: ChatPromptValue (or list of BaseMessage objects)
#   Value: step1_output passed directly
step2_output = model.invoke(step1_output)

# OUTPUT FORMAT:
#   Type: AIMessage (subclass of BaseMessage)
#   Fields:
#     - .content: str -> "Photosynthesis is the biological process by which green plants..."
#     - .response_metadata: dict -> token usage, safety ratings, finish reason, etc.
print("\n[Step 2 - Model Output Type]:", type(step2_output))
print("[Step 2 - Model Output Raw Message]:\n", repr(step2_output))


# --- STEP 3: Output Parser ---
# INPUT FORMAT:
#   Type: AIMessage (or any BaseMessage / str)
#   Value: step2_output passed directly
step3_output = parser.invoke(step2_output)

# OUTPUT FORMAT:
#   Type: str
#   Value: "Photosynthesis is the process..." (plain Python string)
print("\n[Step 3 - Parser Output Type]:", type(step3_output))
print("[Step 3 - Final Parsed Text]:\n", step3_output)


# ==============================================================================
# APPROACH 2: WITH PIPE (`|`)
# The pipe syntax automatically connects output of Step N to input of Step N+1.
# ==============================================================================
print("\n=== APPROACH 2: WITH PIPE (LCEL) ===")

# Under the hood, `a | b` creates a `RunnableSequence(first=a, middle=[], last=b)`.
# When chained further: `a | b | c` produces a single unified RunnableSequence.
chain = prompt | model | parser

print("[Chain Object Type]:", type(chain))
# Type: <class 'langchain_core.runnables.base.RunnableSequence'>

# Executing the chain with the initial dictionary:
final_response = chain.invoke(raw_user_input)

print("\n[LCEL Final Output Type]:", type(final_response))
print("[LCEL Final Response]:\n", final_response)

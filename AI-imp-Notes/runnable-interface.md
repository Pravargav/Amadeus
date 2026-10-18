The **Runnable Interface** (`Runnable`) is the foundational abstraction in `langchain_core`. It provides a uniform execution standard for all components in the LangChain ecosystem—prompts, models, retrievers, output parsers, and custom tools.

Before the Runnable interface, different modules implemented disparate methods (e.g., `model.generate()`, `prompt.format()`, `chain.run()`). The Runnable interface replaced these with a single, consistent set of execution primitives across all objects.

---

## 1. The Standard Execution Protocol

Every object inheriting from `Runnable` exposes the exact same six execution methods, providing immediate support for synchronous, asynchronous, batch, and streaming workflows without modifying component internals:

| Method | Type | Description |
| --- | --- | --- |
| **`.invoke(input, config=None)`** | Synchronous | Runs the component on a single input. |
| **`.ainvoke(input, config=None)`** | Asynchronous | `async/await` version of `.invoke()`. |
| **`.batch([inputs], config=None)`** | Synchronous | Executes concurrently across an iterable of inputs. |
| **`.abatch([inputs], config=None)`** | Asynchronous | Non-blocking concurrent execution over inputs. |
| **`.stream(input, config=None)`** | Synchronous | Yields output chunks (tokens, intermediate state) as an iterator. |
| **`.astream(input, config=None)`** | Asynchronous | Yields output chunks as an async generator (`async for`). |

All execution methods accept an optional `RunnableConfig` dictionary, which carries runtime parameters like:

* `callbacks`: Tracers and loggers (e.g., LangSmith).
* `tags` / `metadata`: Telemetry and filtering labels.
* `max_concurrency`: Thread pool limits for `.batch()`.
* `recursion_limit`: Caps for cyclical or agentic graphs.

---

## 2. Core Runnable Components in `langchain_core.runnables`

LangChain provides several structural components that govern routing, parallel execution, and data transformation within chains.

### A. `RunnableSequence` (The Pipe Operator `|`)

* **Role:** Linear orchestration.
* **Mechanism:** Produced when connecting runnables via `step1 | step2`. It ensures the output of `step1` matches the expected input type of `step2`.
* **Execution:** Iterates over its internal `steps` list, passing intermediate results forward.

```python
# prompt | model | parser creates an instance of RunnableSequence
sequence = prompt | model | parser
output = sequence.invoke({"topic": "Distributed Systems"})

```

### B. `RunnableParallel` (Map / Fork Pattern)

* **Role:** Concurrent branch execution.
* **Mechanism:** Accepts a mapping (dictionary) of runnables. When invoked with an input, it executes every branch simultaneously using a thread pool (or event loop in `ainvoke`), returning a dictionary containing the results under their respective keys.

```python
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Both branches execute concurrently using the same user query
setup_and_retrieval = RunnableParallel(
    context=retriever,
    question=RunnablePassthrough(),
)

```

### C. `RunnablePassthrough`

* **Role:** Identity forwarding and state enrichment.
* **Forms:**
1. **Bare `RunnablePassthrough()**`: Emits its input completely unaltered. Useful in `RunnableParallel` to keep the original input alongside processed values.
2. **`RunnablePassthrough.assign(...)`**: Takes an input dictionary and appends new calculated keys while retaining all existing keys without needing manual dictionary unpacking.



```python
# Appends 'context' to the existing dict {'question': '...'}
chain = RunnablePassthrough.assign(context=retrieval_chain)

```

### D. `RunnableLambda`

* **Role:** Python function bridging.
* **Mechanism:** Wraps any arbitrary Python callable (or `lambda`) so it implements the `Runnable` interface.
* **Use Case:** Custom formatting, sanitization, regex matching, or interfacing with proprietary libraries mid-chain.

```python
from langchain_core.runnables import RunnableLambda


def sanitize_input(data: dict) -> dict:
    data["query"] = data["query"].strip().lower()
    return data


chain = RunnableLambda(sanitize_input) | prompt | model

```

### E. `RunnableBranch` & Dynamic Routing

* **Role:** Conditional routing.
* **Mechanism:** Accepts pairs of `(condition_fn, runnable_to_execute)` alongside a default fallback. Evaluates conditions sequentially and routes input to the matching branch.
* *Note:* Modern LCEL often prefers writing a standard Python function returning a runnable wrapped in `@chain` or `RunnableLambda` over complex `RunnableBranch` definitions for readability.

```python
from langchain_core.runnables import RunnableBranch

router = RunnableBranch(
    (lambda x: "code" in x["topic"].lower(), code_chain),
    (lambda x: "math" in x["topic"].lower(), math_chain),
    general_chain,  # default fallback
)

```

### F. Resiliency Modifiers (`with_fallbacks`, `with_retry`)

Any Runnable instance can be augmented with fault-tolerance features directly on the object:

* **`.with_fallbacks([backup_runnable])`**: If the primary runnable raises an exception (e.g., rate-limit, service degradation), execution immediately swaps to the fallback model/chain.
* **`.with_retry(stop_after_attempt=3)`**: Retries the component on transient network errors using exponential backoff.

```python
robust_model = primary_model.with_fallbacks([secondary_model])

```

---

## 3. End-to-End Architectural Flow

The diagram below illustrates how these components operate as unified stages within an LCEL pipeline:

```text
                     Raw Input: {"question": "How does Raft work?"}
                                      │
                                      ▼
                        [ RunnablePassthrough.assign ]
                       ┌──────────────┴──────────────┐
                       │                             ▼
                 (Passes Query)            [ Sub-Runnable: Retriever ]
                       │                             │
                       └──────────────┬──────────────┘
                                      ▼
                     Dict: {"question": "...", "context": [...]}
                                      │
                                      ▼
                       [ ChatPromptTemplate (Runnable) ]
                                      │
                                      ▼
                         [ ChatModel (Runnable) ]
                        (with_fallbacks / with_retry)
                                      │
                                      ▼
                        [ StrOutputParser (Runnable) ]
                                      │
                                      ▼
                           Final String Output

```

By decoupling control flow (`RunnableParallel`, `RunnableSequence`), functional bridges (`RunnableLambda`), and native operational features (`stream`, `batch`, `fallbacks`), the Runnable interface allows developers to construct modular, production-ready LLM applications without manual threading, streaming loops, or fragile glue code.


Prior to the introduction of the unified **`Runnable`** interface (and LCEL) in `langchain_core`, LangChain relied on a disparate collection of component-specific methods, imperative chain wrapper classes, and fragmented execution functions.

Here is the comprehensive catalog of methods, classes, and execution functions that were used before `Runnable`.

---

### 1. Legacy Execution Methods on Chains (`Chain` Base Class)

Before `.invoke()`, `.stream()`, and `.batch()`, all multi-step workflows inherited from the `Chain` class (`langchain.chains.base.Chain`), which exposed these execution methods:

* **`chain.__call__(inputs)`**: The primary callable entry point. It took a dictionary of inputs and returned a dictionary containing both inputs and outputs (or just outputs, depending on `return_only_outputs`).
* **`chain.run(*args, **kwargs)`**: The most common shorthand for chains with a single output key. It accepted strings or keyword arguments directly and returned the raw value (usually a string) instead of a dictionary.
* **`chain.arun(*args, **kwargs)`**: The asynchronous equivalent of `chain.run()`.
* **`chain.acall(inputs)`**: The asynchronous equivalent of `chain.__call__()`.
* **`chain.apply(input_list)`**: The predecessor to `.batch()`. It ran a list of dictionary inputs sequentially (or pseudo-concurrently) across the chain and returned a list of outputs.

```python
# Legacy style:
result_dict = chain({"topic": "AI"})  # __call__
result_str = chain.run("AI")  # run()
results = chain.apply([{"topic": "AI"}, {"topic": "Math"}])  # apply()

```

---

### 2. Legacy Model Methods (`BaseLLM` and `BaseChatModel`)

Different model types had incompatible interfaces instead of a universal `.invoke()` / `.stream()` standard:

#### For Completion LLMs (`BaseLLM` / `LLM`)

* **`llm.__call__(prompt: str)`**: Called the LLM directly with a string prompt and returned a generated string.
* **`llm.generate(prompts: List[str])`**: Accepted a list of prompt strings and returned an `LLMResult` object containing generations, token usage, and provider metadata.
* **`llm.agenerate(prompts: List[str])`**: The async version of `.generate()`.
* **`llm.predict(text: str)`**: Text completion wrapper returning a plain string.
* **`llm.apredict(text: str)`**: Async version of `.predict()`.

#### For Chat Models (`BaseChatModel`)

* **`chat_model.__call__(messages: List[BaseMessage])`**: Accepted a list of message objects and returned a single `BaseMessage` (such as `AIMessage`).
* **`chat_model.generate(messages: List[List[BaseMessage]])`**: Accepted batches of message lists and returned a `ChatResult` object.
* **`chat_model.agenerate(...)`**: The async version of `chat_model.generate()`.
* **`chat_model.predict_messages(messages: List[BaseMessage])`**: Explicit method returning an `AIMessage`.
* **`chat_model.apredict_messages(messages: List[BaseMessage])`**: Async version of `predict_messages`.

---

### 3. Legacy Prompt Methods (`BasePromptTemplate`)

Before prompt templates became runnables returning a `PromptValue`, formatting required dedicated formatting methods:

* **`prompt.format(**kwargs)`**: Substituted variables and returned a single combined Python string (`str`).
* **`prompt.format_prompt(**kwargs)`**: Returned a `PromptValue` object with helper methods:
* `.to_string()`: Converted the formatted output to a raw text string.
* `.to_messages()`: Converted the formatted output to a list of message objects (`HumanMessage`, `AIMessage`, etc.).


* **`chat_prompt.format_messages(**kwargs)`**: Specifically for chat prompts; directly returned a list of `BaseMessage` instances.

---

### 4. Legacy Output Parser Methods (`BaseOutputParser`)

Parsers did not support piping (`|`) and required manual string-to-object function calls:

* **`parser.parse(text: str)`**: Took raw model output text and parsed it into strings, lists, dictionaries, or Pydantic models.
* **`parser.parse_with_prompt(completion: str, prompt_value: PromptValue)`**: Used when the parser needed context from the original prompt to repair or understand malformed output.
* **`parser.get_format_instructions()`**: Generated textual instructions to be manually interpolated into the prompt text.

---

### 5. Legacy Retriever Methods (`BaseRetriever`)

Before retrievers implemented the `Runnable` protocol, document fetching used dedicated getter methods:

* **`retriever.get_relevant_documents(query: str)`**: Took a single query string and returned a `List[Document]`.
* **`retriever.aget_relevant_documents(query: str)`**: Asynchronous version of `get_relevant_documents()`.

### What Are Runnables in `langchain_core`?

A **`Runnable`** is the standard protocol (base interface) that almost all LangChain components inherit from—including prompt templates, chat models, output parsers, retrievers, and custom tool functions.

Instead of each component having custom method names (like `.generate()`, `.predict()`, or `.format()`), every `Runnable` implements a unified execution interface:

* **`.invoke(input)`**: Synchronous single input run.
* **`.ainvoke(input)`**: Asynchronous single input run.
* **`.batch([input1, input2])`**: Concurrent batch processing.
* **`.stream(input)`**: Real-time token/chunk streaming.
* **`|` (pipe operator)**: Sequences two runnables into a composite `RunnableSequence`.

Because every unit conforms to this exact contract, you can chain disparate components together like Lego bricks, with built-in tracing, batching, and error handling.

---

### Core Runnables: `RunnableLambda` & `RunnableParallel`

#### 1. `RunnableLambda`

* **Purpose**: Converts any standard Python function or lambda into a first-class `Runnable`.
* **Why use it**: Plain Python functions do not natively have `.invoke()`, `.batch()`, or support the pipe (`|`) operator. Wrapping them in `RunnableLambda` allows custom transformations, data cleaning, or formatting logic to sit seamlessly inside a chain.

#### 2. `RunnableParallel`

* **Purpose**: Executes multiple Runnables **concurrently** on the same input, returning a single merged dictionary where keys match the branches.
* **Why use it**: Often, downstream steps require multiple independent pieces of context simultaneously (e.g., retrieving relevant docs and rephrasing the question at the same time). `RunnableParallel` prevents sequential bottlenecks by running those branches in parallel threads.

---

### Comparison: Without Runnables vs. With Runnables

Let's look at an identical problem:
Given a user query, we want to:

1. Normalize and clean the text.
2. Run two tasks in parallel:
* Generate a concise explanation using the LLM.
* Calculate word/character statistics using a custom Python function.


3. Combine both into a single final dictionary.

---

#### 1. WITHOUT Runnables (Manual Standard Python)

Here, you must manually coordinate execution, manage thread pools for parallel calls, handle async/batch plumbing yourself, and unpack/repack every intermediate object:

```python
from concurrent.futures import ThreadPoolExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a concise tutor. Explain in under 20 words.",
        ),
        ("human", "Explain: {clean_topic}"),
    ]
)


# Step 1: Plain python function
def clean_text(text: str) -> str:
    return text.strip().capitalize()


# Step 2: Plain python analysis function
def compute_stats(text: str) -> dict:
    return {"char_count": len(text), "word_count": len(text.split())}


# Step 3: LLM Worker Function
def run_llm_worker(cleaned: str) -> str:
    # Manual prompt format
    prompt_val = prompt.invoke({"clean_topic": cleaned})
    # Manual model call
    ai_msg = llm.invoke(prompt_val)
    # Manual parsing
    return ai_msg.content


# Execution
raw_input = "   distributed caching systems   "

# 1. Clean input
cleaned_topic = clean_text(raw_input)

# 2. Parallel execution requires manual ThreadPoolExecutor management
with ThreadPoolExecutor(max_workers=2) as executor:
    future_stats = executor.submit(compute_stats, cleaned_topic)
    future_llm = executor.submit(run_llm_worker, cleaned_topic)

    stats_result = future_stats.result()
    llm_result = future_llm.result()

# 3. Manual assembly
final_output = {
    "topic": cleaned_topic,
    "summary": llm_result,
    "statistics": stats_result,
}

print("=== Output Without Runnables ===")
print(final_output)

```

---

#### 2. WITH Runnables (`RunnableLambda` & `RunnableParallel`)

With LCEL, thread pooling, type handoffs, and pipe composition are handled automatically:

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
parser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a concise tutor. Explain in under 20 words.",
        ),
        ("human", "Explain: {clean_topic}"),
    ]
)


# Plain Python functions
def clean_text(raw_input: str) -> str:
    return raw_input.strip().capitalize()


def compute_stats(cleaned_text: str) -> dict:
    return {
        "char_count": len(cleaned_text),
        "word_count": len(cleaned_text.split()),
    }


# ------------------------------------------------------------------------------
# 1. RunnableLambda in action
# ------------------------------------------------------------------------------
# Turns `clean_text` into a component that can accept `.invoke()`, `.batch()`, and `|`
cleaner_runnable = RunnableLambda(clean_text)

# ------------------------------------------------------------------------------
# 2. Sub-chains built with pipe
# ------------------------------------------------------------------------------
# Input: str -> Prompt -> LLM -> StrParser -> str
summary_chain = (
    RunnableLambda(lambda text: {"clean_topic": text}) | prompt | llm | parser
)

# ------------------------------------------------------------------------------
# 3. RunnableParallel in action
# ------------------------------------------------------------------------------
# Both branches receive the exact same output from cleaner_runnable concurrently
parallel_tasks = RunnableParallel(
    topic=RunnablePassthrough(),  # Passes the cleaned string as-is
    summary=summary_chain,  # Branch 1: Calls LLM
    statistics=RunnableLambda(
        compute_stats
    ),  # Branch 2: Computes stats via RunnableLambda
)

# ------------------------------------------------------------------------------
# 4. Assembled Complete Pipeline
# ------------------------------------------------------------------------------
pipeline = cleaner_runnable | parallel_tasks

# Execute
final_output = pipeline.invoke("   distributed caching systems   ")

print("=== Output With Runnables ===")
print(final_output)

```

---

### What Changed?

| Aspect | Without Runnables | With Runnables (`RunnableLambda` / `RunnableParallel`) |
| --- | --- | --- |
| **Concurrency** | Manual `ThreadPoolExecutor` or `asyncio.gather` code. | Native: `RunnableParallel` automatically runs branches across threads. |
| **Piping & Composition** | Imperative line-by-line function calls and variable assignments. | Declarative ` |
| **Batch Processing** | You write loops or custom queue dispatchers. | Automatic: `pipeline.batch(["item1", "item2"])` handles batching at every node. |
| **Custom Functions** | Isolated from the ecosystem. | `RunnableLambda` elevates normal functions into unified LangChain nodes with logging, tracing, and metric hooks. |


# 🧪 LLM Response Evaluator

This utility tests how consistently and accurately an LLM (e.g., OpenAI GPT-4o) responds to structured prompts, especially in time-sensitive or context-aware workflows. It evaluates whether the model's output matches expected values and helps benchmark different prompt formats and models under controlled conditions.

---

## 🔍 Overview

The script automates the evaluation of an assistant's ability to return accurate responses based on contextual input — such as natural language appointment requests tied to specific dates.

It is especially useful when:
- Testing **prompt engineering iterations**
- Validating **LLM behavior in scheduling or logic-heavy tasks**
- Benchmarking models across **temperature or version changes**
- Tracking regression across **system prompt updates**

---

## 🧰 Features

- ✅ Batch test multiple `(currentDateTime, user request)` combinations
- 🔁 Runs each test 10 times to evaluate consistency
- 📊 Compares responses to a CSV-based ground truth
- 🧠 Smart formatting of date results for accurate validation
- 📂 Outputs results to a timestamped CSV report
- 🔒 Built-in OpenAI rate limiting to avoid throttling

---

## 🧪 Example Use Case

If the current time is:

```text
2025-01-13 14:01 Mon
```

And the user says:

```text
I want to book a haircut for Friday
```

Then the assistant should return:

```text
2025-01-17
```

This script tests whether it does — and how consistently.

---

## 🛠️ Tech Stack

- Python 3
- OpenAI SDK
- Pandas
- CSV I/O
- Time + Rate Management
- Prompt read from external file
- Validation logic using `validation_data.csv`

---

## 📁 Project Structure

```text
tool_21_prompts/
    tool_21_prompt_V13.txt     # System prompt used for all requests

tool_21_runs/
    results_YYYYMMDD_HHMMSS_tool_21_prompt_V13.csv  # Output log

validation_data.csv            # Ground truth for each test case
OAI_CC_MAKE_DATE_GCAL.py       # Main test script
```

---

## 🚀 Getting Started

1. Add your system prompt to:
   ```
   tool_21_prompts/tool_21_prompt_V13.txt
   ```
2. Provide your expected outputs in:
   ```
   validation_data.csv
   ```
3. Run the script:
   ```bash
   python OAI_CC_MAKE_DATE_GCAL.py
   ```

---

## 🧩 Extending This Project

- Add support for testing **different models** or **temperatures**
- Integrate with LangChain or LangGraph agents
- Log OpenAI response metadata for analysis
- Add charts or dashboards to visualize accuracy trends over time

---

## 🙋 About

Created by Brett C. as part of an AI workflow automation portfolio. I build modular FastAPI agents that connect APIs to real-time interfaces using clean, extensible code patterns.

---

## 📄 License

This project is licensed under the MIT License.

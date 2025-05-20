
# Project Title

A brief description of what this project does and who it's for

# 🧠 Gemini AI Agent with LangGraph + FastAPI

A powerful AI agent built with **LangGraph**, **Gemini 1.5 Flash**, and **FastAPI**, distributed via the blazing-fast `uv` package.

This conversational agent can:

- Detect if a user is registered
- Initiate a registration process with a form
- Confirm user registration
- Dynamically respond based on state
- Expose the conversation via a FastAPI endpoint

---

## 🚀 Features

- ✅ Unregistered user detection
- 🧾 Sends a registration form with a unique `user_id`
- 🔄 Confirms form submission
- ⚙️ Dynamic LangGraph workflow with state transitions
- 🧠 Gemini 1.5 Flash LLM
- ⚡ FastAPI for exposing endpoints
- 📦 `uv` package for zero-hassle CLI and FastAPI entrypoint

---

## 🏗️ Architecture

```mermaid
graph TD
    A[User Message] --> B{Categorizer Node}
    B -->|Registered| C[Register Node]
    B -->|Unregistered| D[Unregister Node]
    D --> E[ToolNode (register/confirm)]



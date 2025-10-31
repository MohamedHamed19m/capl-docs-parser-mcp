# 🤖 Gemini Integration — CAPL Documentation MCP Server

This MCP server (`MCP_Server.py`) allows Gemini (or any MCP-compatible AI) to search and parse Vector CAPL documentation stored in Markdown files.
It’s designed to help you query CAPL function definitions, syntax, parameters, and examples directly from Gemini without manual browsing.

## ✅ When to Use This MCP Server

Use this server when:

*   You want Gemini to search for CAPL functions (e.g., `UdpSend`, `CanSetChannel`, `EthFrameSend`) inside your local documentation.
*   You’re asking questions like:
    *   “Show me the syntax for `UdpSend`.”
    *   “What parameters does `CanWrite` use?”
    *   “Search CAPL docs for all functions that return a socket handle.”
*   You need structured information (syntax, parameters, return values, examples) rather than just raw text.
*   You’re working in offline or local development mode, where Gemini can’t access external documentation sources.

## 🚫 When Not to Use This MCP Server

Avoid using this server when:

*   You’re asking conceptual or theoretical CAPL questions (e.g., “How does event handling work in CAPL?”).
*   You need general CANoe or Vector configuration help (not directly tied to function documentation).
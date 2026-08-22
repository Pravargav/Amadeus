# API Flow Using Postman

```text
┌─────────┐
│ Postman │
└────┬────┘
     │
     │ HTTP Request
     ▼
┌─────────────────┐
│   Weather API   │
└────┬────────────┘
     │
     │ JSON Response
     ▼
┌─────────┐
│ Postman │
└─────────┘

---------------------

┌────────────────┐
│ AI Assistant   │
│ (Copilot/LLM)  │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│   MCP Client   │
└───────┬────────┘
        │ MCP Protocol
        ▼
┌────────────────┐
│   MCP Server   │
└───────┬────────┘
        │
        ├────────► Weather Tool
        │
        ├────────► Database Tool
        │
        └────────► GitHub Tool
                    │
                    ▼
             Tool Response
                    │
                    ▼
┌────────────────┐
│ AI Assistant   │
└────────────────┘

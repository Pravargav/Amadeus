# This content is not about another app trying to access Claude, and it is not about Claude accessing another app specifically.

It is describing how an MCP (Model Context Protocol) client authenticates to an MCP server based on the type of integration.

Think of Claude as the user/client application that wants to use external tools. The MCP server is the bridge to those external systems.

## 1. Remote service with user identity

### Example

- Claude ↔ Linear
- Claude ↔ Jira
- Claude ↔ Google Drive

Here, the MCP server needs to know which user is making the request.

### Flow

1. Claude connects to the MCP server.
2. MCP server responds with `401 Unauthorized`.
3. Claude opens a browser sign-in flow.
4. You log in to Linear/Jira/etc.
5. OAuth token is issued.
6. Claude stores the token and uses it for future requests.

### Analogy

- You open a travel app and connect your Gmail account.
- The app redirects you to Google login.
- After permission is granted, the app can read your emails.

So the identity being used is **your identity**.

```text
You -> Claude -> MCP Server -> Linear
                ^
                OAuth login
```

---

## 2. Remote service with service identity

### Example

- Claude ↔ Internal company API
- Claude ↔ OpenAI API
- Claude ↔ Weather API

Here nobody logs in interactively.

### Instead

1. A service account exists.
2. An API key represents that service account.
3. The API key is stored in an environment variable.
4. Claude/MCP server uses that key when making requests.

### Analogy

- A CI/CD pipeline automatically deploys software.
- No human logs in.
- A secret API key grants access.

```text
Claude -> MCP Server -> Service API
           |
           +-- API Key
```

The identity is the application/service itself, not an individual user.

---

## 3. Local service with file-system access

### Example

- Claude Desktop accessing local files
- MCP server running on your laptop

No network authentication is needed because everything runs locally.

### Security comes from

- Windows/macOS/Linux file permissions
- MCP allow/deny settings

### Analogy

- Notepad opening a file from your Documents folder.
- Notepad doesn't ask for OAuth or API keys.
- The operating system decides whether the file is accessible.

```text
Claude
   |
   +--> Local MCP Server
              |
              +--> Local Files
```

The identity is effectively the local operating-system user account.

---

# In your Claude Enterprise integration tutorial

The tutorial is explaining:

| Scenario | Authentication Method | Identity Used |
|-----------|----------------------|----------------|
| Remote SaaS tool (Linear, Google, Jira) | OAuth | User identity |
| Remote API/service | API Key | Service identity |
| Local MCP server accessing files | OS permissions (stdio) | Local machine user |

---

So when it says:

> "The Linear MCP server uses this pattern"

it means Claude is accessing Linear through an MCP server using your Linear account via OAuth.

When it says:

> "GitHub server authenticates with a personal access token"

it means Claude is accessing GitHub using a GitHub token rather than an OAuth login flow.

The focus of this section is how Claude (or any MCP client) authenticates to external tools/services, not how those tools authenticate to Claude.

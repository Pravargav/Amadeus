## Accelerators & IP Contribution (Claude Developer Certification)

### What is an Accelerator?

An accelerator is a reusable, packaged solution that allows future projects to start from a working foundation instead of building everything from scratch.

In a Claude-based project, you may already have:

- An agent loop
- Configured MCP servers
- Tool integrations
- System prompts
- Evaluation tests
- Working workflows

Instead of rebuilding these components for every customer, you package the reusable portions into an accelerator.

Goal:

> Configure for a new customer instead of rebuilding for a new customer.

This reduces engineering effort, implementation time, onboarding costs, and project risk.

---

### Why Accelerators are Important

Imagine a team delivers a working Claude solution for Customer A.

Without an accelerator:

- Next team copies the repository
- Updates prompts manually
- Edits tool configurations
- Changes paths and credentials
- Recreates evaluations
- Introduces inconsistencies

Result:

- Duplicate work
- Larger maintenance burden
- Multiple diverging versions

With an accelerator:

- Reusable components remain unchanged
- Customer-specific values become configuration
- New deployments happen faster

Result:

- Faster onboarding
- Consistent architecture
- Lower maintenance cost
- Better scalability

---

### Core Principle

Separate:

#### Reusable Core

Parts that remain the same across customers.

Examples:

- Agent loop
- Tool calling logic
- MCP protocol usage
- Evaluation framework
- Retry mechanisms
- Logging patterns

#### Customer-Specific Components

Parts that vary per customer.

Examples:

- System prompts
- API endpoints
- File paths
- Access scopes
- Business rules
- Threshold values
- Dataset locations

These values should be parameterized instead of hardcoded.

---

### Parameterization

Parameterization means replacing hardcoded values with configurable inputs.

Bad Example:

```python
DATA_PATH = "/customerA/files"
```

Good Example:

```python
DATA_PATH = config.data_path
```

Now any future customer can use:

```yaml
data_path: "/customerB/files"
```

without modifying the source code.

---

### Three Common Accelerator Types

#### 1. Agent Template

Packages:

- System prompts
- Tool schemas
- Agent workflow
- Loop structure

Purpose:

Provide a ready-to-use Claude agent that can be configured for different domains.

Correct Packaging:

- Move prompts to configuration
- Move thresholds to configuration
- Move paths to configuration
- Document default values

Instead of editing source code, a new team updates configuration files.

---

#### 2. MCP Server Package

Packages:

- MCP tools
- Tool definitions
- Input contracts
- Resource access patterns

Purpose:

Provide reusable server capabilities.

Correct Packaging:

- Document tool inputs
- Document permissions
- Document scope boundaries
- Allow credential injection
- Allow environment-specific configuration

Goal:

Install the server in a new environment without changing code.

---

#### 3. Eval Suite

Packages:

- Test datasets
- Judge rubrics
- Pass/fail criteria
- Baseline scores

Purpose:

Verify the solution still works after changes.

Correct Packaging:

- Bundle dataset and rubric together
- Document scoring methodology
- Document expected thresholds
- Include baseline performance

Benefits:

- Regression testing
- Quality verification
- Deployment gating

Before releasing a new model version:

1. Run evaluation suite
2. Compare against baseline
3. Verify score remains acceptable
4. Deploy only if quality is maintained

---

### Most Common Packaging Mistake

A team shares:

- Python scripts
- Prompt files
- Configuration spread across folders

The solution technically works but isn't reusable.


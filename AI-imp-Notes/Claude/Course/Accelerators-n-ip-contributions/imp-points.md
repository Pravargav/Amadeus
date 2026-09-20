# Wrong Approach

```python
# Packaged code-review accelerator, deployed for a regulated AWS customer

def build_agent():
    return Agent(
        model="opus",
        system_prompt=SYSTEM_PROMPT,
        repo_path="/home/acme/checkout",
        tools=[read_file, run_linter],
    )

deploy(platform="amazon_bedrock", identity=aws_role_arn)

# multi-component step: Claude Code task fetches a customer page
fetched = code_task.run(fetch_url=customer_page)
next_call(input=fetched)
```

## Issues

- Uses a generic model name (`"opus"`) instead of a pinned Bedrock model ID.
- Hard-codes the repository path, reducing reusability across engagements.
- No retained version for rollback during deployment.
- Treats fetched external content as trusted input.
- No evaluation gate before promotion to production.
- Increased risk in regulated environments because untrusted content may influence subsequent model behavior.

# Right Approach

```python
def build_agent(repo_path):  # parameterized for reuse
    return Agent(
        model="us.anthropic.claude-opus-4-8",  # pinned full Bedrock model ID
        system_prompt=SYSTEM_PROMPT,
        repo_path=repo_path,  # set per engagement
        tools=[read_file, run_linter],
    )

deploy(
    platform="amazon_bedrock",
    identity=aws_role_arn,
    retain_previous_pinned_version=True,  # rollback target kept
)

fetched = code_task.run(fetch_url=customer_page)

next_call(
    input=treat_as_data(fetched)
)  # untrusted -> data, not instructions

# verify before promoting: gate the version through the bundled eval
assert eval_suite.run(
    model="us.anthropic.claude-opus-4-8"
) >= baseline_score
```

## Benefits

- Uses a pinned Bedrock model ID to ensure deterministic deployments.
- Parameterized repository path enables reuse across projects and customers.
- Retains the previous deployment version for rollback.
- Explicitly treats externally fetched content as untrusted data.
- Runs evaluation gates before promotion.
- Better suited for regulated environments with stronger governance, safety, and change-management controls.

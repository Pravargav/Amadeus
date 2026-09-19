## The Template That Shipped Fast and Could Not Be Reused

### What This Scenario Teaches

This case study demonstrates a common mistake in AI and Claude projects:

> Building a solution that works is not the same as building a solution that can be reused.

The first team successfully delivered a working agent template, but they never converted it into a reusable accelerator. As a result, the next team had to rebuild the solution instead of configuring it.

For Claude Developer Certification, this example highlights the importance of:

- Parameterization
- Documentation
- Evaluation
- Reusability

---

### Setup

A team was operating under a strict deadline.

To deliver quickly, they hardcoded several customer-specific values directly into the codebase, including:

- Repository paths
- Model names
- Review thresholds
- Domain-specific prompt text
- Environment settings

The template successfully ran for the customer and the project was completed on time.

Since the solution worked, it was stored in the organization's shared repository and labeled as a reusable template.

At that moment, nobody questioned whether it was actually reusable.

---

### What Happened Later

Several months later, another team attempted to use the same template for a different customer.

They expected to:

1. Update configuration values
2. Adjust prompts
3. Deploy the solution

Instead, they discovered:

- There was no configuration layer.
- Customer-specific values were buried inside code.
- Every important setting was hardcoded.
- Prompt fragments were scattered throughout files.
- Threshold values had no explanation.

The second team had to inspect the entire codebase to determine which values could be changed safely.

Even worse:

- No documentation existed.
- No design assumptions were recorded.
- No evaluation suite was included.

After making modifications, they had no way to verify whether the system still behaved correctly.

Eventually, the team rebuilt the template from scratch.

---

### Root Cause

The build was considered complete when it worked for one customer.

However, reusable assets are not finished when they run.

They are finished when they can be reused by another team with minimal effort.

The original team optimized for:

- Fast delivery

But failed to optimize for:

- Future reuse

---

### The Hardcoding Problem

Hardcoding is often reasonable during initial development.

Example:

```python
MODEL = "claude-sonnet"
REVIEW_THRESHOLD = 0.85
REPOSITORY_PATH = "/customer-a/repo"
```

This helps teams move quickly.

The problem occurs when these temporary shortcuts become permanent.

Months later, another team cannot easily identify:

- Which values are customer-specific
- Which values are core system requirements
- Which values can be modified safely

As a result:

- Changes become risky
- Knowledge becomes trapped in code
- Reuse becomes difficult

---

### Why the Template Failed

The template failed because it lacked the three requirements of a reusable accelerator.

#### Missing Parameterization

Customer-specific values should have been exposed as configuration.

Instead of:

```python
REVIEW_THRESHOLD = 0.85
```

Use:

```python
REVIEW_THRESHOLD = config.review_threshold
```

This allows each customer to provide their own settings without editing source code.

Without parameterization:

- Every new engagement requires code changes.
- Teams duplicate rather than reuse.

---

#### Missing Documentation

The original team never documented:

- Which values were configurable
- Environment assumptions
- Required inputs
- Failure handling
- Deployment requirements

When the second team inherited the asset, they could not determine:

- Why values were chosen
- Which dependencies existed
- What behavior was intentional

Documentation preserves knowledge after the original builders have moved on.

---

#### Missing Evaluation Suite

The template contained no evals.

After modifying values, the second team had no answer to:

> "Does the template still work?"

Without evals:

- Regressions go unnoticed
- Quality cannot be verified
- Refactoring becomes risky

A reusable asset should always include:

- Test dataset
- Judge rubric
- Baseline score
- Pass/fail threshold

This allows future teams to validate changes confidently.

---

### Hidden Cost of the Failure

The original team saved time by hardcoding values.

However, that saved time was lost later.

The second team paid the cost through:

- Code investigation
- Reverse engineering
- Trial-and-error testing
- Rebuilding functionality

The organization paid twice:

1. First to build the template
2. Again to rebuild it

The purpose of an accelerator is to avoid that second cost.

---

### Warning Signs of a Non-Reusable Template

A template is probably not reusable if:

#### Customer Values Are Buried in Code

Examples:

- Paths
- Model names
- API URLs
- Prompt text
- Threshold values

must not be hardcoded.

---

#### No Configuration Layer Exists

If new customers require source-code edits instead of configuration changes, reuse will be difficult.

---

#### No Documentation Exists

If future teams must read code to understand:

- Assumptions
- Inputs
- Dependencies

the asset is not properly packaged.

---

#### No Evaluation Suite Exists

If changes cannot be validated automatically, future teams will hesitate to reuse the asset.

---

### How the Template Should Have Been Packaged

A reusable Claude agent template should include:

#### Configuration

Move customer-specific values into:

```yaml
model: claude-sonnet
review_threshold: 0.85
repository_path: /repos/project
```

---

#### Documentation

Explain:

- Environment assumptions
- Required services
- Inputs
- Outputs
- Error handling
- Deployment process

---

#### Evaluation Suite

Include:

- Test cases
- Expected results
- Judge rubric
- Baseline metrics

This allows future teams to prove the template still works.

---

### Certification Takeaway

For Claude Developer Certification, remember:

> A working template is not automatically a reusable template.

A reusable asset requires three things:

#### 1. Parameterization

Customer-specific values become configuration.

#### 2. Documentation

Assumptions and requirements are clearly explained.

#### 3. Evaluation

A bundled eval proves the asset still works after changes.

Key lesson:

> The best time to package an asset for reuse is immediately after the build is completed, while the knowledge of what is customer-specific is still fresh in the team's mind.

If parameterization, documentation, and evals are missing, the next team will spend more time rebuilding the solution than reusing it, defeating the purpose of an accelerator.

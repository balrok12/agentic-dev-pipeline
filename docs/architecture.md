# Architecture Notes

## Why a pipeline instead of a single code-generation call?

A single LLM call can generate code from a requirement — but it treats the entire problem as one black box.  
As tasks grow in complexity, this approach breaks down in predictable ways:

- The model has no opportunity to clarify ambiguities before writing code.
- There is no structural validation step; errors are discovered only at runtime.
- There is no mechanism to learn from failures within a run.

A pipeline decomposes the problem into distinct stages, each with a clear responsibility and output contract.  
Each stage can be evaluated, replaced, or scaled independently.

---

## Pipeline stages and their rationale

### Analyst
Separating requirement analysis from code generation forces the system to make the implicit explicit.  
Ambiguities in the original requirement surface as gaps in the task list, where they are cheapest to fix.

### Architect
A design step produces a shared contract (data model, endpoint signatures) that the downstream code generator must honour.  
This prevents the common failure mode where generated code invents its own schema and is inconsistent with what was asked for.

### Developer
Code generation is the only truly generative stage. By the time it runs, it has a precise spec rather than a vague intent.  
On retry, it also receives concrete QA feedback, narrowing the search space.

### QA with conditional retry
Automated validation closes the loop within a single run.  
The conditional edge (QA → Developer on failure) is the key structural feature:  
it makes the pipeline self-correcting up to a configurable retry limit, without human intervention.

### Retrospector
A retrospection step produces a structured artefact (one improvement point per cycle) that could be accumulated across runs.  
Over many cycles, this is the foundation for automated prompt or process improvement — without it, failures are silent.

---

## Scaling considerations

As this architecture is extended beyond a demo, several challenges emerge:

**Agent proliferation and consistency**  
With more agents (security review, documentation, test generation), keeping prompt behaviour consistent across agents becomes non-trivial.  
A shared agent contract (input/output schema, tone, failure modes) is necessary before adding agents beyond a handful.

**Validation cost vs. coverage**  
Static syntax and keyword checks are cheap but shallow.  
Deeper validation (type checking, test execution, integration smoke tests) increases quality signal at the cost of latency and infrastructure.  
The right balance depends on the risk profile of what is being generated.

**Retrospection accumulation**  
A single retrospection summary is useful for visibility.  
Making it actionable at scale requires a structured store of past cycles, a retrieval mechanism, and a way to surface relevant past failures when similar requirements recur.

**State and observability**  
LangGraph's explicit state makes it straightforward to log, replay, or diff any run.  
In production, emitting structured events at each node transition is the minimum needed for meaningful debugging and cost tracking.

**Prompt governance**  
As the number of agents and requirements grow, prompt drift becomes a risk — agents that worked well for one domain may degrade on another.  
Versioning prompts alongside code, and evaluating them against a held-out requirement set, is the direction for maintaining quality at scale.

---

## What this demo does not show

This demo intentionally omits:

- Production-grade validation (type checking, test generation, security scanning)
- Multi-squad coordination (multiple developer agents working in parallel)
- Persistent memory across runs
- Deployment or CI/CD integration

These are extensions of the same architecture, not replacements for it.

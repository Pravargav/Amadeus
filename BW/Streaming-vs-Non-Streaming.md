


##### ***Non‑Streaming Process Chain (Traditional BW)***



-> A **batch‑oriented** process chain where **one step finishes completely before the next step starts**.

Each process waits for the **full data load** to complete.



-> How it works

1.  Extract data from source
2.  Load to PSA
3.  Transform and load into DSO / ADSO
4.  Activate data
5.  Roll up / update cubes
6.  Trigger reporting or next chain

Example:

```text
Source → PSA → DSO (complete) → DSO activation → Cube
```




##### ***Streaming Process Chain***



-> A **data‑flow‑oriented** process chain where **records are processed as soon as they arrive**, without waiting for the full dataset.

Also called **real‑time / near‑real‑time processing**.



-> How it works

*   Data moves record‑by‑record or in small packets
*   Downstream steps start **while upstream steps are still running**

Example:

```text
Source → PSA → ADSO → Reporting (simultaneously)
```


##### Comparison

| Aspect            | Non‑Streaming         | Streaming                  |
| ----------------- | --------------------- | -------------------------- |
| Processing type   | Batch                 | Real‑time / Near real‑time |
| Execution         | Sequential            | Parallel / Continuous      |
| Data availability | After full completion | Almost immediately         |
| Latency           | High                  | Low                        |
| Complexity        | Low                   | High                       |
| Error handling    | Simple                | Complex                    |
| Typical usage     | Night batch, finance  | Dashboards, live analytics |

***





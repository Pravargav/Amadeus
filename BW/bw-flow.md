🧩 SAP BW Flow (sap_bw_flow.md)

````markdown
Mermaid
flowchart TD
    A[Source System<br/>(ECC / S4 / Flat File)]
    A --> B[InfoObjects<br/>(Characteristics & Key Figures)]
    B --> C[ADSO<br/>(Inbound / Active / Change Log)]
    C --> D[RSPM<br/>(Request Status and Process Manager )]
    D --> E[Reporting<br/>(Query / SAC / BO)]
````
    
🧩 Node.js Flow (nodejs_flow.md)

````markdown
Mermaid
flowchart TD
    A[API / Source System<br/>(REST / File / Event)] 
    A --> B[Schema Fields<br/>(Model / DTO)]
    B --> C[Database Collection<br/>(MongoDB / SQL)]
    C --> D[Job Queue / Logger<br/>(Bull / PM2 / Cron)]
    D --> E[Dashboard / UI<br/>(React / Power BI)]
````

-> https://community.sap.com/t5/technology-blog-posts-by-members/a-replacement-for-rspcm-process-chain-monitoring-from-st13-ssa-bwt-program/ba-p/12886371

| Feature        | RSPC                     | RSPM (via ST13/SSA/BWT) |
|---------------|--------------------------|-------------------------|
| Main Function | Maintenance & Development | Monitoring & Support   |

Note: RSPCM is an older, often slower, monitoring transaction that requires manual additions, while RSPM (via ST13/SSA/BWT) is generally preferred for performance reasons.

-> ***Process (Process Variant / Step)*** - 
A Process is a single step within a Process Chain. It is the modularization of a technical action (e.g., "Delete Data from Target", "Activate Data"). 

-> ***Process Chain (RSPC)*** - 
A Process Chain is a sequence of Processes (steps) that are scheduled to wait for an event, automatically triggering the next step upon successful completion of the previous one. 


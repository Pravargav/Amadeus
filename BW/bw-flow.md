🧩 SAP BW Flow (sap_bw_flow.md)
Copy code
Mermaid
flowchart TD
    A[Source System<br/>(ECC / S4 / Flat File)] --> B[InfoObjects<br/>(Characteristics & Key Figures)]
    B --> C[ADSO<br/>(Inbound / Active / Change Log)]
    C --> D[RSPM<br/>(Request & Process Management)]
    D --> E[Reporting<br/>(Query / SAC / BO)]
🧩 Node.js Flow (nodejs_flow.md)
Copy code
Mermaid
flowchart TD
    A[API / Source System<br/>(REST / File / Event)] --> B[Schema Fields<br/>(Model / DTO)]
    B --> C[Database Collection<br/>(MongoDB / SQL)]
    C --> D[Job Queue / Logger<br/>(Bull / PM2 / Cron)]
    D --> E[Dashboard / UI<br/>(React / Power BI)]

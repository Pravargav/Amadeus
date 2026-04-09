
## 1. RFC (Remote Function Call)
**RFC** is SAP’s standard communication mechanism used to connect:
- SAP ↔ SAP systems 
- SAP- SAP ↔ non‑SAP systems 

### Key Uses
- Data transfer 
- System integration 
- Background job communication 
- BW data extraction 
- SLT, BW, S/4HANA, and third‑party integrations

---

## 2. SDA (Smart Data Access)
**SDA** is an SAP HANA feature that enables **virtual access** to external/remote data **without loading it physically** into HANA.

### Supported External Databases
- Oracle 
- SQL Server 
- Hadoop 
- *SAP IQ*

***Note: IQ Systems (SAP IQ)***
[SAP IQ is a columnar, high‑performance analytical database with use cases below:

##### Primary Use Cases
- Nearline Storage (NLS) 
- Warm data archiving 
- Long‑term data retention 
- Offloading historical BW requests to reduce HANA memory usage]

### Purpose
- Real‑time data federation 
- Reduced data replication 
- Hybrid modeling in BW/4HANA

---





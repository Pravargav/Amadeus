
#### Upload vs Import vs Export in SAP Analytics Cloud (SAC)

SAP Analytics Cloud (SAC) provides three main data management operations: **Upload**, **Import**, and **Export**.  
Although they seem similar, each serves a different purpose in how data moves in and out of SAC.

---

##### 📤 1. Upload (File Upload)

##### **What it means**
Upload is used to bring data **from your local computer** into SAC using files.

##### **Supported Formats**
- `.xlsx` (Excel)
- `.csv` (Comma‑separated)

##### **Where Upload is used**
- Updating/adding data to a **Planning Model**
- Loading **master data** or **transaction data**
- Working with **Datasets**

##### **Typical Use Cases**
- Initial load of historical data  
- Uploading master data like Product, Customer, Region  
- Manually adding planning data using Excel  

##### **Direction**
**Local Machine → SAC**

---

#### 🔽 2. Import (Connected System Import)

##### **What it means**
Import is used to load data into SAC **from external systems** using live or acquired data connections.

##### **Supports connections from**
- SAP **S/4HANA**
- SAP **BW / BW4HANA**
- SAP **HANA**
- SAP **Datasphere**
- **OData** services
- Other backend systems configured via connection

##### **Where Import is used**
- Automated / scheduled refresh of actuals  
- Importing master data from enterprise systems  
- Integrating SAC planning with operational systems  

##### **Typical Use Cases**
- Pulling Actuals from BW into a Planning model  
- Scheduled monthly refresh from S/4HANA  
- Loading hierarchies or master data from Datasphere  

##### **Direction**
**External System → SAC (via connection)**

---

##### 📤 3. Export (Data Write‑Out)

##### **What it means**
Export sends data **out of SAC**, either to a file or back to another SAP system.

##### **Export Options**
- Export as Excel/CSV  
- Export to **S/4HANA**, **BW**, **Datasphere**  
- Data Actions for **write‑back** scenarios  

##### **Where Export is used**
- Sending planning/budget data back to ERP systems  
- Sharing SAC data with external teams  
- Auditing and external reporting  

##### **Typical Use Cases**
- Writing forecast data back to S/4HANA  
- Downloading model data for offline analysis  
- Extracting data for auditors or business users  

##### **Direction**
**SAC → External System / Local File**

---

##### 🔍 Quick Comparison Table

| Operation | Direction | Source | Destination | Purpose |
|----------|-----------|---------|-------------|---------|
| **Upload** | Local → SAC | Excel/CSV | SAC Model or Dataset | Manual file-based loading |
| **Import** | System → SAC | SAP BW, S/4, HANA, Datasphere | SAC Model | Scheduled/automated integration |
| **Export** | SAC → File/System | SAC Model | Excel, S/4, BW, Datasphere | Write-back and external reporting |

---
👉 Live = Real-time (no storage)

👉 Acquired = Stored (imported data)


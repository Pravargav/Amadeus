##  1. RC (Return Code)
Indicates the execution status of a background job, process chain step, or program.

| RC Value | Meaning |
|----------|----------|
| **0** | Success — no issues |
| **4** | Warning — minor issues but completed |
| **8** | Error — process failed |
| **12/16** | Serious error — terminated |

---

##  2. Change Number (ECN – Engineering Change Number)
Used for version-controlled changes to materials, BOMs, documents, and routings.

**Purpose:**
- Controls *valid-from* date of changes 
- Tracks who changed what 
- Provides version management 
- Ensures structured engineering change control 

**Key Transactions:**
- **CC01** – Create Change Number 
- **CC02** – Change 
- **CC03** – Display 

---

##  3. TR (Transport Request)
Used to move configuration or development objects across SAP systems:

**DEV → QA → PROD**

**Types:**
- **Workbench TR** – ABAP programs, tables, DDIC objects 
- **Customizing TR** – SPRO configuration changes 

**Key Transactions:**
- **SE09** – Workbench- **SE09** – Workbench Organizer 
- **SE10** – Transport Organizer 

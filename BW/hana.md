
***

#### ✅ 1. BW on HANA

👉 **Definition:**  
Traditional SAP BW system running on **HANA database instead of old databases (like Oracle, DB2)**

***

##### 🔹 Key idea:

> “Same old BW → just database changed to HANA”

***

##### 🔹 Features:

*   Existing BW objects remain:
    *   InfoCubes ✅
    *   DSOs ✅
    *   Multiproviders ✅
*   Only **performance improves** (due to HANA)

***

##### 🔹 Example:

    Classic BW 7.0 → migrated to HANA

👉 No redesign, just migration

***

##### ✅ Use case:

*   When company wants **quick migration**
*   Minimal changes required

***

#### ✅ 2. BW for HANA

👉 **Definition:**  
Optimized version of BW **redesigned specifically for HANA**

***

##### 🔹 Key idea:

> “New BW model → built to fully use HANA power”

***

##### 🔹 Features:

*   New modeling objects:
    *   ADSO ✅ (replaces DSO + InfoCube)
    *   Composite Provider ✅
    *   Open ODS Views ✅
*   Old objects become **obsolete**
*   Push-down logic to HANA (processing in DB)

***

##### 🔹 Example:

    Using ADSO instead of InfoCube
    Using CompositeProvider instead of MultiProvider

***

##### ✅ Use case:

*   New BW implementations
*   Performance-critical analytics
*   Modern architecture

***

#### ✅ Key Differences 🔥

| Feature      | BW on HANA          | BW for HANA     |
| ------------ | ------------------- | --------------- |
| Concept      | Migration           | Redesign        |
| Database     | HANA                | HANA            |
| Data Models  | Old (InfoCube, DSO) | New (ADSO, CP)  |
| Optimization | Limited             | Fully optimized |
| Effort       | Low                 | High            |
| Performance  | High                | Very High       |

***

#### ✅ Simple Memory Trick 🔥

👉 **BW on HANA = “Lift & Shift”**  
👉 **BW for HANA = “Rebuild for HANA”**

***

#### ✅ Real Project Understanding (Amadeus-like scenario ✈️)

##### BW on HANA:

*   Existing flight reports
*   Just faster after migration

***

##### BW for HANA:

*   Redesigned data model:
    *   Booking ADSO
    *   Revenue ADSO
    *   Composite Provider for analytics

👉 Built for **real-time analytics**

***


> **Old BW objects vs New BW/HANA objects**


#### ✅ OLD BW (Classic)

👉 Uses: **InfoCube, DSO, MultiProvider, InfoObject**

***

##### 🔹 1. InfoObject

*   Smallest unit (field)
*   Example: `CUSTOMER`, `MATERIAL`

✅ Same in both old & new BW

***

##### 🔹 2. InfoCube

👉 Used for **reporting (OLAP)**

*   Star schema
*   Fact + Dimension tables
*   Optimized for analysis

✅ Example:
Sales cube with:

*   Customer
*   Product
*   Sales amount

***

##### 🔹 3. DSO (Data Store Object)

👉 Used for **detailed storage**

*   Stores granular data
*   Supports overwrite/update
*   3 tables (active, change log, new)

✅ Example:
Daily sales transaction data

***

##### 🔹 4. MultiProvider

👉 Used for **combining multiple providers**

*   Combines InfoCubes + DSOs
*   Logical union (no data storage)

✅ Example:
Sales + target combined view

***

#### ✅ NEW BW (BW on HANA / BW/4HANA)

👉 Uses: **InfoObject, ADSO, Composite Provider**

***

##### 🔹 1. InfoObject

✅ SAME as before  
(No change)

***

##### 🔹 2. ADSO (Advanced DSO)

👉 **Replaces BOTH InfoCube + DSO**

*   Stores data
*   Supports reporting ✅
*   Supports updates ✅
*   Multiple modeling types

✅ Example:
Single ADSO for:

*   Transaction data
*   Reporting

***

##### 🔹 3. Composite Provider

👉 **Replaces MultiProvider**

*   Combines ADSOs / other sources
*   Used for reporting layer
*   More powerful & flexible

✅ Example:
Sales + target combined

***



#### ✅ KEY DIFFERENCE (MOST IMPORTANT 🔥)

| Concept       | Old BW                | New BW                |
| ------------- | --------------------- | --------------------- |
| Data models   | Separate (Cube + DSO) | Unified (ADSO)        |
| Complexity    | High                  | Simplified            |
| Performance   | Moderate              | High (HANA optimized) |
| Objects count | More                  | Less                  |

***

#### ✅ SIMPLE MEMORY TRICK 🧠

👉 **Old BW = IC + DSO + MP (Many objects)**  
👉 **New BW = ADSO + CP (Simplified)**

***

#### ✅ VISUAL FLOW

##### 🔴 Old BW:

    InfoObject
       ↓
    DSO → InfoCube → MultiProvider → Report

***

##### 🟢 New BW:

    InfoObject
       ↓
    ADSO → Composite Provider → Report

***

#### ✅ REAL PROJECT UNDERSTANDING (Amadeus ✈️)

##### Old BW:

*   Booking data → DSO
*   Reporting → InfoCube
*   Combined → MultiProvider

***

##### New BW:

*   Booking data → ADSO
*   Combined → Composite Provider

👉 Less layers, faster queries 🚀

***







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




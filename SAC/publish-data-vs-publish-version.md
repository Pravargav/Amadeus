In **SAP Analytics Cloud (SAC)**, **“Publish Data”** and **“Publish Story”** sound similar but work at **completely different levels**. This is a **very common interview + real-time confusion**, so let’s lock it down clearly.

---

# 🔹 Publish **Data** vs Publish **Story** in SAC

## 1️⃣ Publish **Data**

### ✅ What it means

* Moves **data** from a **Private Version → Public Version**
* Applies to **Planning Models**
* Changes **planning numbers** in the model (not Actuals)

### 📌 Where you see it

* In **planning stories**
* When working with **versions**

### 🧠 Key idea

> **Data is getting committed**

### 🧪 Example

* You adjust forecast revenue in your **Private Version**
* Click **Publish Data**
* Now everyone sees updated numbers in **Public Version**

### ⚠️ Important

* Affects **reports, other stories, publications**
* Requires **write permission**
* Can trigger **data locks / validations**

---

## 2️⃣ Publish **Story**

### ✅ What it means

* Makes the **story object** visible to others
* Does **NOT change data**
* Only affects **access & visibility**

### 📌 Where you see it

* When saving / sharing a story
* Content management level

### 🧠 Key idea

> **Layout is shared, data stays same**

### 🧪 Example

* You design a dashboard
* Click **Publish Story**
* Others can now open the same dashboard

### ⚠️ Important

* No data write-back
* No impact on versions
* Works for **both planning & analytic stories**

---

## 🔥 Side-by-Side Comparison (Very Exam-Friendly)

| Aspect                | Publish **Data** | Publish **Story**       |
| --------------------- | ---------------- | ----------------------- |
| What is published     | Numbers          | Story (layout, widgets) |
| Impacts model data    | ✅ Yes            | ❌ No                    |
| Version involved      | Private → Public | Not applicable          |
| Used in               | Planning         | Analytics & Planning    |
| Requires write access | ✅ Yes            | ❌ No                    |
| Affects other stories | ✅ Yes (data)     | ❌ No                    |
| Similar to            | Save to PROD     | Share report            |

---



# Publish Data in SAC – Does It Change Actuals?

## ❓ Question

**When we publish data in SAP Analytics Cloud (SAC), do the values in the Actuals version get changed?**

---

## ✅ Short Answer

**❌ No — publishing data does NOT change the Actuals version.**

---

## 🔹 What *Publish Data* Actually Does

When you click **Publish Data** in SAC:

* Data moves from **Private Version → Public Version**
* Works **within the same version**
* Applies mainly to **Planning Models**
* Commits planning numbers so others can see them

📌 Example:

```
Private Forecast
      │
      ▼  Publish Data
Public Forecast
```

---

## 🚫 What Publish Data Does **NOT** Do

| Item                      | Changed? |
| ------------------------- | -------- |
| Actuals version data      | ❌ No     |
| Historical actual data    | ❌ No     |
| Data loaded from BW / S/4 | ❌ No     |

➡️ **Actuals remain untouched**

---

## 🧠 Why Actuals Are Not Changed

### 1️⃣ Actuals Are Usually Read-Only

* Loaded from:

  * SAP BW
  * SAP S/4HANA
  * Flat files / data imports
* Treated as the **source of truth**

### 2️⃣ Publish Works Only *Within a Version*

* Private Forecast → Public Forecast
* Private Budget → Public Budget

❌ Never:

```
Private Version → Actuals
```



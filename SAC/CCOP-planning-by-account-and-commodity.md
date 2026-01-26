# SAP SAC Planning – Account View vs Procurement (Commodity) View

In **SAP SAC (Planning)**, planning data is structured and analyzed using **different business dimensions**. 
Simply put, it’s about **“which lens you plan from.”**

---

## 1️⃣ Planning by **Account**

Planning is driven by the **Account dimension** (types of costs). 
This view is mainly used by **Finance teams** for **budgeting, cost control, and GL-level planning**.

### Accounts Explained

### 🔹 Internal FTEs
- Cost of **employees on company payroll**
- Includes:
  - Salaries
  - Bonuses
  - Benefits
- Example: Permanent employees

---

### 🔹 External FTEs
- Cost of **contractors, vendors, or consultants**
- Not on company payroll
- Example: Third-party developers or consultants

---


### 🔹 Non-Labour
- Costs **not related to people**
- Examples:
  - Software licenses
  - Cloud services
  - Office rent
  - Utilities

---

### 🔹 CapEx (Capital Expenditure)
- Long-term investments
- Examples:
  - Servers
  - Hardware
  - Buildings
- These costs are **capitalized** and **depreciated over time**

📌 **Use Case:** 
Finance wants to know: 
> *“How much are we spending on each cost type?”*

---

## 2️⃣ Planning by **Commodity**

Planning is driven by the **Commodity dimension** (what is being purchased). 
This view is typically used by **Procurement and Operations teams**.

### Commodities Explained

### 🔹 Non-Labour
- Purchased goods or services
- Examples:
  - Software subscriptions
  - Cloud infrastructure
  - Maintenance services

---

### 🔹 CapEx
- Physical or long-term assets
- Examples:
  - Machines
  - Network equipment
  - Office infrastructure

📌 **Use Case:** 
Procurement wants to know: 
> *“What are we buying and how much?”*

---

##  Why Both Views Exist in SAC

| Aspect | Planning by Account | Planning by Commodity |
|------|-------------------|----------------------|
| Driven by | Finance (GL view) | Procurement view |
| Focus | Cost type | Purchase type |
| Labour costs | Included |  Not included |
| Non-Labour | Included | Included |
| CapEx | Included | Included |

👉 **Labour costs (Internal / External FTEs)** 
- Relevant only at the **Account level**

👉 **Non-Labour & CapEx** 
- Relevant in **both views**, but used by different business teams

---

##  Simple Example

### Buying laptops for employees

**Planning by Account**
- Account → CapEx → ₹50 lakhs

**Planning by Commodity**
- Commodity → IT Hardware → ₹50 lakhs

➡ Same cost, **different planning lens**

---




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

### 🔹 CBS (Cost Breakdown Structure)
- A **grouping structure** to categorize costs
- Used to:
  - Track costs at a higher level
  - Compare **Actual vs Plan**
- Examples:
  - IT costs
  - HR costs
  - Travel costs

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

## 3️⃣ Why Both Views Exist in SAC

| Aspect | Planning by Account | Planning by Commodity |
|------|-------------------|----------------------|
| Driven by | Finance (GL view) | Procurement view |
| Focus | Cost type | Purchase type |
| Labour costs | Included | ❌ Not included |
| Non-Labour | Included | Included |
| CapEx | Included | Included |

👉 **Labour costs (Internal / External FTEs)** 
- Relevant only at the **Account level**

👉 **Non-Labour & CapEx** 
- Relevant in **both views**, but used by different business teams

---

## 4️⃣ Simple Example

### Buying laptops for employees

**Planning by Account**
- Account → CapEx → ₹50 lakhs

**Planning by Commodity**
- Commodity → IT Hardware → ₹50 lakhs

➡ Same cost, **different planning lens**

---

## 🔑 Key Takeaways

- **Account-based planning** = *What type of cost?*
- **Commodity-based planning** = *What are we buying?*
- SAC supports both to satisfy **Finance and Procurement** needs

---

# Procurement View & Purchase Type in SAP SAC

In **SAP SAC / Enterprise Planning**, these are **business views**, not technical terms.

---

## 1️⃣ What is **Procurement View**

The **Procurement View** looks at planning data **from a purchasing perspective**, rather than a finance perspective.

### Focus Areas
- What is being bought
- From whom (vendor)
- In what quantity
- For what purpose

Procurement teams think in terms of **materials, services, and assets**, not GL accounts.

### Procurement View Answers:
- What goods or services are we buying?
- How much budget is required?
- Is the spend **OpEx or CapEx**?
- Which vendor or category does it belong to?

### Typical Dimensions in Procurement View
- Commodity
- Vendor
- Category
- Purchase Type
- Cost Center / Project

---

## 2️⃣ What is **Purchase Type**

**Purchase Type** defines **how a purchase is treated financially and operationally**.

It classifies spending into broad categories.

### Common Purchase Types

### 🔹 Non-Labour
- Purchases not related to employees
- Examples:
  - Software licenses
  - Cloud services (AWS, Azure)
  - Office rent
  - Travel and utilities

---

### 🔹 CapEx (Capital Expenditure)
- Purchases that create long-term assets
- Capitalized on the balance sheet
- Examples:
  - Servers
  - Laptops
  - Machinery
  - Network equipment

📌 **Important:** 
Purchase Type is **not the same as Account**, but it **maps to Finance accounts**.

---

## 3️⃣ Procurement View vs Finance (Account) View

| Aspect | Procurement View | Finance / Account View |
|------|-----------------|------------------------|
| Main user | Procurement team | Finance team |
| Focus | What is purchased | How cost is booked |
| Dimension | Commodity / Purchase Type | Account |
| Language | Business items | GL / Cost Elements |
| Example | “Buy cloud services” | “Non-Labour expense account” |

---

## 4️⃣ Real-Life Example

### Buying cloud services

**Procurement View**
- Commodity → Cloud Services
- Purchase Type → Non-Labour
- Vendor → AWS
- Amount → ₹20 lakhs

**Finance View**
- Account → IT Services Expense
- Cost Center → IT
- Amount → ₹20 lakhs

➡ Same spend, **two different lenses**

---

## 5️⃣ Why SAP SAC Uses Purchase Type

Purchase Type helps to:
- Standardize planning across teams
- Separate **OpEx vs CapEx**
- Enable approval workflows
- Support reporting and variance analysis
- Map procurement planning to finance accounts automatically

---

## 6️⃣ One-Line Summary

- **Procurement View** = *Planning by what you buy*
- **Purchase Type** = *How that purchase is financially classified* 

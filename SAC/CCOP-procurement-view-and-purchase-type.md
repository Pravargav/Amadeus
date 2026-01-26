# Procurement View & Purchase Type in SAP SAC

In **SAP SAC / Enterprise Planning**, these are **business views**, not technical terms.

---

## 1️⃣ What is **Procurement View**

The **Procurement View** looks at planning data **from a purchasing perspective**, rather than a finance perspective.




Procurement teams think in terms of **materials, services, and assets**, not GL accounts.

### Procurement View Answers:
- What goods or services are we buying?
- How much budget is required?
- Is the spend **OpEx or CapEx**?
- Which vendor or category does it belong to?
- Quantity of the goods or services we are buying?
- For what purpose we are buying?

### Typical Dimensions in Procurement View
- Commodity
- Vendor
- Category
- Purchase Type
- Project 

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

##  Procurement View vs Finance / Account View

| Aspect | Procurement View | Finance / Account View |
|------|-----------------|------------------------|
| Main user | Procurement team | Finance team |
| Focus | What is purchased | How cost is booked |
| Dimension | Commodity / Purchase Type | Account |
| Language | Business items | GL / Cost Elements |
| Example | “Buy cloud services” | “Non-Labour expense account” |

---

##  Real-Life Example

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




**Note**: Use st22 for dumps and sm21 for system logs

### RFC User vs Normal Employee User in ST22

#### RFC User
- Used for **system-to-system communication**.
- User type in **SU01**: `System`, `Communication`, or `Service`.
- Typically associated with:
  - BW loads
  - Process chains
  - Interfaces
  - RFC calls
  - Background jobs
- Common examples: `ALEREMOTE`, `BWREMOTE`, `RFC_*`, technical service accounts.
- Dumps usually indicate an integration or interface issue.

#### Normal Employee User
- Used by employees for daily SAP activities.
- User type in **SU01**: `Dialog`.
- Executes transactions directly via SAP GUI/Fiori.
- Examples: Personal user IDs such as `P123456`, `JSMITH`.
- Dumps are typically caused by manual execution of reports, queries, or transactions.

#### How to Identify in ST22
1. Open the dump.
2. Check the **User** field under *User and Transaction Information*.
3. Verify the user in **SU01**:
   - `Dialog` → Employee User
   - `System` / `Communication` / `Service` → RFC or Technical User
4. Review the transaction/program:
   - RFC calls, background processing, BW loads → RFC User
   - Business transactions (e.g., RSA1, SE38, VA01, FB03) → Employee User
----------------------------------------------------------------------------------------------------------------
#### RC (Return Code)
Indicates the execution status of a background job, process chain step, or program.

| RC Value | Meaning |
|----------|----------|
| **0** | Success — no issues |
| **4** | Warning — minor issues but completed |
| **8** | Error — process failed |
| **12/16** | Serious error — terminated |
----------------------------------------------------------------------------------------------------------------
### RFC Error and Its Relation to Qlik

The error *"CPIC-CALL ThCMSEND CM_DEALLOCATED_NORMAL"* in your Qlik connection is related to **RFC connectivity issues**, particularly in the context of SAP's Support Backbone infrastructure changes.

#### Key Information About RFC Shutdown

SAP completely shut down **RFC connections from customer systems to SAP** on **November 30, 2020**. This affects RFC destinations such as:

- `SAPNET_RTCC`
- `SDCC_OSS`
- `SAP-OSS`
- `SAPOSS`

#### Resolution Steps

##### 1. For Systems with SAP_BASIS 7.40 or Higher

- Establish a direct **HTTPS** connection to SAP Support Backbone.
- Ensure the **Service Data Manager (SDCCN)** is active (refer to SAP Note 763561).
- Follow **SAP Note 2923799** for final RFC shutdown guidance.

##### 2. For Systems with SAP_BASIS ≤ 7.31

Use one of the following indirect connectivity options through a hub system:

###### Via Solution Manager 7.2
- Reuse the existing SDCCN setup.
- Configure RFC destinations `SM_*_BACK`.

###### Via Solution Manager 7.1
- Implement **SAP Note 2837310**.
- Enable HTTP-based connectivity to SAP Support Backbone.

###### Via Focused Run (FRUN)
- Requires:
  - ST-A/PI level ≥ `01T* SP02`
  - ST-PI 740 ≥ `SP11`

##### 3. Check Your Current Setup

- Verify RFC destination configuration.
- Ensure deprecated RFC connections are not being used.
- Validate connectivity to SAP Support Backbone.

#### Relation to Qlik

If Qlik is connecting to SAP through an RFC destination that has been deprecated or deactivated, the connection may fail with errors such as:

```text
CPIC-CALL ThCMSEND CM_DEALLOCATED_NORMAL
```

This typically indicates that the communication channel has been terminated or is no longer supported. Migrating the connection to **HTTPS-based communication** is required to restore connectivity.

#### Summary

The error is most likely caused by an attempt to use an RFC-based connection that has been deactivated following SAP's RFC Support Backbone shutdown. To resolve the issue, migrate the connectivity to **HTTPS-based communication**, verify your RFC destinations, and implement the relevant SAP Notes based on your SAP_BASIS release.
``

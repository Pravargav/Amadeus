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

----------------------------------------------------------------------------------------
### RFC Error and Its Relation to Qlik

#### Error Description

The error:

```text
CPIC-CALL: 'ThCMSEND', communication rc: CM_DEALLOCATED_NORMAL (cmRc=18)
```

generally indicates that the **RFC connection was deallocated normally**, meaning the communication session was terminated while the RFC call was still in progress.

In many cases, this is not a system failure but rather a connection that was closed before all data could be transmitted or received.

#### Common Causes

1. Session Terminated During RFC Processing

2. Network Connectivity Issues

3. SAP Gateway Issues

4. SAP Kernel Issues

5. RFC Destination Configuration Problems

#### Troubleshooting Steps

##### Check SAP Gateway Logs
- Use transaction **SMGW**.
- Review gateway logs and trace files.
- Activate gateway statistics if additional diagnostics are required.

##### Verify RFC Destinations
- Use transaction **SM59**.
- Test:
  - Connection
  - Authorization
  - Remote logon
- Ensure all destination parameters are valid.

##### Review Network Connectivity
- Check for:
  - Packet loss
  - Firewall interruptions
  - DNS resolution issues
  - VPN/network instability

##### Update SAP Kernel
- Verify the current kernel patch level.
- Apply recommended SAP kernel patches if known RFC issues exist.

##### Monitor RFC Load
- Check whether parallel RFC executions or heavy workloads are impacting connectivity.
- Review work process utilization and gateway performance.

#### Additional RFC Scenarios

##### Heavy Load / Parallel RFC Processing

Under high system load, RFC-related errors such as:

```text
CALL_FUNCTION_SEND_ERROR
```

may occur due to gateway or kernel limitations.

Recommended actions:
- Apply SAP-recommended kernel patches.
- Reduce excessive parallel RFC execution.
- Monitor gateway resources.

##### Large Data Transfers (SAP APO and Similar Scenarios)

Large deployment packages may cause RFC connection loss.

Possible mitigations:
- Reduce package size.
- Adjust deployment runtime parameters.
- Use parallel processing profiles where appropriate.

#### Recommended Actions for Qlik Integrations

1. Verify the RFC destination in **SM59**.
2. Check SAP gateway logs in **SMGW**.
3. Review Qlik connector logs for timeout or cancellation events.
4. Validate network stability between Qlik and SAP.
5. Apply the latest SAP kernel patches.
6. Avoid manually terminating sessions during data extraction.
7. Test with smaller data volumes if the issue occurs during large loads.

#### Summary

The error **CM_DEALLOCATED_NORMAL (cmRc=18)** usually indicates that an RFC session was closed normally before processing completed. In Qlik integrations, it often points to a prematurely terminated connection caused by user cancellation, network interruptions, timeout issues, gateway problems, or RFC configuration defects. Reviewing SM59, SMGW, network connectivity, and SAP kernel levels is recommended for root cause analysis.


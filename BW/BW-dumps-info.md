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


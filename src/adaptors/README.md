# Outlook Adaptor

This adaptor allows the Agentic RAG system to use emails from a Microsoft Outlook account as a data source. It uses the Microsoft Graph API with the Client Credentials flow, which is suitable for headless or daemon applications running in a secure, non-interactive environment.

## Setup and Configuration

To use this adaptor, you need to register an application in Azure Active Directory (Azure AD), create a client secret, and grant it the necessary **application permissions** to read emails.

### 1. Register an Application in Azure AD

1.  **Go to the Azure Portal**: Log in to [https://portal.azure.com](https://portal.azure.com).
2.  **Navigate to Azure Active Directory**: You can search for it in the search bar.
3.  **Go to App registrations**: In the left-hand menu, click on "App registrations".
4.  **New registration**: Click on the "+ New registration" button.
5.  **Name your application**: Give it a descriptive name, e.g., "Faryx-OutlookReader".
6.  **Supported account types**: Select "Accounts in this organizational directory only (Default Directory only - Single tenant)".
7.  **Register**: Click the "Register" button. You don't need a Redirect URI for this flow.

### 2. Get Credentials

After the app is registered, you will be taken to its overview page. You need to copy two values from here:

*   **Application (client) ID**: This is your `OUTLOOK_CLIENT_ID`.
*   **Directory (tenant) ID**: This is your `OUTLOOK_TENANT_ID`.

### 3. Create a Client Secret

1.  **Go to Certificates & secrets**: In the left-hand menu of your app registration.
2.  **New client secret**: Click on "+ New client secret".
3.  **Description**: Give it a description, e.g., "Faryx-Secret".
4.  **Expires**: Choose an expiration period.
5.  **Add**: Click the "Add" button.
6.  **Copy the secret value**: **Immediately copy the "Value" of the secret.** This is your `OUTLOOK_CLIENT_SECRET`. You will not be able to see it again after you leave this page.

### 4. Grant API Permissions

For a headless application, you need to grant **Application permissions**, not Delegated permissions.

1.  **Go to API permissions**: In the left-hand menu of your app registration.
2.  **Add a permission**: Click on "+ Add a permission".
3.  **Select Microsoft Graph**: Choose "Microsoft Graph".
4.  **Application permissions**: Select "Application permissions".
5.  **Find and add permissions**:
    *   Search for `Mail`.
    *   Select `Mail.Read`. This allows the application to read mail in all mailboxes without a signed-in user.
6.  **Grant admin consent**: After adding the permission, you **must** grant admin consent. Click the "Grant admin consent for [Your Directory Name]" button. The status should change to "Granted for...".

### 5. Configure Your Environment

Create a `.env` file in the root of the project and add the credentials you copied:

```
# The Application (Client) ID from your Azure AD app registration.
OUTLOOK_CLIENT_ID="your-application-client-id"

# The Client Secret value you created in Azure AD.
OUTLOOK_CLIENT_SECRET="your-client-secret-value"

# The Directory (Tenant) ID from your Azure AD app registration.
OUTLOOK_TENANT_ID="your-directory-tenant-id"

# The email address of the user whose mailbox you want to read.
# e.g., "user@yourdomain.com"
OUTLOOK_USER_PRINCIPAL_NAME="user-email-address-to-read"
```

### 6. Running with the Outlook Adaptor

You can now run the main application and specify `outlook` as the data source:

```bash
python main.py "Your query about your emails" --source outlook
```

The application will use the configured credentials to authenticate and fetch emails from the specified user's mailbox non-interactively.

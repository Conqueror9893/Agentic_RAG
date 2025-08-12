# Outlook Adaptor

This adaptor allows the Agentic RAG system to use emails from a Microsoft Outlook account as a data source. It uses the Microsoft Graph API to fetch emails.

## Setup and Configuration

To use this adaptor, you need to register an application in Azure Active Directory (Azure AD) and grant it the necessary permissions to read emails.

### 1. Register an Application in Azure AD

1.  **Go to the Azure Portal**: Log in to [https://portal.azure.com](https://portal.azure.com).
2.  **Navigate to Azure Active Directory**: You can search for it in the search bar.
3.  **Go to App registrations**: In the left-hand menu, click on "App registrations".
4.  **New registration**: Click on the "+ New registration" button.
5.  **Name your application**: Give it a descriptive name, e.g., "AgenticRAG-OutlookReader".
6.  **Supported account types**: Select "Accounts in this organizational directory only (Default Directory only - Single tenant)".
7.  **Redirect URI (optional)**:
    *   Select "Public client/native (mobile & desktop)".
    *   Use the URI `http://localhost`.
8.  **Register**: Click the "Register" button.

### 2. Get Credentials

After the app is registered, you will be taken to its overview page. You need to copy two values from here:

*   **Application (client) ID**: This is your `OUTLOOK_CLIENT_ID`.
*   **Directory (tenant) ID**: This is your `OUTLOOK_TENANT_ID`.

### 3. Grant API Permissions

1.  **Go to API permissions**: In the left-hand menu of your app registration.
2.  **Add a permission**: Click on "+ Add a permission".
3.  **Select Microsoft Graph**: Choose "Microsoft Graph".
4.  **Delegated permissions**: Select "Delegated permissions".
5.  **Find and add permissions**:
    *   Search for `Mail`.
    *   Select `Mail.Read`. This allows the application to read emails in the user's mailbox.
6.  **Grant admin consent**: After adding the permission, you may need to grant admin consent. Click the "Grant admin consent for [Your Directory Name]" button.

### 4. Configure Your Environment

Create a `.env` file in the root of the project and add the credentials you copied:

```
OUTLOOK_CLIENT_ID="your-application-client-id"
OUTLOOK_TENANT_ID="your-directory-tenant-id"
```

### 5. Running with the Outlook Adaptor

You can now run the main application and specify `outlook` as the data source:

```bash
python main.py "Your query about your emails" --source outlook
```

The first time you run this, you will be prompted to sign in with your Microsoft account in a web browser and grant consent for the application to access your emails.

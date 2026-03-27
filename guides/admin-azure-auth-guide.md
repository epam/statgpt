# StatGPT Admin Azure Authentication Guide

This guide describes how to configure Azure Active Directory (Entra ID) authentication for StatGPT Admin Frontend and StatGPT Admin Backend only. It covers the StatGPT Admin auth workflow, required Entra ID resources, and Helm values for the admin components.

## Architecture and Workflow

StatGPT Admin uses OAuth 2.0 / OpenID Connect (OIDC):

1. User Login: The user logs into the Admin Frontend.
2. Token Request: The Frontend requests a token with the scope `Admin.Login` and requests the user's Azure AD Group Memberships.
3. API Call: The Frontend calls the Admin Backend.
4. Validation: The Admin Backend validates the token and checks if the user's `groups` claim contains the allowed Azure AD Group ID.

## Entra ID Setup

You will need to create 2 App Registrations and 1 Azure AD Group.

### Step A: Create Azure AD Group

This group controls who has access to the StatGPT Admin Panel.

1. Go to Microsoft Entra ID -> Groups -> New Group.
2. Group Type: Security (or Microsoft 365).
3. Name: `StatGPT Admins`.
4. Members: Add the users who require admin access.
5. Important: Copy the Object ID of this group. You will need it for `ADMIN_ROLES_VALUES`.

### Step B: Create "Admin Service" (Backend Identity)

This app is the audience of the access token that the Admin Backend validates.

1. Create App Registration: Name it `StatGPT-Admin-Backend`.
2. Expose an API:
    - Click Expose an API -> Add a scope.
    - Application ID URI: Click "Set" (accept the default `api://<UUID>`).
    - Scope Name: `Admin.Login`.
    - Who can consent: Admins and Users.
    - Description: "Access StatGPT Admin Backend".
    - After Step C: Under Expose an API -> Authorized client applications, add the Admin Client app and select `Admin.Login` so users are not prompted for consent.
3. Token Configuration:
    - Go to Token configuration -> Add groups claim.
    - Select Groups assigned to the application.
    - Expand "ID" -> Select Group ID.
    - Click Add.
4. Copy ID: Copy the Application (client) ID.
    - Mapping: `OIDC_CLIENT_ID`.
5. Assign the Group to the Application (Enterprise Applications):
    - Search for Enterprise applications in the top Azure search bar and open it.
    - Find and click on `StatGPT-Admin-Backend`.
    - Go to Users and groups -> Add user/group -> Select `StatGPT Admins` group -> Click Select -> Assign.
    - Result: Only members of this group can get a token for this app, and their Group ID will appear in the token's `groups` claim (used by `ADMIN_ROLES_VALUES`).

### Step C: Create "Admin Client" (Frontend Identity)

This app is used by the Admin Frontend to sign users in and obtain tokens for the Admin Service.

1. Create App Registration: Name it `StatGPT-Admin-Frontend`.
2. Authentication:
    - Platform: Web.
    - Redirect URIs:
        - `https://<YOUR_ADMIN_DOMAIN>/api/auth/callback/azure-ad`
3. API Permissions:
    - Click Add a permission -> My APIs -> Select `StatGPT-Admin-Backend`.
    - Check `Admin.Login` (delegated).
    - Click Grant admin consent (if available).
4. Secrets: Go to Certificates & secrets -> New client secret. Copy the Value. (Sensitive variable: `AUTH_AZURE_AD_SECRET`).
5. Copy ID: Copy the Application (client) ID. (Variable: `AUTH_AZURE_AD_CLIENT_ID`).

## Application Configuration

Configure your Helm `values.yaml` for Admin Backend and Admin Frontend. Replace placeholders with the IDs from the steps above.

### Admin Backend

This service validates the token and enforces group and scope.

```yaml
admin-backend:
  enabled: true
  env:
    # OIDC Configuration
    OIDC_AUTH_ENABLED: "true"
    OIDC_CONFIGURATION_ENDPOINT: "https://login.microsoftonline.com/<TENANT_ID>/v2.0/.well-known/openid-configuration"
    OIDC_ISSUER: "https://sts.windows.net/<TENANT_ID>/"
    OIDC_CLIENT_ID: "<ADMIN_SERVICE_APP_ID>"
    OIDC_USERNAME_CLAIM: "upn" # "upn" usually maps to email in Azure AD

    # Role and Scope Validation
    ADMIN_ROLES_CLAIM: "groups"
    ADMIN_ROLES_VALUES: "<SECURITY_GROUP_OBJECT_ID>"
    ADMIN_SCOPE_CLAIM_VALIDATION_ENABLED: "true"
    ADMIN_SCOPE_CLAIM: "scp"
    ADMIN_SCOPE_VALUE: "Admin.Login"
```

### Admin Frontend

This service handles the login UI and sends the token to the Admin Backend.

```yaml
admin-frontend:
  enabled: true
  env:
    # Azure AD
    AUTH_AZURE_AD_NAME: "StatGPT-Admin-Frontend"
    AUTH_AZURE_AD_TENANT_ID: "<TENANT_ID>"
    AUTH_AZURE_AD_CLIENT_ID: "<ADMIN_CLIENT_APP_ID>"
    # Must include the Admin Service scope so the token has aud and scp for Admin Backend
    AUTH_AZURE_AD_SCOPE: "openid profile <ADMIN_SERVICE_APP_ID>/Admin.Login email offline_access"

  secrets:
    AUTH_AZURE_AD_SECRET: "<ADMIN_CLIENT_SECRET_VALUE>"
```

## Placeholder Reference

| Placeholder | Where to get it |
|-------------|-----------------|
| `<TENANT_ID>` | Azure AD -> Overview -> Tenant ID |
| `<ADMIN_SERVICE_APP_ID>` | Step B - Application (client) ID of StatGPT-Admin-Backend |
| `<ADMIN_CLIENT_APP_ID>` | Step C - Application (client) ID of StatGPT-Admin-Frontend |
| `<ADMIN_CLIENT_SECRET_VALUE>` | Step C - Client secret value |
| `<SECURITY_GROUP_OBJECT_ID>` | Step A - Group Object ID |
| `<YOUR_ADMIN_DOMAIN>` | Admin base host (e.g. `admin-statgpt.example.com`) |

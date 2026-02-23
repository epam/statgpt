# Azure Authentication Guide

This guide provides a comprehensive walkthrough for setting up Azure Active Directory (Entra ID) authentication for the StatGPT solution. It covers infrastructure setup, the authentication workflow, and the required Helm chart configuration.

## Architecture and Workflow

StatGPT uses OAuth 2.0/OpenID Connect (OIDC) to decouple the User Interfaces (Frontends) from the APIs (Backends).

### Chat Flow:

1. User Login: The user logs into the Chat Frontend.
2. Token Request: The Frontend requests an Access Token from Azure with the scope `Chat.Login`.
3. API Call: The Frontend calls the Chat Backend, attaching the token as a Bearer header.
4. Validation: The Chat Backend validates the token against the Chat Service App Registration to ensure it was issued for this specific service.

### Admin Flow:

1. User Login: The user logs into the Admin Frontend.
2. Token Request: The Frontend requests a token with the scope `Admin.Login` and requests the user's Azure AD Group Memberships.
3. API Call: The Frontend calls the Admin Backend.
4. Validation: The Admin Backend validates the token and checks if the user's groups claim contains the allowed Azure AD Group ID.

## Azure Resource Setup

You will need to create 4 App Registrations and 1 Azure AD Group.

### Step A: Create Azure AD Group

This group controls who has access to the StatGPT Admin Panel.

1. Go to Microsoft Entra ID -> Groups -> New Group.
2. Group Type: Security (or Microsoft 365).
3. Name: `StatGPT Admins`.
4. Members: Add the users who require admin access.
5. Important: Copy the Object Id of this group. You will need it for `ADMIN_ROLES_VALUES`.

### Step B: Create "Chat Service" (Backend Identity)

1. Create App Registration: Name it `StatGPT-Chat-Backend`.
2. Expose an API:
    - Click Expose an API -> Add a scope.
    - Application ID URI: Click "Set" (accept the default `api://<UUID>`).
    - Scope Name: `Chat.Login`.
    - Who can consent: Admins and Users.
    - Description: "Access StatGPT Chat Backend".
    - After Step C: Under Expose an API -> Authorized client applications, add the Chat Client app and select `Chat.Login` so users are not prompted for consent.
3. Secrets: Go to Certificates & secrets -> New client secret. Copy the Value.
    - Mapping: `SERVICES_CHAT_CLIENT_SECRET`.
4. Copy ID: Copy the Application (client) ID.
    - Mapping: `SERVICES_CHAT_CLIENT_ID`.

### Step C: Create "Chat Client" (Frontend Identity)

1. Create App Registration: Name it `StatGPT-Chat-Frontend`.
2. Authentication:
    - Platform: Web.
    - Redirect URIs:
        - https://<YOUR_CHAT_DOMAIN>/auth/toolset-signin
3. API Permissions:
    - Click Add a permission -> My APIs -> Select `StatGPT-Chat-Backend`.
    - Check `Chat.Login`.
    - Click Grant admin consent (if available).
4. Secrets: Go to Certificates & secrets -> New client secret. Copy the Value.
    - Mapping: `CLIENTS_SPA_CHAT_CLIENT_SECRET`.
5. Copy ID: Copy the Application (client) ID.
    - Mapping: `CLIENTS_SPA_CHAT_CLIENT_ID`.

### Step D: Create "Admin Service" (Backend Identity)

1. Create App Registration: Name it `StatGPT-Admin-Backend`.
2. Expose an API:
    - Click Expose an API -> Add a scope.
    - Application ID URI: Click "Set" (accept the default `api://<UUID>`).
    - Scope Name: `Admin.Login`.
    - Who can consent: Admins and Users.
    - Description: "Access StatGPT Admin Backend".
    - After Step E: Under Expose an API -> Authorized client applications, add the Admin Client app and select `Admin.Login` so users are not prompted for consent.
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

### Step E: Create "Admin Client" (Frontend Identity)

1. Create App Registration: Name it `StatGPT-Admin-Frontend`.
2. Authentication:
    - Platform: Web.
    - Redirect URIs:
        - https://<YOUR_ADMIN_DOMAIN>/api/auth/callback/azure-ad
3. API Permissions:
    - Click Add a permission -> My APIs -> Select `StatGPT-Admin-Backend`.
    - Check `Admin.Login`.
    - Click Grant admin consent (if available).
4. Secrets: Go to Certificates & secrets -> New client secret. Copy the Value. (Sensitive variable: `AUTH_AZURE_AD_SECRET`).
5. Copy ID: Copy the Application (client) ID. (Variable: `AUTH_AZURE_AD_CLIENT_ID`).

## Application Configuration

Below are the required configurations for your `values.yaml`. Replace the placeholders `<...>` with the IDs collected above.

### Chat Backend Configuration

This service validates tokens from the Chat Client.

```yaml
chat-backend:
  enabled: true
  env:
    # Azure AD Token Endpoint
    OAUTH2_TOKEN_ENDPOINT_URL: "https://login.microsoftonline.com/<TENANT_ID>/oauth2/v2.0/token"

    # Chat Service (Backend) Identity
    SERVICES_CHAT_CLIENT_ID: "<CHAT_SERVICE_APP_ID>"
    SERVICES_CHAT_SCOPE: "<CHAT_SERVICE_APP_ID>/.default email"

    # Chat Client (Frontend) Identity
    CLIENTS_SPA_CHAT_CLIENT_ID: "<CHAT_CLIENT_APP_ID>"

  secrets:
    SERVICES_CHAT_CLIENT_SECRET: "<CHAT_SERVICE_SECRET_VALUE>"
    # Required if chat-backend uses on-behalf-of or token exchange
    CLIENTS_SPA_CHAT_CLIENT_SECRET: "<CHAT_CLIENT_SECRET_VALUE>"
```

### Admin Backend Configuration

This service validates tokens and checks for Group membership.

```yaml
admin-backend:
  enabled: true
  env:
    # Service-to-Service Communication (Admin calling Chat)
    OAUTH2_TOKEN_ENDPOINT_URL: "https://login.microsoftonline.com/<TENANT_ID>/oauth2/v2.0/token"
    SERVICES_CHAT_CLIENT_ID: "<CHAT_SERVICE_APP_ID>"
    SERVICES_CHAT_SCOPE: "<CHAT_SERVICE_APP_ID>/.default email"

    # OIDC Configuration
    OIDC_AUTH_ENABLED: "true"
    OIDC_CONFIGURATION_ENDPOINT: "https://login.microsoftonline.com/<TENANT_ID>/v2.0/.well-known/openid-configuration"
    OIDC_ISSUER: "https://sts.windows.net/<TENANT_ID>/"
    OIDC_CLIENT_ID: "<ADMIN_SERVICE_APP_ID>"
    OIDC_USERNAME_CLAIM: "upn" # 'upn' usually maps to email in Azure AD

    # Role and Scope Validation
    ADMIN_ROLES_CLAIM: "groups"
    ADMIN_ROLES_VALUES: "<SECURITY_GROUP_OBJECT_ID>"
    ADMIN_SCOPE_CLAIM_VALIDATION_ENABLED: "true"
    ADMIN_SCOPE_CLAIM: "scp"
    ADMIN_SCOPE_VALUE: "Admin.Login"

  secrets:
    # Required for Admin Backend to authenticate against Chat Backend
    SERVICES_CHAT_CLIENT_SECRET: "<CHAT_SERVICE_SECRET_VALUE>"
```

### Admin Frontend Configuration

This service handles the login UI and passes the token to the backend.

```yaml
admin-frontend:
  enabled: true
  env:
    # Azure AD
    AUTH_AZURE_AD_NAME: "StatGPT-Admin-Frontend"
    AUTH_AZURE_AD_TENANT_ID: "<TENANT_ID>"
    AUTH_AZURE_AD_CLIENT_ID: "<ADMIN_CLIENT_APP_ID>"
    # Scopes: Standard OIDC scopes + custom scope for Admin Backend (must include Admin.Login)
    AUTH_AZURE_AD_SCOPE: "openid profile <ADMIN_SERVICE_APP_ID>/Admin.Login email offline_access"

  secrets:
    AUTH_AZURE_AD_SECRET: "<ADMIN_CLIENT_SECRET_VALUE>"
```

## Placeholder Reference

| Placeholder | Where to get it |
|-------------|-----------------|
| `<TENANT_ID>` | Azure AD -> Overview -> Tenant ID |
| `<CHAT_SERVICE_APP_ID>` | Step B - Application (client) ID |
| `<CHAT_SERVICE_SECRET_VALUE>` | Step B - Client secret value |
| `<CHAT_CLIENT_APP_ID>` | Step C - Application (client) ID |
| `<CHAT_CLIENT_SECRET_VALUE>` | Step C - Client secret value |
| `<ADMIN_SERVICE_APP_ID>` | Step D - Application (client) ID |
| `<ADMIN_CLIENT_APP_ID>` | Step E - Application (client) ID |
| `<ADMIN_CLIENT_SECRET_VALUE>` | Step E - Client secret value |
| `<SECURITY_GROUP_OBJECT_ID>` | Step A - Group Object ID |
| `<YOUR_CHAT_DOMAIN>` | Chat base host |
| `<YOUR_ADMIN_DOMAIN>` | Admin base host |

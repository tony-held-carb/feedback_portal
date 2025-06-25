"""
Okta Integration Settings for ARB Feedback Portal

Current State:
- The portal uses a local database for authentication and authorization.
- The USE_OKTA flag controls whether Okta (OIDC/SAML) is used for authentication.

Transition Plan:
- When Okta is adopted, set USE_OKTA = True.
- All routes and functions that check USE_OKTA will switch to Okta-based logic.
- This file documents the transition plan and serves as a reference for Okta-related configuration.

How to Identify Okta-Ready Code:
- Any route or function that checks USE_OKTA is ready for Okta integration.
- TODOs and NotImplementedError messages indicate what Okta information is needed.

To enable Okta, set USE_OKTA = True and provide required Okta configuration below.
"""

USE_OKTA = False

# Future Okta configuration (client ID, endpoints, etc.) can be added here. 
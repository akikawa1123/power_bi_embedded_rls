# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

class BaseConfig(object):

    # Can be set to 'MasterUser' or 'ServicePrincipal'
    AUTHENTICATION_MODE = 'ServicePrincipal'

    # Workspace Id in which the report is present
    WORKSPACE_ID = 'YOUR_WORKSPACE_ID'
    
    # Report Id for which Embed token needs to be generated
    REPORT_ID = 'YOUR_REPORT_ID'
    
    # Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal authentication mode.
    TENANT_ID = 'YOUR_TENANT_ID'
    
    # Client Id (Application Id) of the AAD app
    CLIENT_ID = 'YOUR_CLIENT_ID'
    
    # Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
    CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
    
    # Scope Base of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
    SCOPE_BASE = ['https://analysis.windows.net/powerbi/api/.default']
    
    # URL used for initiating authorization request
    AUTHORITY_URL = 'https://login.microsoftonline.com/organizations'
    
    # Master user email address. Required only for MasterUser authentication mode.
    POWER_BI_USER = ''
    
    # Master user email password. Required only for MasterUser authentication mode.
    POWER_BI_PASS = ''



    # Customer mapping for Row-Level Security (RLS) demo
    # Each customer has:
    # - name: Display name for the customer
    # - username: Username passed to RLS (must match the value used in Power BI RLS rules)
    # - roles: List of RLS role names defined in Power BI dataset
    # 
    # Example scenario:
    # - customer_a: Can only see "Software" products (filtered by RLS)
    # - customer_b: Can only see "Hardware" products (filtered by RLS)
    # - customer_c: Can see all products
    CUSTOMER_MAPPING = {
        'customer_a': {
            'name': '顧客A - ソフトウェア事業部',
            'username': 'customer_a',
            'roles': ['CustomerRole']
        },
        'customer_b': {
            'name': '顧客B - 家具事業部',
            'username': 'customer_b',
            'roles': ['CustomerRole']
        },
        'customer_c': {
            'name': '顧客C - 統括本部（全データ）',
            'username': 'customer_c',
            'roles': ['CustomerRole']
        }
    }
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license

class EffectiveIdentity:
    '''Effective identity for Row-Level Security (RLS)'''

    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys

    username = None
    roles = None
    datasets = None

    def __init__(self, username, roles, datasets):
        '''Initialize EffectiveIdentity

        Args:
            username (str): Username to apply RLS (typically customer ID or email)
            roles (list): List of role names defined in Power BI dataset
            datasets (list): List of dataset IDs to apply this identity to
        '''
        self.username = username
        self.roles = roles
        self.datasets = datasets

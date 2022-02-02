import botocore
import boto3
import datetime
from dateutil.tz import tzlocal

class AssumeRole:

    def __init__(self, role_arn):
        self.role_arn = role_arn
    
    """
    Assumes a session role
    """    
    def assumed_role_session(self):
        base_session = botocore.session.Session
        base_session = boto3.session.Session()._session
        fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
            client_creator = base_session.create_client,
            source_credentials = base_session.get_credentials(),
            role_arn = self.role_arn,
            extra_args = {
            #    'RoleSessionName': None # set this if you want something non-default
            }
        )
        creds = botocore.credentials.DeferredRefreshableCredentials(
            method = 'assume-role',
            refresh_using = fetcher.fetch_credentials,
            time_fetcher = lambda: datetime.datetime.now(tzlocal())
        )
        botocore_session = botocore.session.Session()
        botocore_session._credentials = creds

        return boto3.Session(botocore_session = botocore_session)

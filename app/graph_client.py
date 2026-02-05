import time
from typing import Dict, Iterable, Optional

import msal
import requests

GRAPH_API = "https://graph.microsoft.com/v1.0"


class GraphClient:
    def __init__(self, tenant_id: str, client_id: str):
        self._app = msal.PublicClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )

    def acquire_token_device_code(self, scopes: Iterable[str]) -> str:
        flow = self._app.initiate_device_flow(scopes=list(scopes))
        if "user_code" not in flow:
            raise RuntimeError("Failed to create device flow for Microsoft Graph")
        print(flow["message"])
        result = self._app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise RuntimeError(
                f"Device code flow failed: {result.get('error_description')}"
            )
        return result["access_token"]

    def _get(self, url: str, access_token: str, params: Optional[Dict] = None):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_messages_delta(
        self,
        mailbox_user: str,
        access_token: str,
        delta_link: Optional[str] = None,
    ) -> Dict:
        if delta_link:
            return self._get(delta_link, access_token)

        url = f"{GRAPH_API}/users/{mailbox_user}/mailFolders/inbox/messages/delta"
        params = {
            "$select": "id,subject,receivedDateTime,from,body,bodyPreview",
            "$orderby": "receivedDateTime desc",
        }
        return self._get(url, access_token, params=params)

    def get_message(self, mailbox_user: str, access_token: str, message_id: str) -> Dict:
        url = f"{GRAPH_API}/users/{mailbox_user}/messages/{message_id}"
        params = {"$select": "id,subject,receivedDateTime,from,body,bodyPreview"}
        return self._get(url, access_token, params=params)

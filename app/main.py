from app.config import get_settings
from app.graph_client import GraphClient
from app.ingestion import ingest_mailbox
from app.storage import Storage


def main() -> None:
    settings = get_settings()
    storage = Storage(settings.db_path)
    graph_client = GraphClient(settings.tenant_id, settings.client_id)

    access_token = graph_client.acquire_token_device_code(scopes=["Mail.Read"])
    ingest_mailbox(
        graph_client=graph_client,
        storage=storage,
        mailbox_user=settings.mailbox_user,
        access_token=access_token,
    )


if __name__ == "__main__":
    main()

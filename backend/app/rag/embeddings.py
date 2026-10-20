import voyageai

from app.core.config import settings

MODEL = "voyage-4"
DIMENSIONS = 1024

client = voyageai.Client(api_key=settings.voyage_api_key)


def embed_documents(texts: list[str]) -> list[list[float]]:
    result = client.embed(
        texts, model=MODEL, input_type="document", output_dimension=DIMENSIONS
    )
    return result.embeddings


def embed_query(text: str) -> list[float]:
    result = client.embed(
        [text], model=MODEL, input_type="query", output_dimension=DIMENSIONS
    )
    return result.embeddings[0]

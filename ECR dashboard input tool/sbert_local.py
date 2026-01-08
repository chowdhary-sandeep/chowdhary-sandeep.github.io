import os
from typing import Optional

try:
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import snapshot_download
except Exception:  # libs might not be installed yet
    SentenceTransformer = None
    snapshot_download = None


def setup_local_model(model_name: str = 'all-MiniLM-L6-v2', base_dir: Optional[str] = None):
    """
    Minimal local loader for Sentence-BERT models.
    - Downloads once into ./models/<model_name>
    - Loads model from that local folder afterward
    Returns the SentenceTransformer instance, or None on failure.
    """
    if SentenceTransformer is None or snapshot_download is None: return None
    root = base_dir or os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(root, 'models')
    os.makedirs(cache_dir, exist_ok=True)

    target = os.path.join(cache_dir, model_name)
    try:
        if not os.path.exists(target) or not os.listdir(target):
            snapshot_download(
                repo_id=f'sentence-transformers/{model_name}',
                local_dir=target,
                local_dir_use_symlinks=False,
            )
        return SentenceTransformer(target)
    except Exception:
        return None



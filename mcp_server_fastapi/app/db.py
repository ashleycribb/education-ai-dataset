from typing import Dict
from .models import ContextData

# In-memory database
# The key is the context_id (str)
# The value is the ContextData object
fake_context_db: Dict[str, ContextData] = {}

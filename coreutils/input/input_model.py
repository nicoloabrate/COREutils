from pydantic import TypeAdapter, BaseModel
from typing import Any

class CaseInsensitiveAdapter(TypeAdapter[Any]):
    def validate_python(self, value: Any) -> Any:
        def __lower__(value: Any) -> Any:
            if isinstance(value, dict):
                return {k.lower(): __lower__(v) for k, v in value.items()}
            return value

        value = __lower__(value)
        return super().validate_python(value)
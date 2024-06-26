from typing import Self

from wialon import Wialon


class WialonSession:
    def __init__(self, token: str) -> None:
        self.wialon_api: Wialon = Wialon()
        self.token = token

        return None

    def __enter__(self) -> Self:
        login = self.wialon_api.token_login(token=self.token)
        self.wialon_api.sid = login["eid"]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> str | None:
        if any([exc_type, exc_val, exc_tb]):
            return f"Error: {exc_val}"
        self.wialon_api.core_logout()
        return None

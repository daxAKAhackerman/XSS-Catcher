class DetailResponse:
    def __new__(cls, detail: str) -> dict[str, str]:
        return {"detail": detail}

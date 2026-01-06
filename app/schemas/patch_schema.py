from pydantic import BaseModel

class PatchDownload(BaseModel):
    catalogUrl: str
    baseUrl: str

class PatchResponse(BaseModel):
    appVersionMin: str
    appVersionMax: str

    contentVersion: str
    mandatory: bool

    download: PatchDownload
    sizeMb: int
    checksum: str | None = None

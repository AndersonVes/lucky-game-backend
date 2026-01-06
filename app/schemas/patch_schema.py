from pydantic import BaseModel, field_validator
from packaging.version import Version, InvalidVersion

class PatchDownloadOut(BaseModel):
    catalogUrl: str
    baseUrl: str

class PatchLatestOut(BaseModel):
    appVersionMin: str
    appVersionMax:str
    contentVersion: str
    mandatory: bool
    sizeMb: int
    checksum: str | None
    download: PatchDownloadOut

    @field_validator("appVersionMin", "appVersionMax", "contentVersion", mode="before")
    @classmethod
    def validate_version(cls, v):
        if v is None:
            return v
        try:
            Version(str(v))
        except InvalidVersion:
            raise ValueError("Invalid version format")
        return str(v)
    


# # class PatchOut(BaseModel):
# #     appVersionMin: str
# #     appVersionMax: str

# #     contentVersion: str
# #     mandatory: bool

# #     download: PatchDownload
# #     sizeMb: int
# #     checksum: str | None = None

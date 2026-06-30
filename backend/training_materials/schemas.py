from pydantic import BaseModel, ConfigDict, HttpUrl



class TrainingMaterialResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str
    url: str
    material_type: str
    session_id: int
    user_id: int

class TrainingMaterialUrlCreateRequest(BaseModel):
    title: str
    url: HttpUrl
    session_id: int
    user_id: int
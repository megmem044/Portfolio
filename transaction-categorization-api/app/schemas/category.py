from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)

    @field_validator("name")
    @classmethod
    def clean_name(cls, name: str) -> str:
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("name must not be blank")
        return cleaned

    @field_validator("description")
    @classmethod
    def clean_description(cls, description: str | None) -> str | None:
        if description is None:
            return None
        return description.strip() or None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)

    @field_validator("name")
    @classmethod
    def clean_name(cls, name: str | None) -> str | None:
        if name is None:
            return None
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("name must not be blank")
        return cleaned

    @field_validator("description")
    @classmethod
    def clean_description(cls, description: str | None) -> str | None:
        if description is None:
            return None
        return description.strip() or None

    @model_validator(mode="after")
    def require_a_change(self):
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null")
        return self


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_default: bool

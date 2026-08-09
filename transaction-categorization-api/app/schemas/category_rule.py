"""Check merchant-rule input and define rule API response shapes."""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoryRuleCreate(BaseModel):
    keyword: str = Field(
        min_length=1,
        max_length=100,
        description="Text to find inside a merchant name",
        examples=["netflix"],
    )
    category_id: int = Field(gt=0)
    priority: int = Field(default=100, ge=1, le=10_000)
    is_active: bool = True

    @field_validator("keyword")
    @classmethod
    def normalize_keyword(cls, keyword: str) -> str:
        cleaned = keyword.strip().casefold()
        if not cleaned:
            raise ValueError("keyword must not be blank")
        return cleaned


class CategoryRuleUpdate(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=100)
    category_id: int | None = Field(default=None, gt=0)
    priority: int | None = Field(default=None, ge=1, le=10_000)
    is_active: bool | None = None

    @field_validator("keyword")
    @classmethod
    def normalize_keyword(cls, keyword: str | None) -> str | None:
        if keyword is None:
            return None
        cleaned = keyword.strip().casefold()
        if not cleaned:
            raise ValueError("keyword must not be blank")
        return cleaned

    @model_validator(mode="after")
    def require_a_change(self):
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("updated fields cannot be null")
        return self


class CategoryRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keyword: str
    category_id: int
    category_name: str
    priority: int
    is_active: bool
    is_default: bool

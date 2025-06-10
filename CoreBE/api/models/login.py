from pydantic import BaseModel, Field

class LoginInput(BaseModel):
	username: str = Field(
		...,
		description="Username for login",
		example="Admin",
		min_length=1
	)
	password: str = Field(
		...,
		description="Password for login",
		example="thaco@1234",
		min_length=1
	)

	class Config:
		json_schema_extra = {
			"example": {
				"username": "Admin",
				"password": "thaco@1234"
			}
		}

class LoginOutput(BaseModel):
	id: str
	username: str
	accesstoken: str
	refresh_token: str = Field(alias="refreshToken")
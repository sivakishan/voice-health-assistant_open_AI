import os
from dotenv import load_dotenv
from opperai import Opper
from pydantic import BaseModel, Field

# Ensure .env is loaded from the same directory as this script
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

opper = Opper(api_key=os.getenv("OPPER_API_KEY"))

class ResponseModel(BaseModel):
    reply: str = Field(description="Assistant's response")

def ask_gpt(prompt):
    output, _ = opper.call(
        name="healthcare_assistant",
        instructions="Provide medical advice based on the user's input.",
        input={"user_input": prompt},
        output_type=ResponseModel,
    )
    return output.reply


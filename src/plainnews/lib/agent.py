from boto3.session import Session
from strands import Agent
from strands.models import BedrockModel

from plainnews.lib.prompts import SYSTEM_PROMPT
from plainnews.lib.tools import fetch_url_as_markdown
from plainnews.settings import Settings, create_boto_session


def create_agent(*, settings: Settings) -> Agent:
    boto_session: Session = create_boto_session(settings)

    return Agent(
        model=BedrockModel(
            boto_session=boto_session,
            model_id=settings.resolved_bedrock_model_id,
        ),
        tools=[fetch_url_as_markdown],
        system_prompt=SYSTEM_PROMPT,
    )

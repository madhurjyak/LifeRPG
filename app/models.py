from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal

AttributeLiteral = Literal['MIND', 'HEALTH', 'CAREER', 'WEALTH']
DifficultyLiteral = Literal['E', 'D', 'C', 'B', 'A', 'S']
ItemTypeLiteral = Literal['IRL_REWARD', 'SYSTEM_ARTIFACT']
BurnoutLiteral = Literal['LOW', 'MODERATE', 'HIGH']

class CampaignCreateRequest(BaseModel):
    goal_title: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = Field(default="", max_length=1000)
    difficulty_focus: Optional[str] = Field(default="BALANCED")
    target_date: Optional[str] = None

class QuestCreateRequest(BaseModel):
    task_name: str = Field(..., min_length=2, max_length=200)
    attribute_type: AttributeLiteral
    difficulty_rank: DifficultyLiteral = 'C'
    campaign_id: Optional[int] = None

class CrucibleCompleteRequest(BaseModel):
    duration_minutes: int = Field(..., ge=1, le=300)
    attribute_type: AttributeLiteral = 'MIND'
    campaign_id: Optional[int] = None

class JournalCreateRequest(BaseModel):
    journal_content: str = Field(..., min_length=5, max_length=5000)

class ReliquaryItemCreateRequest(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=100)
    item_description: str = Field(..., min_length=2, max_length=300)
    gold_cost: int = Field(..., ge=1, le=10000)
    icon_name: str = Field(default="sparkles", max_length=50)
    item_type: ItemTypeLiteral = 'IRL_REWARD'

class GeneratedQuest(BaseModel):
    task_name: str
    attribute_type: AttributeLiteral
    difficulty_rank: DifficultyLiteral = 'C'
    xp_value: int = 65
    gold_value: int = 25
    boss_damage: int = 65

class CampaignSplinterResponse(BaseModel):
    boss_name: str
    boss_title: str
    boss_hp: int = 500
    narrative_premise: str
    quests: List[GeneratedQuest]

class JournalAnalysisResponse(BaseModel):
    sentiment_score: int = Field(..., ge=-100, le=100)
    auto_tags: str
    detected_blockers: str
    ai_gamemaster_notes: str

    @field_validator('auto_tags', mode='before')
    @classmethod
    def format_tags(cls, v):
        if isinstance(v, list):
            return ",".join(str(t).strip() for t in v)
        return str(v)

class OracleProphecyResponse(BaseModel):
    prophecy_title: str
    narrative_assessment: str
    weakest_pillar_advice: str
    burnout_risk_level: BurnoutLiteral
    recommended_quests: List[GeneratedQuest] = Field(default_factory=list)


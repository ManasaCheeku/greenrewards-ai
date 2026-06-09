from typing import List
from datetime import datetime, timedelta

import models


def generate_ai_tips_for_campaign(campaign: models.Campaign) -> List[str]:
    tips = []
    # Basic heuristics for tips based on campaign activities and type
    if campaign.goal and 'walk' in (campaign.goal or '').lower():
        tips.append("Break your daily walk into shorter sessions to hit the target consistently.")
        tips.append("Use a pedometer or phone health app to track distance accurately.")
    if campaign.goal and 'cycle' in (campaign.goal or '').lower():
        tips.append("Plan a safe route and cycle with a buddy for motivation.")
    # generic tips
    tips.append("Share progress with your team to inspire others.")
    tips.append("Upload clear photos or screenshots as proof for faster verification.")
    return tips


def schedule_campaign_reminder(campaign: models.Campaign, user_id: int):
    # Placeholder: in production, hook with email/SMS/push provider
    # For now, return a scheduled datetime for reminder
    now = datetime.utcnow()
    remind_at = now + timedelta(days=1)
    return {"user_id": user_id, "campaign_id": campaign.id, "remind_at": remind_at.isoformat()}

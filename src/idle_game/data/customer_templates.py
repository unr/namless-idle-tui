"""Customer templates for tutorial and regular customers."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal


@dataclass
class CustomerTrade:
    """Represents a trade offer from a customer."""
    gives_emotion: str
    gives_amount: int
    receives_emotion: str
    receives_amount: int


@dataclass
class TutorialCustomerTemplate:
    """Template for event-triggered tutorial customers."""
    id: str
    name: str
    avatar: str
    trigger_emotion: str  # Emotion that triggers this customer
    trigger_amount: int  # Amount needed to trigger
    dialogue: str
    trade: CustomerTrade
    unlocks_emotion: str  # Emotion unlocked by this trade
    unlocks_description: str


@dataclass
class RegularCustomerTemplate:
    """Template for generating queue customers."""
    name_pool: List[str]
    avatar_pool: List[str]
    dialogue_templates: List[str]
    min_budget: Decimal
    max_budget: Decimal
    base_patience: int


# Tutorial Customers (Event-Triggered)
TUTORIAL_CUSTOMERS: List[TutorialCustomerTemplate] = [
    TutorialCustomerTemplate(
        id="joy_seeker",
        name="Joy Seeker",
        avatar="😊",
        trigger_emotion="smiles",
        trigger_amount=10,
        dialogue="I heard you collect smiles. Can I buy some happiness?",
        trade=CustomerTrade(
            gives_emotion="smiles",
            gives_amount=10,
            receives_emotion="joy",
            receives_amount=1
        ),
        unlocks_emotion="joy",
        unlocks_description="Joy resource unlocked! Joy generates Smiles passively."
    ),
    TutorialCustomerTemplate(
        id="melancholy_poet",
        name="Melancholy Poet",
        avatar="📝",
        trigger_emotion="joy",
        trigger_amount=50,
        dialogue="I need sadness for my art. Too much joy lately.",
        trade=CustomerTrade(
            gives_emotion="joy",
            gives_amount=50,
            receives_emotion="sadness",
            receives_amount=5
        ),
        unlocks_emotion="sadness",
        unlocks_description="Sadness unlocked! Mixing potential available."
    ),
    TutorialCustomerTemplate(
        id="frustrated_worker",
        name="Frustrated Worker",
        avatar="💼",
        trigger_emotion="love",
        trigger_amount=100,
        dialogue="I'm too content. I need anger to demand change.",
        trade=CustomerTrade(
            gives_emotion="love",
            gives_amount=100,
            receives_emotion="anger",
            receives_amount=10
        ),
        unlocks_emotion="anger",
        unlocks_description="Anger unlocked! Courage recipes now available."
    ),
    TutorialCustomerTemplate(
        id="thrill_seeker",
        name="Thrill Seeker",
        avatar="🎢",
        trigger_emotion="nostalgia",
        trigger_amount=500,
        dialogue="Life's too predictable. I need some fear.",
        trade=CustomerTrade(
            gives_emotion="nostalgia",
            gives_amount=500,
            receives_emotion="fear",
            receives_amount=20
        ),
        unlocks_emotion="fear",
        unlocks_description="Fear unlocked! Excitement mixing available."
    ),
    TutorialCustomerTemplate(
        id="boundary_setter",
        name="Boundary Setter",
        avatar="🛡️",
        trigger_emotion="serenity",
        trigger_amount=1000,
        dialogue="I need to reject toxic people. Give me disgust.",
        trade=CustomerTrade(
            gives_emotion="serenity",
            gives_amount=1000,
            receives_emotion="disgust",
            receives_amount=50
        ),
        unlocks_emotion="disgust",
        unlocks_description="Disgust unlocked! Full emotion palette complete."
    ),
]


# Regular Customer Name Pools
CUSTOMER_NAMES = [
    "Sarah Martinez", "Marcus Chen", "Dr. Kim", "Alex Johnson", "Taylor Brown",
    "Jordan Lee", "Casey Smith", "Riley Davis", "Morgan Wilson", "Avery Garcia",
    "Quinn Rodriguez", "Parker Martinez", "Cameron Anderson", "Sydney Taylor",
    "Blake Thomas", "Hayden Jackson", "Peyton White", "Dakota Harris",
    "Finley Martin", "Rowan Thompson", "Sage Moore", "River Clark",
    "Phoenix Lewis", "Skylar Walker", "Eden Hall", "Atlas Allen",
    "Willow Young", "Reed King", "Luna Wright", "Iris Lopez"
]


# Customer Avatars by Mood/Type
CUSTOMER_AVATARS = [
    "😊", "😢", "😠", "😰", "😌", "🤔", "😔", "😖", "😣", "😞",
    "🙂", "😐", "😑", "😕", "😟", "😤", "😥", "😨", "😩", "😪",
    "👤", "👨", "👩", "🧑", "👴", "👵", "🧒", "👦", "👧"
]


# Dialogue Templates for Regular Customers
DIALOGUE_TEMPLATES = [
    "I've been feeling {emotion_state}. Can you help?",
    "My life lacks {need}. Do you have any?",
    "I heard you're the best at {service}.",
    "Can you sell me some {need}? I really need it.",
    "I'm willing to pay for quality {need}.",
    "Everyone says you have the purest {need}.",
    "I've tried everything else. Maybe {need} will help.",
    "A friend recommended your {service}.",
    "I don't know if this will work, but I need {need}.",
    "How much for your best {need}?",
    "I'm desperate for {need}. Please help.",
    "Do you have any {need} in stock?",
    "I've been a customer before. More {need}, please.",
    "My therapist suggested trying {need}.",
    "I read online that {need} might help me."
]


# Special Customer Types
@dataclass
class SpecialCustomerType:
    """Defines special customer variants."""
    type_id: str
    name_prefix: str
    budget_multiplier: float
    patience_modifier: int
    min_purity_required: float
    reputation_impact: float
    dialogue_prefix: str


SPECIAL_CUSTOMER_TYPES = {
    "vip": SpecialCustomerType(
        type_id="vip",
        name_prefix="[VIP]",
        budget_multiplier=2.0,
        patience_modifier=-2,  # Less patience
        min_purity_required=90.0,
        reputation_impact=2.0,
        dialogue_prefix="I expect only the finest quality. "
    ),
    "desperate": SpecialCustomerType(
        type_id="desperate",
        name_prefix="[URGENT]",
        budget_multiplier=3.0,
        patience_modifier=1,
        min_purity_required=50.0,
        reputation_impact=1.5,
        dialogue_prefix="I'm desperate! I'll pay anything! "
    ),
    "addicted": SpecialCustomerType(
        type_id="addicted",
        name_prefix="[RETURNING]",
        budget_multiplier=0.7,  # Can't afford as much
        patience_modifier=3,  # More patient/desperate
        min_purity_required=30.0,
        reputation_impact=-0.5,  # Ethical concern
        dialogue_prefix="I need more... The last batch wore off. "
    ),
}


# Emotion-based dialogue states
EMOTION_STATES = {
    "joy": ["happy", "cheerful", "delighted", "content"],
    "sadness": ["sad", "melancholy", "down", "blue", "depressed"],
    "anger": ["angry", "frustrated", "irritated", "furious"],
    "fear": ["anxious", "worried", "scared", "nervous", "terrified"],
    "disgust": ["disgusted", "repulsed", "sick", "revolted"],
    "love": ["loving", "affectionate", "warm", "caring"],
    "surprise": ["surprised", "shocked", "amazed", "astonished"],
    "anticipation": ["excited", "eager", "hopeful", "expectant"],
    "trust": ["trusting", "confident", "secure", "faithful"],
    "contempt": ["contemptuous", "scornful", "disdainful"]
}


# Service descriptions for dialogue
SERVICE_DESCRIPTIONS = {
    "joy": "spreading happiness",
    "sadness": "processing grief",
    "anger": "channeling frustration",
    "fear": "managing anxiety",
    "disgust": "setting boundaries",
    "love": "fostering connection",
    "courage": "building bravery",
    "serenity": "finding peace",
    "nostalgia": "remembering fondly",
    "euphoria": "experiencing bliss"
}


# Customer story arc seeds (for future implementation)
STORY_ARC_SEEDS = [
    {
        "arc_id": "sarah_job_interview",
        "character_name": "Sarah Martinez",
        "visits": 5,
        "initial_need": "courage",
        "arc_type": "success_story"
    },
    {
        "arc_id": "marcus_addiction",
        "character_name": "Marcus Chen",
        "visits": 8,
        "initial_need": "joy",
        "arc_type": "dependency"
    },
    {
        "arc_id": "dr_kim_research",
        "character_name": "Dr. Kim",
        "visits": 6,
        "initial_need": "curiosity",
        "arc_type": "growth"
    }
]

package game

import (
	"github.com/shopspring/decimal"
)

// EmotionTier represents the complexity level of an emotion
type EmotionTier int

const (
	TierBasic    EmotionTier = 0 // Smiles
	TierSimple   EmotionTier = 1 // Joy
	TierComplex  EmotionTier = 2 // Love, Hope
	TierNuanced  EmotionTier = 3 // Nostalgia, Pride
	TierDeep     EmotionTier = 4 // Gratitude, Serenity
	TierProfound EmotionTier = 5 // Transcendence
)

// EmotionType identifies specific emotions
type EmotionType string

const (
	EmotionSmiles        EmotionType = "smiles"
	EmotionJoy           EmotionType = "joy"
	EmotionLove          EmotionType = "love"
	EmotionHope          EmotionType = "hope"
	EmotionNostalgia     EmotionType = "nostalgia"
	EmotionPride         EmotionType = "pride"
	EmotionGratitude     EmotionType = "gratitude"
	EmotionSerenity      EmotionType = "serenity"
	EmotionTranscendence EmotionType = "transcendence"
)

// EmotionDefinition defines the static properties of an emotion type
type EmotionDefinition struct {
	Type           EmotionType
	Name           string
	Tier           EmotionTier
	Icon           string
	Description    string
	Produces       EmotionType // What emotion this produces (empty for smiles)
	ProductionRate decimal.Decimal
	BaseCost       decimal.Decimal // Cost to buy first producer
	MinStorage     int
	MaxStorage     int // 0 means unlimited
	BaseClickValue decimal.Decimal
	UnlockCost     decimal.Decimal // Cost in previous tier to unlock
}

// GetAllEmotions returns all emotion definitions in tier order
func GetAllEmotions() []EmotionDefinition {
	return []EmotionDefinition{
		{
			Type:           EmotionSmiles,
			Name:           "Smiles",
			Tier:           TierBasic,
			Icon:           "☺",
			Description:    "The fundamental building block of all emotions. Simple, pure, accessible.",
			Produces:       "",
			ProductionRate: decimal.Zero,
			BaseCost:       decimal.Zero,
			MinStorage:     100,
			MaxStorage:     0, // Unlimited
			BaseClickValue: decimal.NewFromInt(5),
			UnlockCost:     decimal.Zero,
		},
		{
			Type:           EmotionJoy,
			Name:           "Joy",
			Tier:           TierSimple,
			Icon:           "😊",
			Description:    "A step beyond simple pleasure. Deeper, more resonant.",
			Produces:       EmotionSmiles,
			ProductionRate: decimal.NewFromFloat(1.0),
			BaseCost:       decimal.NewFromInt(50),
			MinStorage:     50,
			MaxStorage:     10000,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(25),
		},
		{
			Type:           EmotionLove,
			Name:           "Love",
			Tier:           TierComplex,
			Icon:           "❤",
			Description:    "Connection and warmth between souls.",
			Produces:       EmotionJoy,
			ProductionRate: decimal.NewFromFloat(0.5),
			BaseCost:       decimal.NewFromInt(500),
			MinStorage:     25,
			MaxStorage:     5000,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(250),
		},
		{
			Type:           EmotionHope,
			Name:           "Hope",
			Tier:           TierComplex,
			Icon:           "🌟",
			Description:    "The light that guides through darkness.",
			Produces:       EmotionJoy,
			ProductionRate: decimal.NewFromFloat(0.4),
			BaseCost:       decimal.NewFromInt(450),
			MinStorage:     20,
			MaxStorage:     4000,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(225),
		},
		{
			Type:           EmotionNostalgia,
			Name:           "Nostalgia",
			Tier:           TierNuanced,
			Icon:           "🕰",
			Description:    "Sweet sorrow of memory. Bittersweet and profound.",
			Produces:       EmotionLove,
			ProductionRate: decimal.NewFromFloat(0.25),
			BaseCost:       decimal.NewFromInt(2500),
			MinStorage:     10,
			MaxStorage:     1000,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(1250),
		},
		{
			Type:           EmotionPride,
			Name:           "Pride",
			Tier:           TierNuanced,
			Icon:           "🦁",
			Description:    "Satisfaction in achievement and growth.",
			Produces:       EmotionHope,
			ProductionRate: decimal.NewFromFloat(0.2),
			BaseCost:       decimal.NewFromInt(2000),
			MinStorage:     8,
			MaxStorage:     800,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(1000),
		},
		{
			Type:           EmotionGratitude,
			Name:           "Gratitude",
			Tier:           TierDeep,
			Icon:           "🙏",
			Description:    "Deep appreciation for the gifts of existence.",
			Produces:       EmotionNostalgia,
			ProductionRate: decimal.NewFromFloat(0.15),
			BaseCost:       decimal.NewFromInt(10000),
			MinStorage:     5,
			MaxStorage:     500,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(5000),
		},
		{
			Type:           EmotionSerenity,
			Name:           "Serenity",
			Tier:           TierDeep,
			Icon:           "🧘",
			Description:    "Perfect peace and acceptance.",
			Produces:       EmotionPride,
			ProductionRate: decimal.NewFromFloat(0.1),
			BaseCost:       decimal.NewFromInt(8000),
			MinStorage:     3,
			MaxStorage:     300,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(4000),
		},
		{
			Type:           EmotionTranscendence,
			Name:           "Transcendence",
			Tier:           TierProfound,
			Icon:           "✨",
			Description:    "The ineffable beyond language. True enlightenment.",
			Produces:       EmotionGratitude,
			ProductionRate: decimal.NewFromFloat(0.05),
			BaseCost:       decimal.NewFromInt(50000),
			MinStorage:     1,
			MaxStorage:     100,
			BaseClickValue: decimal.Zero,
			UnlockCost:     decimal.NewFromInt(25000),
		},
	}
}

// GetEmotion returns the definition for a specific emotion type
func GetEmotion(emotionType EmotionType) *EmotionDefinition {
	emotions := GetAllEmotions()
	for i := range emotions {
		if emotions[i].Type == emotionType {
			return &emotions[i]
		}
	}
	return nil
}

// GetEmotionsByTier returns all emotions of a specific tier
func GetEmotionsByTier(tier EmotionTier) []EmotionDefinition {
	result := []EmotionDefinition{}
	for _, emotion := range GetAllEmotions() {
		if emotion.Tier == tier {
			result = append(result, emotion)
		}
	}
	return result
}

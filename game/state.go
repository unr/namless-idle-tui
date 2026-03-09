package game

import (
	"time"

	"github.com/shopspring/decimal"
)

// GameState represents the complete state of the game
type GameState struct {
	// Resources
	Resources        map[EmotionType]*EmotionResource
	UnlockedEmotions map[EmotionType]bool

	// Multipliers and bonuses
	ClickMultiplier            decimal.Decimal
	GlobalProductionMultiplier decimal.Decimal
	OfflineEfficiency          decimal.Decimal

	// Statistics
	TotalClicks      int
	TotalPlaytime    float64
	CustomersServed  int
	RecipesDiscovered map[string]bool

	// Prestige
	EmotionalDepth int
	PrestigeCount  int
	EthicalScore   decimal.Decimal

	// Timestamps
	LastSaveTime time.Time
	LastTickTime time.Time

	// Game state
	GamePaused bool

	// Calculator instance
	Calculator *ResourceCalculator
}

// NewGameState creates a new game with default starting values
func NewGameState() *GameState {
	gs := &GameState{
		Resources:                  make(map[EmotionType]*EmotionResource),
		UnlockedEmotions:           make(map[EmotionType]bool),
		RecipesDiscovered:          make(map[string]bool),
		ClickMultiplier:            decimal.NewFromInt(1),
		GlobalProductionMultiplier: decimal.NewFromInt(1),
		OfflineEfficiency:          decimal.NewFromInt(1),
		TotalClicks:                0,
		TotalPlaytime:              0,
		CustomersServed:            0,
		EmotionalDepth:             0,
		PrestigeCount:              0,
		EthicalScore:               decimal.NewFromInt(50),
		LastSaveTime:               time.Now(),
		LastTickTime:               time.Now(),
		GamePaused:                 false,
		Calculator:                 &ResourceCalculator{},
	}

	// Start with smiles unlocked
	gs.UnlockEmotion(EmotionSmiles)

	return gs
}

// UnlockEmotion unlocks a new emotion type
func (gs *GameState) UnlockEmotion(emotionType EmotionType) bool {
	if gs.UnlockedEmotions[emotionType] {
		return false
	}

	gs.UnlockedEmotions[emotionType] = true
	gs.Resources[emotionType] = NewEmotionResource(emotionType)
	return true
}

// GetResource retrieves a resource by emotion type, creating it if needed
func (gs *GameState) GetResource(emotionType EmotionType) *EmotionResource {
	if resource, ok := gs.Resources[emotionType]; ok {
		return resource
	}

	// Create if not exists
	resource := NewEmotionResource(emotionType)
	gs.Resources[emotionType] = resource
	return resource
}

// PerformClick harvests smiles manually
func (gs *GameState) PerformClick() decimal.Decimal {
	smilesResource := gs.GetResource(EmotionSmiles)
	definition := GetEmotion(EmotionSmiles)

	// Calculate click power
	clickPower := gs.Calculator.CalculateClickPower(
		definition.BaseClickValue,
		gs.ClickMultiplier,
		decimal.NewFromInt(1), // TODO: Implement mood bonus
	)

	// Add to resource
	added := smilesResource.AddAmount(clickPower)
	gs.TotalClicks++

	return added
}

// CanAffordProducer checks if player can afford to buy a producer
func (gs *GameState) CanAffordProducer(emotionType EmotionType) bool {
	if !gs.UnlockedEmotions[emotionType] {
		return false
	}

	definition := GetEmotion(emotionType)
	resource := gs.GetResource(emotionType)

	cost := gs.Calculator.CalculateProducerCost(definition.BaseCost, resource.ProducerCount)

	// Check if we can afford (smiles are the currency)
	smilesResource := gs.GetResource(EmotionSmiles)
	return smilesResource.CanAfford(cost)
}

// PurchaseProducer attempts to purchase a producer for the given emotion
func (gs *GameState) PurchaseProducer(emotionType EmotionType) bool {
	if !gs.UnlockedEmotions[emotionType] {
		return false
	}

	definition := GetEmotion(emotionType)
	resource := gs.GetResource(emotionType)

	cost := gs.Calculator.CalculateProducerCost(definition.BaseCost, resource.ProducerCount)

	// Try to deduct cost
	smilesResource := gs.GetResource(EmotionSmiles)
	if !smilesResource.RemoveAmount(cost) {
		return false
	}

	// Purchase successful
	resource.ProducerCount++
	return true
}

// GetPrestigeBonus calculates the current prestige production bonus
func (gs *GameState) GetPrestigeBonus() decimal.Decimal {
	return gs.Calculator.CalculatePrestigeBonus(gs.EmotionalDepth)
}

// AdjustEthicalScore adjusts the ethical score, clamping between 0 and 100
func (gs *GameState) AdjustEthicalScore(delta decimal.Decimal) {
	gs.EthicalScore = gs.EthicalScore.Add(delta)

	// Clamp to 0-100
	if gs.EthicalScore.LessThan(decimal.Zero) {
		gs.EthicalScore = decimal.Zero
	} else if gs.EthicalScore.GreaterThan(decimal.NewFromInt(100)) {
		gs.EthicalScore = decimal.NewFromInt(100)
	}
}

// CalculateEmotionalDepthGain calculates how much ED would be gained from prestige
func (gs *GameState) CalculateEmotionalDepthGain() int {
	recipesBonus := len(gs.RecipesDiscovered)
	satisfactionBonus := gs.CustomersServed / 10 // 1 point per 10 customers

	ethicsFloat, _ := gs.EthicalScore.Float64()
	ethicsBonus := ethicsFloat / 100.0

	edGain := int(float64(recipesBonus+satisfactionBonus) * ethicsBonus)
	return edGain
}

// CanPrestige checks if the player meets the requirements to prestige
func (gs *GameState) CanPrestige() (bool, string) {
	minRecipes := 3
	minCustomers := 10

	recipesM := len(gs.RecipesDiscovered) >= minRecipes
	customersM := gs.CustomersServed >= minCustomers

	if recipesM && customersM {
		return true, "Ready to prestige!"
	}

	reason := "Need: "
	if !recipesM {
		reason += "3 recipes "
	}
	if !customersM {
		reason += "10 customers"
	}

	return false, reason
}

// ResetForPrestige performs a prestige reset
func (gs *GameState) ResetForPrestige() int {
	edGained := gs.CalculateEmotionalDepthGain()

	// Update prestige data
	gs.EmotionalDepth += edGained
	gs.PrestigeCount++

	// Reset resources (keep only smiles, reset amount)
	gs.Resources = make(map[EmotionType]*EmotionResource)
	gs.UnlockedEmotions = make(map[EmotionType]bool)
	gs.UnlockEmotion(EmotionSmiles)

	// Reset statistics (keep prestige data and ethical score)
	gs.TotalClicks = 0
	gs.CustomersServed = 0
	gs.RecipesDiscovered = make(map[string]bool)

	// Reset multipliers (except prestige bonus)
	gs.ClickMultiplier = decimal.NewFromInt(1)
	gs.GlobalProductionMultiplier = decimal.NewFromInt(1)
	gs.OfflineEfficiency = decimal.NewFromInt(1)

	return edGained
}

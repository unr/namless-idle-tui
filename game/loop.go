package game

import (
	"time"

	"github.com/shopspring/decimal"
)

// GameLoop manages the game update loop with delta-time calculations
type GameLoop struct {
	State           *GameState
	AccumulatedTime float64
}

// NewGameLoop creates a new game loop
func NewGameLoop(state *GameState) *GameLoop {
	return &GameLoop{
		State:           state,
		AccumulatedTime: 0.0,
	}
}

// Update is the main update method called each frame
func (gl *GameLoop) Update(deltaTime float64) {
	if gl.State.GamePaused {
		return
	}

	// Update total playtime
	gl.State.TotalPlaytime += deltaTime

	// Apply game logic
	gl.ApplyPassiveGeneration(deltaTime)
	gl.ApplyPurityDecay(deltaTime)
	gl.CheckStorageCapacity()
}

// ApplyPassiveGeneration applies passive resource generation based on producers
func (gl *GameLoop) ApplyPassiveGeneration(deltaTime float64) {
	if deltaTime <= 0 {
		return
	}

	// Calculate prestige bonus once
	prestigeBonus := gl.State.GetPrestigeBonus()

	// Process each emotion type
	for emotionType, resource := range gl.State.Resources {
		// Skip if no producers
		if resource.ProducerCount == 0 {
			continue
		}

		// Get emotion definition
		definition := GetEmotion(emotionType)
		if definition == nil {
			continue
		}

		// Skip tier 0 (smiles don't produce anything themselves)
		if definition.Tier == TierBasic {
			continue
		}

		// Get the emotion this produces
		producedEmotion := definition.Produces
		if producedEmotion == "" {
			continue
		}

		// Get or create the target resource
		targetResource := gl.State.GetResource(producedEmotion)

		// Get storage state for production modifier
		storageState := gl.State.Calculator.GetStorageState(targetResource.StoragePercentage())

		// Calculate production rate
		productionRate := gl.State.Calculator.CalculateProduction(
			definition.ProductionRate,
			resource.ProducerCount,
			gl.State.GlobalProductionMultiplier,
			prestigeBonus,
			storageState,
		)

		// Calculate amount produced this frame
		amountProduced := productionRate.Mul(decimal.NewFromFloat(deltaTime))

		// Add to target resource (respects storage capacity)
		if amountProduced.GreaterThan(decimal.Zero) {
			targetResource.AddAmount(amountProduced)
		}
	}
}

// ApplyPurityDecay applies purity decay to all stored emotions
func (gl *GameLoop) ApplyPurityDecay(deltaTime float64) {
	if deltaTime <= 0 {
		return
	}

	// Apply decay to all resources with stored amounts
	for _, resource := range gl.State.Resources {
		if resource.Amount.GreaterThan(decimal.Zero) {
			resource.Purity = gl.State.Calculator.CalculatePurityDecay(
				resource.Purity,
				deltaTime,
			)
		}
	}
}

// CheckStorageCapacity checks storage capacity and applies overflow penalties
func (gl *GameLoop) CheckStorageCapacity() {
	for _, resource := range gl.State.Resources {
		if resource.IsOverflowing() {
			// Apply overflow penalty: -10% purity
			resource.Purity = resource.Purity.Sub(decimal.NewFromInt(10))
			if resource.Purity.LessThan(decimal.Zero) {
				resource.Purity = decimal.Zero
			}

			// Cap resources at storage capacity
			maxAmount := decimal.NewFromInt(int64(resource.StorageCapacity))
			if resource.Amount.GreaterThan(maxAmount) {
				resource.Amount = maxAmount
			}
		}
	}
}

// GetProductionRate calculates the current production rate for an emotion
func (gl *GameLoop) GetProductionRate(emotionType EmotionType) decimal.Decimal {
	resource := gl.State.GetResource(emotionType)
	if resource == nil || resource.ProducerCount == 0 {
		return decimal.Zero
	}

	definition := GetEmotion(emotionType)
	if definition == nil || definition.Produces == "" {
		return decimal.Zero
	}

	// Get target resource for storage state
	targetResource := gl.State.GetResource(definition.Produces)
	storageState := gl.State.Calculator.GetStorageState(targetResource.StoragePercentage())

	prestigeBonus := gl.State.GetPrestigeBonus()

	return gl.State.Calculator.CalculateProduction(
		definition.ProductionRate,
		resource.ProducerCount,
		gl.State.GlobalProductionMultiplier,
		prestigeBonus,
		storageState,
	)
}

// ForceTick simulates a game update (for testing)
func (gl *GameLoop) ForceTick(deltaTime float64) {
	gl.Update(deltaTime)
}

// ProcessOfflineTime processes time spent offline
func (gl *GameLoop) ProcessOfflineTime(offlineSeconds float64) {
	if offlineSeconds <= 0 {
		return
	}

	// Calculate offline production for each resource
	for emotionType, resource := range gl.State.Resources {
		if resource.ProducerCount == 0 {
			continue
		}

		definition := GetEmotion(emotionType)
		if definition == nil || definition.Tier == TierBasic || definition.Produces == "" {
			continue
		}

		// Calculate production rate
		productionRate := gl.GetProductionRate(emotionType)

		// Get target resource
		targetResource := gl.State.GetResource(definition.Produces)

		// Calculate offline production with efficiency
		offlineProduction := gl.State.Calculator.CalculateOfflineProduction(
			productionRate,
			offlineSeconds,
			targetResource.StorageCapacity,
			gl.State.OfflineEfficiency,
		)

		// Add to target resource
		targetResource.AddAmount(offlineProduction)
	}

	// Add to total playtime
	gl.State.TotalPlaytime += offlineSeconds
}

// Reset resets the game loop state
func (gl *GameLoop) Reset() {
	gl.AccumulatedTime = 0.0
	gl.State.LastTickTime = time.Now()
}

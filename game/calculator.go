package game

import (
	"math"

	"github.com/shopspring/decimal"
)

// ResourceCalculator handles all production and cost calculations
type ResourceCalculator struct{}

const (
	// Cost growth formula: base_cost * (growth_rate ^ count)
	CostGrowthRate = 1.15

	// Purity decay rate: 0.1% per minute in storage
	PurityDecayPerMinute = 0.1
)

// Storage state modifiers for production
var StorageModifiers = map[string]decimal.Decimal{
	"empty":     decimal.NewFromFloat(1.0), // 0-25%: Normal production
	"moderate":  decimal.NewFromFloat(1.0), // 25-75%: Normal production
	"near_full": decimal.NewFromFloat(0.5), // 75-95%: Reduced production
	"full":      decimal.Zero,              // 95%+: Production stops
}

// CalculateProducerCost calculates the cost to purchase the next producer
// Uses exponential scaling: base_cost * (1.15 ^ current_count)
func (rc *ResourceCalculator) CalculateProducerCost(baseCost decimal.Decimal, currentCount int) decimal.Decimal {
	multiplier := math.Pow(CostGrowthRate, float64(currentCount))
	return baseCost.Mul(decimal.NewFromFloat(multiplier))
}

// CalculateProduction calculates the total production rate per second
// Formula: base_rate * producer_count * global_multiplier * prestige_bonus * storage_modifier
func (rc *ResourceCalculator) CalculateProduction(
	baseRate decimal.Decimal,
	producerCount int,
	globalMultiplier decimal.Decimal,
	prestigeBonus decimal.Decimal,
	storageState string,
) decimal.Decimal {
	if producerCount == 0 {
		return decimal.Zero
	}

	production := baseRate.Mul(decimal.NewFromInt(int64(producerCount)))
	production = production.Mul(globalMultiplier)
	production = production.Mul(prestigeBonus)

	// Apply storage modifier
	if modifier, ok := StorageModifiers[storageState]; ok {
		production = production.Mul(modifier)
	}

	return production
}

// CalculatePurityDecay calculates purity decay over time
// Purity decays at 0.1% per minute in storage
func (rc *ResourceCalculator) CalculatePurityDecay(currentPurity decimal.Decimal, deltaTime float64) decimal.Decimal {
	if currentPurity.LessThanOrEqual(decimal.Zero) {
		return decimal.Zero
	}

	decayPerSecond := decimal.NewFromFloat(PurityDecayPerMinute / 60.0)
	decayAmount := decayPerSecond.Mul(decimal.NewFromFloat(deltaTime))

	newPurity := currentPurity.Sub(decayAmount)
	if newPurity.LessThan(decimal.Zero) {
		return decimal.Zero
	}
	return newPurity
}

// GetStorageState determines the storage state based on fill percentage
func (rc *ResourceCalculator) GetStorageState(storagePercentage float64) string {
	if storagePercentage >= 0.95 {
		return "full"
	} else if storagePercentage >= 0.75 {
		return "near_full"
	} else if storagePercentage >= 0.25 {
		return "moderate"
	}
	return "empty"
}

// CalculatePrestigeBonus calculates the prestige production bonus
// Formula: 1 + (emotional_depth * 0.03)
// Each point of Emotional Depth gives +3% to all production
func (rc *ResourceCalculator) CalculatePrestigeBonus(emotionalDepth int) decimal.Decimal {
	bonus := decimal.NewFromFloat(float64(emotionalDepth) * 0.03)
	return decimal.NewFromInt(1).Add(bonus)
}

// CalculateClickPower calculates the amount gained from a manual click
// Formula: base_click * click_multiplier * mood_bonus
func (rc *ResourceCalculator) CalculateClickPower(
	baseClick decimal.Decimal,
	clickMultiplier decimal.Decimal,
	moodBonus decimal.Decimal,
) decimal.Decimal {
	return baseClick.Mul(clickMultiplier).Mul(moodBonus)
}

// CalculatePurityPriceModifier calculates sell price modifier based on purity
// Formula: purity% × base_price
func (rc *ResourceCalculator) CalculatePurityPriceModifier(purity decimal.Decimal) decimal.Decimal {
	return purity.Div(decimal.NewFromInt(100))
}

// CalculateOfflineProduction calculates resources gained during offline time
// Production is capped by storage capacity and affected by offline efficiency
func (rc *ResourceCalculator) CalculateOfflineProduction(
	productionRate decimal.Decimal,
	offlineSeconds float64,
	storageCapacity int,
	offlineEfficiency decimal.Decimal,
) decimal.Decimal {
	if offlineSeconds <= 0 {
		return decimal.Zero
	}

	// Calculate total production
	rawProduction := productionRate.Mul(decimal.NewFromFloat(offlineSeconds))
	rawProduction = rawProduction.Mul(offlineEfficiency)

	// Cap by storage capacity
	maxAmount := decimal.NewFromInt(int64(storageCapacity))
	if rawProduction.GreaterThan(maxAmount) {
		return maxAmount
	}
	return rawProduction
}

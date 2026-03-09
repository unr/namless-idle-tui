package game

import (
	"github.com/shopspring/decimal"
)

// EmotionResource represents a stored emotion with amount, purity, and capacity
type EmotionResource struct {
	EmotionType     EmotionType
	Amount          decimal.Decimal
	Purity          decimal.Decimal // 0-100
	StorageCapacity int
	ProducerCount   int
}

// NewEmotionResource creates a new resource for the given emotion type
func NewEmotionResource(emotionType EmotionType) *EmotionResource {
	definition := GetEmotion(emotionType)
	if definition == nil {
		return nil
	}

	return &EmotionResource{
		EmotionType:     emotionType,
		Amount:          decimal.Zero,
		Purity:          decimal.NewFromInt(100),
		StorageCapacity: definition.MinStorage,
		ProducerCount:   0,
	}
}

// StoragePercentage returns the fill percentage (0.0 to 1.0+)
func (r *EmotionResource) StoragePercentage() float64 {
	if r.StorageCapacity == 0 {
		return 0.0
	}
	percentage, _ := r.Amount.Div(decimal.NewFromInt(int64(r.StorageCapacity))).Float64()
	return percentage
}

// IsFull returns true if storage is at or near capacity (95%+)
func (r *EmotionResource) IsFull() bool {
	return r.StoragePercentage() >= 0.95
}

// IsOverflowing returns true if storage has exceeded capacity
func (r *EmotionResource) IsOverflowing() bool {
	return r.StoragePercentage() > 1.0
}

// AddAmount adds resources, respecting storage capacity
// Returns the amount that was actually added
func (r *EmotionResource) AddAmount(amount decimal.Decimal) decimal.Decimal {
	if amount.LessThanOrEqual(decimal.Zero) {
		return decimal.Zero
	}

	availableSpace := decimal.NewFromInt(int64(r.StorageCapacity)).Sub(r.Amount)
	if availableSpace.LessThanOrEqual(decimal.Zero) {
		return decimal.Zero
	}

	amountToAdd := amount
	if amount.GreaterThan(availableSpace) {
		amountToAdd = availableSpace
	}

	r.Amount = r.Amount.Add(amountToAdd)
	return amountToAdd
}

// RemoveAmount removes resources if available
// Returns true if the full amount was removed, false if insufficient
func (r *EmotionResource) RemoveAmount(amount decimal.Decimal) bool {
	if amount.LessThanOrEqual(decimal.Zero) {
		return true
	}

	if r.Amount.GreaterThanOrEqual(amount) {
		r.Amount = r.Amount.Sub(amount)
		return true
	}
	return false
}

// CanAfford checks if we have enough of this resource
func (r *EmotionResource) CanAfford(amount decimal.Decimal) bool {
	return r.Amount.GreaterThanOrEqual(amount)
}

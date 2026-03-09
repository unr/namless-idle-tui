package persistence

import (
	"encoding/json"
	"os"
	"path/filepath"
	"time"

	"github.com/shopspring/decimal"
	"github.com/unr/emotion-merchant/game"
)

// SaveData represents the serializable game state
type SaveData struct {
	Resources        map[game.EmotionType]ResourceData `json:"resources"`
	UnlockedEmotions []game.EmotionType                `json:"unlocked_emotions"`

	ClickMultiplier            string `json:"click_multiplier"`
	GlobalProductionMultiplier string `json:"global_production_multiplier"`
	OfflineEfficiency          string `json:"offline_efficiency"`

	TotalClicks       int              `json:"total_clicks"`
	TotalPlaytime     float64          `json:"total_playtime"`
	CustomersServed   int              `json:"customers_served"`
	RecipesDiscovered []string         `json:"recipes_discovered"`
	EmotionalDepth    int              `json:"emotional_depth"`
	PrestigeCount     int              `json:"prestige_count"`
	EthicalScore      string           `json:"ethical_score"`
	LastSaveTime      time.Time        `json:"last_save_time"`
}

// ResourceData represents a serializable resource
type ResourceData struct {
	Amount          string `json:"amount"`
	Purity          string `json:"purity"`
	StorageCapacity int    `json:"storage_capacity"`
	ProducerCount   int    `json:"producer_count"`
}

// SaveGameState saves the game state to a JSON file
func SaveGameState(state *game.GameState, filename string) error {
	// Convert resources map
	resources := make(map[game.EmotionType]ResourceData)
	for emotionType, resource := range state.Resources {
		resources[emotionType] = ResourceData{
			Amount:          resource.Amount.String(),
			Purity:          resource.Purity.String(),
			StorageCapacity: resource.StorageCapacity,
			ProducerCount:   resource.ProducerCount,
		}
	}

	// Convert unlocked emotions map to slice
	unlockedEmotions := []game.EmotionType{}
	for emotion := range state.UnlockedEmotions {
		unlockedEmotions = append(unlockedEmotions, emotion)
	}

	// Convert recipes discovered
	recipes := []string{}
	for recipe := range state.RecipesDiscovered {
		recipes = append(recipes, recipe)
	}

	saveData := SaveData{
		Resources:                  resources,
		UnlockedEmotions:           unlockedEmotions,
		ClickMultiplier:            state.ClickMultiplier.String(),
		GlobalProductionMultiplier: state.GlobalProductionMultiplier.String(),
		OfflineEfficiency:          state.OfflineEfficiency.String(),
		TotalClicks:                state.TotalClicks,
		TotalPlaytime:              state.TotalPlaytime,
		CustomersServed:            state.CustomersServed,
		RecipesDiscovered:          recipes,
		EmotionalDepth:             state.EmotionalDepth,
		PrestigeCount:              state.PrestigeCount,
		EthicalScore:               state.EthicalScore.String(),
		LastSaveTime:               time.Now(),
	}

	// Marshal to JSON
	data, err := json.MarshalIndent(saveData, "", "  ")
	if err != nil {
		return err
	}

	// Ensure directory exists
	dir := filepath.Dir(filename)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	// Write to file
	return os.WriteFile(filename, data, 0644)
}

// LoadGameState loads the game state from a JSON file
func LoadGameState(filename string) (*game.GameState, error) {
	// Read file
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	// Unmarshal JSON
	var saveData SaveData
	if err := json.Unmarshal(data, &saveData); err != nil {
		return nil, err
	}

	// Create new game state
	state := game.NewGameState()

	// Restore decimal values
	state.ClickMultiplier, _ = decimal.NewFromString(saveData.ClickMultiplier)
	state.GlobalProductionMultiplier, _ = decimal.NewFromString(saveData.GlobalProductionMultiplier)
	state.OfflineEfficiency, _ = decimal.NewFromString(saveData.OfflineEfficiency)
	state.EthicalScore, _ = decimal.NewFromString(saveData.EthicalScore)

	// Restore statistics
	state.TotalClicks = saveData.TotalClicks
	state.TotalPlaytime = saveData.TotalPlaytime
	state.CustomersServed = saveData.CustomersServed
	state.EmotionalDepth = saveData.EmotionalDepth
	state.PrestigeCount = saveData.PrestigeCount

	// Restore unlocked emotions
	state.UnlockedEmotions = make(map[game.EmotionType]bool)
	for _, emotion := range saveData.UnlockedEmotions {
		state.UnlockedEmotions[emotion] = true
	}

	// Restore resources
	state.Resources = make(map[game.EmotionType]*game.EmotionResource)
	for emotionType, resourceData := range saveData.Resources {
		amount, _ := decimal.NewFromString(resourceData.Amount)
		purity, _ := decimal.NewFromString(resourceData.Purity)

		resource := &game.EmotionResource{
			EmotionType:     emotionType,
			Amount:          amount,
			Purity:          purity,
			StorageCapacity: resourceData.StorageCapacity,
			ProducerCount:   resourceData.ProducerCount,
		}
		state.Resources[emotionType] = resource
	}

	// Restore recipes
	state.RecipesDiscovered = make(map[string]bool)
	for _, recipe := range saveData.RecipesDiscovered {
		state.RecipesDiscovered[recipe] = true
	}

	state.LastSaveTime = saveData.LastSaveTime

	return state, nil
}

// GetDefaultSaveLocation returns the default save file location
func GetDefaultSaveLocation() string {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		homeDir = "."
	}
	return filepath.Join(homeDir, ".emotion-merchant", "save.json")
}

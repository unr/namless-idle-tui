package ui

import (
	"time"

	"github.com/unr/emotion-merchant/game"
)

// TickMsg is sent on each game update tick
type TickMsg time.Time

// HarvestMsg is sent when the player clicks to harvest smiles
type HarvestMsg struct{}

// PurchaseProducerMsg is sent when the player wants to buy a producer
type PurchaseProducerMsg struct {
	EmotionType game.EmotionType
}

// UnlockEmotionMsg is sent when the player unlocks a new emotion
type UnlockEmotionMsg struct{
	EmotionType game.EmotionType
}

// PrestigeMsg is sent when the player wants to prestige
type PrestigeMsg struct{}

// SaveGameMsg is sent to trigger a game save
type SaveGameMsg struct{}

// LoadGameMsg is sent to trigger a game load
type LoadGameMsg struct{}

// ChangeScreenMsg is sent to navigate between screens
type ChangeScreenMsg struct {
	Screen ScreenType
}

// ScreenType represents different screens in the game
type ScreenType int

const (
	ScreenGame ScreenType = iota
	ScreenProducers
	ScreenStats
	ScreenPrestige
	ScreenHelp
)

func (s ScreenType) String() string {
	switch s {
	case ScreenGame:
		return "Game"
	case ScreenProducers:
		return "Producers"
	case ScreenStats:
		return "Stats"
	case ScreenPrestige:
		return "Prestige"
	case ScreenHelp:
		return "Help"
	default:
		return "Unknown"
	}
}

package ui

import (
	"fmt"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/unr/emotion-merchant/game"
	"github.com/unr/emotion-merchant/persistence"
)

// Model represents the Bubble Tea model for the entire application
type Model struct {
	GameState    *game.GameState
	GameLoop     *game.GameLoop
	CurrentScreen ScreenType
	LastMessage   string
	MessageColor  string
	Width         int
	Height        int
	SaveLocation  string
}

// NewModel creates a new Model instance
func NewModel() Model {
	gameState := game.NewGameState()
	gameLoop := game.NewGameLoop(gameState)

	return Model{
		GameState:     gameState,
		GameLoop:      gameLoop,
		CurrentScreen: ScreenGame,
		LastMessage:   "Welcome to Emotion Merchant!",
		MessageColor:  "success",
		SaveLocation:  persistence.GetDefaultSaveLocation(),
	}
}

// Init initializes the model (required by tea.Model interface)
func (m Model) Init() tea.Cmd {
	// Start the game tick timer
	return tea.Batch(
		tickCmd(),
		tea.EnterAltScreen,
	)
}

// tickCmd returns a command that sends a TickMsg after a delay
func tickCmd() tea.Cmd {
	return tea.Tick(time.Second/10, func(t time.Time) tea.Msg {
		return TickMsg(t)
	})
}

// Update handles messages and updates the model (required by tea.Model interface)
func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		return m.handleKeyPress(msg)

	case tea.WindowSizeMsg:
		m.Width = msg.Width
		m.Height = msg.Height
		return m, nil

	case TickMsg:
		// Calculate delta time
		now := time.Now()
		deltaTime := now.Sub(m.GameState.LastTickTime).Seconds()
		m.GameState.LastTickTime = now

		// Update game logic
		m.GameLoop.Update(deltaTime)

		// Continue ticking
		return m, tickCmd()

	case HarvestMsg:
		amount := m.GameState.PerformClick()
		amountFloat, _ := amount.Float64()
		m.LastMessage = fmt.Sprintf("☺ Harvested %.1f Smiles!", amountFloat)
		m.MessageColor = "success"
		return m, nil

	case PurchaseProducerMsg:
		if m.GameState.PurchaseProducer(msg.EmotionType) {
			definition := game.GetEmotion(msg.EmotionType)
			m.LastMessage = fmt.Sprintf("✓ Purchased %s producer!", definition.Name)
			m.MessageColor = "success"
		} else {
			m.LastMessage = "✗ Cannot afford that producer"
			m.MessageColor = "error"
		}
		return m, nil

	case UnlockEmotionMsg:
		if m.GameState.UnlockEmotion(msg.EmotionType) {
			definition := game.GetEmotion(msg.EmotionType)
			m.LastMessage = fmt.Sprintf("🎉 Unlocked %s!", definition.Name)
			m.MessageColor = "success"
		} else {
			m.LastMessage = "Already unlocked"
			m.MessageColor = "error"
		}
		return m, nil

	case PrestigeMsg:
		if canPrestige, reason := m.GameState.CanPrestige(); canPrestige {
			edGain := m.GameState.ResetForPrestige()
			m.LastMessage = fmt.Sprintf("✨ Prestige! Gained %d Emotional Depth", edGain)
			m.MessageColor = "success"
		} else {
			m.LastMessage = reason
			m.MessageColor = "error"
		}
		return m, nil

	case SaveGameMsg:
		if err := persistence.SaveGameState(m.GameState, m.SaveLocation); err != nil {
			m.LastMessage = fmt.Sprintf("✗ Save failed: %v", err)
			m.MessageColor = "error"
		} else {
			m.LastMessage = "✓ Game saved!"
			m.MessageColor = "success"
		}
		return m, nil

	case LoadGameMsg:
		if loadedState, err := persistence.LoadGameState(m.SaveLocation); err != nil {
			m.LastMessage = fmt.Sprintf("✗ Load failed: %v", err)
			m.MessageColor = "error"
		} else {
			m.GameState = loadedState
			m.GameLoop = game.NewGameLoop(loadedState)
			m.LastMessage = "✓ Game loaded!"
			m.MessageColor = "success"
		}
		return m, nil

	case ChangeScreenMsg:
		m.CurrentScreen = msg.Screen
		m.LastMessage = fmt.Sprintf("Switched to %s screen", msg.Screen.String())
		m.MessageColor = "success"
		return m, nil
	}

	return m, nil
}

// handleKeyPress processes keyboard input
func (m Model) handleKeyPress(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch msg.String() {
	case "ctrl+c", "q":
		// Save before quitting
		_ = persistence.SaveGameState(m.GameState, m.SaveLocation)
		return m, tea.Quit

	case "h":
		// Harvest smiles
		return m.Update(HarvestMsg{})

	case "s":
		// Save game
		return m.Update(SaveGameMsg{})

	case "l":
		// Load game
		return m.Update(LoadGameMsg{})

	case "1":
		// Switch to game screen
		return m.Update(ChangeScreenMsg{Screen: ScreenGame})

	case "2":
		// Switch to producers screen
		return m.Update(ChangeScreenMsg{Screen: ScreenProducers})

	case "3":
		// Switch to stats screen
		return m.Update(ChangeScreenMsg{Screen: ScreenStats})

	case "4":
		// Switch to prestige screen
		return m.Update(ChangeScreenMsg{Screen: ScreenPrestige})

	case "5":
		// Switch to help screen
		return m.Update(ChangeScreenMsg{Screen: ScreenHelp})

	case "p":
		// Prestige
		return m.Update(PrestigeMsg{})

	// Quick buy keys for first few emotions
	case "j":
		if m.GameState.UnlockedEmotions[game.EmotionJoy] {
			return m.Update(PurchaseProducerMsg{EmotionType: game.EmotionJoy})
		}
	case "o":
		if m.GameState.UnlockedEmotions[game.EmotionLove] {
			return m.Update(PurchaseProducerMsg{EmotionType: game.EmotionLove})
		}
	}

	return m, nil
}

// View renders the UI (required by tea.Model interface)
func (m Model) View() string {
	// Render current screen
	var content string
	switch m.CurrentScreen {
	case ScreenGame:
		content = m.viewGameScreen()
	case ScreenProducers:
		content = m.viewProducersScreen()
	case ScreenStats:
		content = m.viewStatsScreen()
	case ScreenPrestige:
		content = m.viewPrestigeScreen()
	case ScreenHelp:
		content = m.viewHelpScreen()
	default:
		content = "Unknown screen"
	}

	// Add navigation bar at bottom
	navBar := m.renderNavigationBar()

	// Add message at top
	messageBar := m.renderMessageBar()

	return ScreenStyle.Render(
		messageBar + "\n\n" +
		content + "\n\n" +
		navBar,
	)
}

// renderMessageBar renders the message bar at the top
func (m Model) renderMessageBar() string {
	var style lipgloss.Style
	switch m.MessageColor {
	case "success":
		style = SuccessStyle
	case "error":
		style = ErrorStyle
	default:
		style = HelpStyle
	}

	return style.Render(m.LastMessage)
}

// renderNavigationBar renders the navigation bar
func (m Model) renderNavigationBar() string {
	screens := []struct {
		key    string
		name   string
		screen ScreenType
	}{
		{"1", "Game", ScreenGame},
		{"2", "Producers", ScreenProducers},
		{"3", "Stats", ScreenStats},
		{"4", "Prestige", ScreenPrestige},
		{"5", "Help", ScreenHelp},
	}

	var buttons []string
	for _, s := range screens {
		label := fmt.Sprintf("[%s] %s", s.key, s.name)
		if s.screen == m.CurrentScreen {
			buttons = append(buttons, ButtonActiveStyle.Render(label))
		} else {
			buttons = append(buttons, ButtonStyle.Render(label))
		}
	}

	return lipgloss.JoinHorizontal(lipgloss.Left, buttons...)
}

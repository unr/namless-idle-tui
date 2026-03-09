package ui

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"github.com/unr/emotion-merchant/game"
)

// viewGameScreen renders the main game screen
func (m Model) viewGameScreen() string {
	var sections []string

	// Title
	title := TitleStyle.Render("✨ EMOTION MERCHANT ✨")
	sections = append(sections, title)

	// Resources panel
	sections = append(sections, m.renderResourcesPanel())

	// Actions panel
	sections = append(sections, m.renderActionsPanel())

	// Help text
	help := HelpStyle.Render("Press [h] to harvest smiles | [s] to save | [q] to quit")
	sections = append(sections, help)

	return strings.Join(sections, "\n\n")
}

// renderResourcesPanel renders the resources display
func (m Model) renderResourcesPanel() string {
	header := HeaderStyle.Render("📦 Resources")

	var rows []string

	// Get all unlocked emotions in tier order
	for _, definition := range game.GetAllEmotions() {
		if !m.GameState.UnlockedEmotions[definition.Type] {
			continue
		}

		resource := m.GameState.GetResource(definition.Type)

		// Format amount
		amountFloat, _ := resource.Amount.Float64()
		amountStr := FormatLargeNumber(amountFloat)

		// Format storage
		storageStr := fmt.Sprintf("%s/%d", amountStr, resource.StorageCapacity)

		// Format purity
		purityFloat, _ := resource.Purity.Float64()
		purityStr := fmt.Sprintf("%.1f%%", purityFloat)

		// Calculate production rate
		productionRate := m.GameLoop.GetProductionRate(definition.Type)
		productionFloat, _ := productionRate.Float64()
		var productionStr string
		if productionFloat > 0 {
			productionStr = fmt.Sprintf("+%.1f/s", productionFloat)
		} else {
			productionStr = "-"
		}

		// Build row
		row := lipgloss.JoinHorizontal(
			lipgloss.Left,
			ResourceNameStyle.Render(definition.Icon+" "+definition.Name),
			ResourceAmountStyle.Render(storageStr),
			lipgloss.NewStyle().Width(15).Foreground(ColorSuccess).Render(productionStr),
			lipgloss.NewStyle().Width(10).Foreground(ColorWarning).Render(purityStr),
		)

		rows = append(rows, row)
	}

	content := strings.Join(rows, "\n")

	return PanelStyle.Render(header + "\n" + content)
}

// renderActionsPanel renders the quick actions panel
func (m Model) renderActionsPanel() string {
	header := HeaderStyle.Render("⚡ Quick Actions")

	var actions []string

	// Harvest button
	harvestBtn := ButtonStyle.Render("  [h] Harvest Smiles  ")
	actions = append(actions, harvestBtn)

	// Quick buy buttons for unlocked emotions (first few)
	if m.GameState.UnlockedEmotions[game.EmotionJoy] {
		joy := m.GameState.GetResource(game.EmotionJoy)
		joyDef := game.GetEmotion(game.EmotionJoy)
		cost := m.GameState.Calculator.CalculateProducerCost(joyDef.BaseCost, joy.ProducerCount)
		costFloat, _ := cost.Float64()

		label := fmt.Sprintf("[j] Buy Joy (%.0f)", costFloat)
		if m.GameState.CanAffordProducer(game.EmotionJoy) {
			actions = append(actions, ButtonStyle.Render(label))
		} else {
			actions = append(actions, ButtonDisabledStyle.Render(label))
		}
	}

	if m.GameState.UnlockedEmotions[game.EmotionLove] {
		love := m.GameState.GetResource(game.EmotionLove)
		loveDef := game.GetEmotion(game.EmotionLove)
		cost := m.GameState.Calculator.CalculateProducerCost(loveDef.BaseCost, love.ProducerCount)
		costFloat, _ := cost.Float64()

		label := fmt.Sprintf("[o] Buy Love (%.0f)", costFloat)
		if m.GameState.CanAffordProducer(game.EmotionLove) {
			actions = append(actions, ButtonStyle.Render(label))
		} else {
			actions = append(actions, ButtonDisabledStyle.Render(label))
		}
	}

	content := strings.Join(actions, "  ")

	return PanelStyle.Render(header + "\n" + content)
}

// viewProducersScreen renders the producers screen
func (m Model) viewProducersScreen() string {
	header := HeaderStyle.Render("🏭 Producers & Unlocks")

	var rows []string

	// Show all emotions
	for _, definition := range game.GetAllEmotions() {
		isUnlocked := m.GameState.UnlockedEmotions[definition.Type]

		if !isUnlocked {
			// Show locked emotion with unlock cost
			unlockCostFloat, _ := definition.UnlockCost.Float64()
			row := fmt.Sprintf(
				"%s %s (Locked - Cost: %.0f)",
				definition.Icon,
				definition.Name,
				unlockCostFloat,
			)
			rows = append(rows, lipgloss.NewStyle().Foreground(ColorMuted).Render(row))
			continue
		}

		// Show unlocked emotion
		resource := m.GameState.GetResource(definition.Type)

		// Skip smiles (no producers)
		if definition.Tier == game.TierBasic {
			amountFloat, _ := resource.Amount.Float64()
			row := fmt.Sprintf(
				"%s %s: %s (Base resource - click to harvest)",
				definition.Icon,
				definition.Name,
				FormatLargeNumber(amountFloat),
			)
			rows = append(rows, row)
			continue
		}

		// Calculate cost for next producer
		cost := m.GameState.Calculator.CalculateProducerCost(definition.BaseCost, resource.ProducerCount)
		costFloat, _ := cost.Float64()

		// Production info
		productionRate := m.GameLoop.GetProductionRate(definition.Type)
		productionFloat, _ := productionRate.Float64()

		row := fmt.Sprintf(
			"%s %s: %d producers | Cost: %.0f | Production: %.1f/s",
			definition.Icon,
			definition.Name,
			resource.ProducerCount,
			costFloat,
			productionFloat,
		)

		if m.GameState.CanAffordProducer(definition.Type) {
			rows = append(rows, lipgloss.NewStyle().Foreground(ColorSuccess).Render(row))
		} else {
			rows = append(rows, row)
		}
	}

	content := strings.Join(rows, "\n")

	help := HelpStyle.Render("Use keybinds [j], [o], etc. to quickly buy producers")

	return PanelStyle.Render(header + "\n" + content + "\n\n" + help)
}

// viewStatsScreen renders the statistics screen
func (m Model) viewStatsScreen() string {
	header := HeaderStyle.Render("📊 Statistics")

	var stats []string

	// Format playtime
	hours := int(m.GameState.TotalPlaytime) / 3600
	minutes := (int(m.GameState.TotalPlaytime) % 3600) / 60
	seconds := int(m.GameState.TotalPlaytime) % 60
	playtimeStr := fmt.Sprintf("%dh %dm %ds", hours, minutes, seconds)

	stats = append(stats,
		m.renderStat("Total Playtime", playtimeStr),
		m.renderStat("Total Clicks", fmt.Sprintf("%d", m.GameState.TotalClicks)),
		m.renderStat("Customers Served", fmt.Sprintf("%d", m.GameState.CustomersServed)),
		m.renderStat("Recipes Discovered", fmt.Sprintf("%d", len(m.GameState.RecipesDiscovered))),
		"",
		m.renderStat("Prestige Count", fmt.Sprintf("%d", m.GameState.PrestigeCount)),
		m.renderStat("Emotional Depth", fmt.Sprintf("%d", m.GameState.EmotionalDepth)),
	)

	ethicsFloat, _ := m.GameState.EthicalScore.Float64()
	stats = append(stats,
		m.renderStat("Ethical Score", fmt.Sprintf("%.1f/100", ethicsFloat)),
	)

	// Multipliers
	stats = append(stats, "")
	stats = append(stats, HeaderStyle.Render("Multipliers"))

	clickMult, _ := m.GameState.ClickMultiplier.Float64()
	prodMult, _ := m.GameState.GlobalProductionMultiplier.Float64()
	offlineMult, _ := m.GameState.OfflineEfficiency.Float64()
	prestigeBonus, _ := m.GameState.GetPrestigeBonus().Float64()

	stats = append(stats,
		m.renderStat("Click Power", fmt.Sprintf("%.2fx", clickMult)),
		m.renderStat("Production", fmt.Sprintf("%.2fx", prodMult)),
		m.renderStat("Prestige Bonus", fmt.Sprintf("%.2fx", prestigeBonus)),
		m.renderStat("Offline Efficiency", fmt.Sprintf("%.2fx", offlineMult)),
	)

	content := strings.Join(stats, "\n")

	return PanelStyle.Render(header + "\n" + content)
}

// renderStat renders a stat row
func (m Model) renderStat(label, value string) string {
	return lipgloss.JoinHorizontal(
		lipgloss.Left,
		StatLabelStyle.Render(label+":"),
		StatValueStyle.Render(value),
	)
}

// viewPrestigeScreen renders the prestige screen
func (m Model) viewPrestigeScreen() string {
	header := HeaderStyle.Render("✨ Emotional Rebirth (Prestige)")

	description := lipgloss.NewStyle().Foreground(ColorMuted).Render(
		"Reset your progress to gain Emotional Depth, which provides permanent bonuses.\n" +
		"Each point of Emotional Depth grants +3% to all production.",
	)

	// Check requirements
	canPrestige, reason := m.GameState.CanPrestige()

	var status string
	if canPrestige {
		edGain := m.GameState.CalculateEmotionalDepthGain()
		status = SuccessStyle.Render(fmt.Sprintf("✓ Ready to prestige! You will gain %d Emotional Depth", edGain))
	} else {
		status = ErrorStyle.Render("✗ " + reason)
	}

	// What you'll keep
	keep := lipgloss.NewStyle().Foreground(ColorSuccess).Render(
		"You will keep:\n" +
		"  • Emotional Depth gained\n" +
		"  • Prestige count\n" +
		"  • Ethical score",
	)

	// What you'll lose
	lose := lipgloss.NewStyle().Foreground(ColorDanger).Render(
		"You will lose:\n" +
		"  • All resources and producers\n" +
		"  • Unlocked emotions (except Smiles)\n" +
		"  • Upgrades and multipliers\n" +
		"  • Customers served and recipes",
	)

	help := HelpStyle.Render("Press [p] to prestige")

	content := strings.Join([]string{
		description,
		"",
		status,
		"",
		keep,
		"",
		lose,
		"",
		help,
	}, "\n")

	return PanelStyle.Render(header + "\n" + content)
}

// viewHelpScreen renders the help screen
func (m Model) viewHelpScreen() string {
	header := HeaderStyle.Render("❓ Help & Controls")

	controls := []string{
		"Navigation:",
		"  [1] - Game Screen",
		"  [2] - Producers Screen",
		"  [3] - Stats Screen",
		"  [4] - Prestige Screen",
		"  [5] - Help Screen",
		"",
		"Game Actions:",
		"  [h] - Harvest Smiles (manual click)",
		"  [j] - Quick buy Joy producer",
		"  [o] - Quick buy Love producer",
		"  [p] - Prestige/Emotional Rebirth",
		"",
		"System:",
		"  [s] - Save game",
		"  [l] - Load game",
		"  [q] or [Ctrl+C] - Quit (auto-saves)",
		"",
		"About:",
		"Emotion Merchant is an idle game about harvesting and refining emotions.",
		"Start by clicking to harvest Smiles, then unlock higher-tier emotions.",
		"Producers automatically generate lower-tier emotions.",
		"When ready, prestige to gain Emotional Depth for permanent bonuses!",
	}

	content := strings.Join(controls, "\n")

	return PanelStyle.Render(header + "\n" + content)
}

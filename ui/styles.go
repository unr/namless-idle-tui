package ui

import (
	"fmt"

	"github.com/charmbracelet/lipgloss"
)

var (
	// Colors
	ColorPrimary   = lipgloss.Color("205") // Pink
	ColorSecondary = lipgloss.Color("99")  // Purple
	ColorSuccess   = lipgloss.Color("42")  // Green
	ColorWarning   = lipgloss.Color("220") // Yellow
	ColorDanger    = lipgloss.Color("196") // Red
	ColorMuted     = lipgloss.Color("240") // Gray

	// Base styles
	BaseStyle = lipgloss.NewStyle().
			Padding(1, 2)

	// Title style
	TitleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(ColorPrimary).
			Background(lipgloss.Color("235")).
			Padding(0, 1)

	// Header style
	HeaderStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(ColorSecondary).
			MarginBottom(1)

	// Resource row styles
	ResourceNameStyle = lipgloss.NewStyle().
				Width(15).
				Bold(true).
				Foreground(ColorPrimary)

	ResourceAmountStyle = lipgloss.NewStyle().
				Width(15).
				Align(lipgloss.Right).
				Foreground(ColorSuccess)

	ResourceStorageStyle = lipgloss.NewStyle().
				Width(20).
				Foreground(ColorMuted)

	// Button styles
	ButtonStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("15")).
			Background(ColorPrimary).
			Padding(0, 2).
			MarginRight(2)

	ButtonActiveStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color("15")).
				Background(ColorSecondary).
				Padding(0, 2).
				MarginRight(2).
				Bold(true)

	ButtonDisabledStyle = lipgloss.NewStyle().
				Foreground(ColorMuted).
				Background(lipgloss.Color("235")).
				Padding(0, 2).
				MarginRight(2)

	// Stats styles
	StatLabelStyle = lipgloss.NewStyle().
			Foreground(ColorMuted).
			Width(20)

	StatValueStyle = lipgloss.NewStyle().
			Foreground(ColorSuccess).
			Bold(true)

	// Help text
	HelpStyle = lipgloss.NewStyle().
			Foreground(ColorMuted).
			MarginTop(1)

	// Error style
	ErrorStyle = lipgloss.NewStyle().
			Foreground(ColorDanger).
			Bold(true)

	// Success message style
	SuccessStyle = lipgloss.NewStyle().
			Foreground(ColorSuccess).
			Bold(true)

	// Panel/box style
	PanelStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(ColorPrimary).
			Padding(1, 2).
			MarginBottom(1)

	// Screen container
	ScreenStyle = lipgloss.NewStyle().
			Padding(1)
)

// FormatLargeNumber formats large numbers with K/M/B suffixes
func FormatLargeNumber(value float64) string {
	if value < 1000 {
		return fmt.Sprintf("%.1f", value)
	} else if value < 1000000 {
		return fmt.Sprintf("%.1fK", value/1000)
	} else if value < 1000000000 {
		return fmt.Sprintf("%.1fM", value/1000000)
	}
	return fmt.Sprintf("%.1fB", value/1000000000)
}

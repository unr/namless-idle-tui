"""
Save/load management for the Emotion Merchant idle game.

This module handles JSON persistence, offline progression calculation,
and save file versioning.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Optional

from src.idle_game.models.game_state import GameState
from src.idle_game.models.resources import EmotionResource, ResourceCalculator
from src.idle_game.data.emotions import get_emotion


class SaveManager:
    """Manages game state persistence and offline progression.

    Save files are stored in JSON format at ~/.emotion_merchant/save.json
    with support for version migration.
    """

    # Current save file version
    SAVE_VERSION = 1

    # Default save location
    DEFAULT_SAVE_DIR = Path.home() / ".emotion_merchant"
    DEFAULT_SAVE_FILE = "save.json"

    def __init__(self, save_dir: Optional[Path] = None):
        """Initialize the save manager.

        Args:
            save_dir: Directory to store save files (defaults to ~/.emotion_merchant)
        """
        self.save_dir = save_dir or self.DEFAULT_SAVE_DIR
        self.save_file_path = self.save_dir / self.DEFAULT_SAVE_FILE

        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def save_game(self, game_state: GameState) -> bool:
        """Save the current game state to disk.

        Args:
            game_state: The GameState to save

        Returns:
            True if save successful, False otherwise
        """
        try:
            # Update last save time
            game_state.last_save_time = datetime.now()

            # Build save data dictionary
            save_data = {
                "version": self.SAVE_VERSION,
                "timestamp": game_state.last_save_time.isoformat(),
                "resources": self._serialize_resources(game_state.resources),
                "unlocked_emotions": list(game_state.unlocked_emotions),
                "click_multiplier": str(game_state.click_multiplier),
                "global_production_multiplier": str(game_state.global_production_multiplier),
                "offline_efficiency": str(game_state.offline_efficiency),
                "mood_rating": str(game_state.mood_rating),
                "total_clicks": game_state.total_clicks,
                "customers_served": game_state.customers_served,
                "recipes_discovered": list(game_state.recipes_discovered),
                "prestige_count": game_state.prestige_count,
                "emotional_depth": game_state.emotional_depth,
                "ethical_score": str(game_state.ethical_score),
                "total_playtime": game_state.total_playtime,
                "tutorial_completed": game_state.tutorial_completed,
                "tutorial_stage": game_state.tutorial_stage,
            }

            # Write to file
            with open(self.save_file_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, game_state: GameState) -> bool:
        """Load game state from disk and apply offline progression.

        Args:
            game_state: The GameState to load into

        Returns:
            True if load successful, False otherwise
        """
        try:
            # Check if save file exists
            if not self.save_file_path.exists():
                return False

            # Read save file
            with open(self.save_file_path, 'r') as f:
                save_data = json.load(f)

            # Check version and migrate if necessary
            version = save_data.get("version", 1)
            if version < self.SAVE_VERSION:
                save_data = self._migrate_save(save_data, version)

            # Load basic data
            game_state.click_multiplier = Decimal(save_data.get("click_multiplier", "1.0"))
            game_state.global_production_multiplier = Decimal(
                save_data.get("global_production_multiplier", "1.0")
            )
            game_state.offline_efficiency = Decimal(save_data.get("offline_efficiency", "1.0"))
            game_state.mood_rating = Decimal(save_data.get("mood_rating", "1.0"))
            game_state.total_clicks = save_data.get("total_clicks", 0)
            game_state.customers_served = save_data.get("customers_served", 0)
            game_state.recipes_discovered = set(save_data.get("recipes_discovered", []))
            game_state.prestige_count = save_data.get("prestige_count", 0)
            game_state.emotional_depth = save_data.get("emotional_depth", 0)
            game_state.ethical_score = Decimal(save_data.get("ethical_score", "50.0"))
            game_state.total_playtime = save_data.get("total_playtime", 0.0)
            game_state.tutorial_completed = save_data.get("tutorial_completed", False)
            game_state.tutorial_stage = save_data.get("tutorial_stage", 0)

            # Load resources
            game_state.resources = self._deserialize_resources(save_data.get("resources", {}))
            game_state.unlocked_emotions = set(save_data.get("unlocked_emotions", ["smiles"]))

            # Calculate offline progression
            timestamp_str = save_data.get("timestamp")
            if timestamp_str:
                last_save_time = datetime.fromisoformat(timestamp_str)
                self._apply_offline_progression(game_state, last_save_time)

            # Update last save time to now
            game_state.last_save_time = datetime.now()

            return True

        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def save_exists(self) -> bool:
        """Check if a save file exists.

        Returns:
            True if save file exists
        """
        return self.save_file_path.exists()

    def delete_save(self) -> bool:
        """Delete the save file.

        Returns:
            True if deletion successful
        """
        try:
            if self.save_file_path.exists():
                self.save_file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False

    def _serialize_resources(self, resources: Dict[str, EmotionResource]) -> Dict[str, Any]:
        """Serialize resources to JSON-compatible format.

        Args:
            resources: Dictionary of EmotionResource objects

        Returns:
            Dictionary suitable for JSON serialization
        """
        serialized = {}
        for emotion_type, resource in resources.items():
            serialized[emotion_type] = {
                "amount": str(resource.amount),
                "purity": str(resource.purity),
                "storage_capacity": resource.storage_capacity,
                "producer_count": resource.producer_count,
            }
        return serialized

    def _deserialize_resources(
        self, serialized: Dict[str, Any]
    ) -> Dict[str, EmotionResource]:
        """Deserialize resources from JSON format.

        Args:
            serialized: Dictionary from JSON

        Returns:
            Dictionary of EmotionResource objects
        """
        resources = {}
        for emotion_type, data in serialized.items():
            resources[emotion_type] = EmotionResource(
                emotion_type=emotion_type,
                amount=Decimal(data.get("amount", "0")),
                purity=Decimal(data.get("purity", "100.0")),
                storage_capacity=data.get("storage_capacity", 0),
                producer_count=data.get("producer_count", 0),
            )
        return resources

    def _apply_offline_progression(
        self, game_state: GameState, last_save_time: datetime
    ) -> None:
        """Calculate and apply offline progression.

        Args:
            game_state: The game state to update
            last_save_time: When the game was last saved
        """
        # Calculate time offline
        now = datetime.now()
        offline_duration = (now - last_save_time).total_seconds()

        # Cap offline time at 24 hours (86400 seconds)
        offline_duration = min(offline_duration, 86400)

        if offline_duration <= 0:
            return

        # Calculate prestige bonus
        prestige_bonus = game_state.get_prestige_bonus()

        # Process each emotion that has producers
        for emotion_type, resource in game_state.resources.items():
            if resource.producer_count == 0:
                continue

            # Get emotion definition
            emotion = get_emotion(emotion_type)

            # Skip tier 0 (smiles) - they don't produce anything
            if emotion.tier == 0:
                continue

            # Calculate production rate
            production_rate = ResourceCalculator.calculate_production(
                emotion.production_rate,
                resource.producer_count,
                game_state.global_production_multiplier,
                prestige_bonus,
            )

            # Calculate offline production (capped by storage)
            produced_emotion = emotion.produces
            if produced_emotion and produced_emotion in game_state.resources:
                target_resource = game_state.resources[produced_emotion]

                offline_amount = ResourceCalculator.calculate_offline_production(
                    production_rate,
                    offline_duration,
                    target_resource.storage_capacity,
                    game_state.offline_efficiency
                )

                # Add to target resource
                target_resource.add_amount(offline_amount)

        # Apply purity decay for all resources with amounts
        for resource in game_state.resources.values():
            if resource.amount > Decimal("0"):
                resource.purity = ResourceCalculator.calculate_purity_decay(
                    resource.purity,
                    offline_duration
                )

    def _migrate_save(self, save_data: Dict[str, Any], from_version: int) -> Dict[str, Any]:
        """Migrate save data from an older version.

        Args:
            save_data: The save data to migrate
            from_version: The version to migrate from

        Returns:
            Migrated save data
        """
        # Future version migrations go here
        # For now, just update the version number
        save_data["version"] = self.SAVE_VERSION
        return save_data

    def export_save(self, export_path: Path) -> bool:
        """Export save file to a different location.

        Args:
            export_path: Path to export to

        Returns:
            True if export successful
        """
        try:
            if not self.save_file_path.exists():
                return False

            with open(self.save_file_path, 'r') as source:
                with open(export_path, 'w') as dest:
                    dest.write(source.read())

            return True
        except Exception as e:
            print(f"Error exporting save: {e}")
            return False

    def import_save(self, import_path: Path) -> bool:
        """Import save file from a different location.

        Args:
            import_path: Path to import from

        Returns:
            True if import successful
        """
        try:
            if not import_path.exists():
                return False

            with open(import_path, 'r') as source:
                with open(self.save_file_path, 'w') as dest:
                    dest.write(source.read())

            return True
        except Exception as e:
            print(f"Error importing save: {e}")
            return False

"""
Game logic for the TCG game.
Contains the Game class with all turn management, combat, and AI logic.
"""

from typing import List, Optional, Callable
# Headless-safe import: tkinter may be unavailable on server runtimes
try:
    from tkinter import messagebox  # type: ignore
except Exception:
    class _MessageBoxStub:
        def showinfo(self, *args, **kwargs):
            return None
        def showwarning(self, *args, **kwargs):
            return None
        def showerror(self, *args, **kwargs):
            return None
        def askyesno(self, *args, **kwargs):
            return False
    messagebox = _MessageBoxStub()
from .models import Card, Player
from .ai_engine import DataDrivenAI


class Game:
    """Main game logic controller."""
    
    def __init__(self, player: Player, ai: Player, on_update):
        self.player = player
        self.ai = ai
        self.turn = 'player'
        self.on_update = on_update
        self.action_log: List[str] = []
        # track recent played cards for both sides for UI
        self.ai_played: List[Card] = []
        self.player_played: List[Card] = []
        # UI callback for choosing a blocker: should be set by UI
        self.ask_blocker: Optional[Callable[[Card], Optional[int]]] = None
        # Reference to root window (set by UI)
        self.root = None
        self.game_started = False  # Prevents check_end during initialization
        
        # AI decision maker - DataDrivenAI expects ai_config
        if ai.ai_config:
            self.ai_brain = DataDrivenAI(ai, ai.ai_config)
        else:
            # Default to medium difficulty if no config
            from .ai_engine import AIConfig
            default_config = AIConfig(5)
            self.ai_brain = DataDrivenAI(ai, default_config)

    def start(self):
        """Initialize the game state."""
        # Draw initial hand: 5 cards normally, 6 for Tacticus
        player_initial_cards = 6 if (self.player.champion and self.player.champion.ability_type == 'card_draw') else 5
        ai_initial_cards = 6 if (self.ai.champion and self.ai.champion.ability_type == 'card_draw') else 5
        
        for _ in range(player_initial_cards):
            self.player.draw_card()
        for _ in range(ai_initial_cards):
            self.ai.draw_card()
        
        self.player.max_mana = 1
        self.player.mana = 1
        self.ai.max_mana = 1
        self.ai.mana = 1
        
        # Log champion abilities
        if self.player.champion:
            self.log_action(f"Player Champion: {self.player.champion.name} - {self.player.champion.passive_name}")
        if self.ai.champion:
            self.log_action(f"AI Champion: {self.ai.champion.name} - {self.ai.champion.passive_name}")
        
        self.game_started = True  # Game is now fully initialized
        self.on_update()

    def start_turn(self, who: str):
        """Start a turn for the specified player."""
        p = self.player if who == 'player' else self.ai
        # increase mana on start of owner's turn
        p.max_mana = min(10, p.max_mana + 1)
        p.mana = p.max_mana
        
        # Apply champion passive: card draw
        draw_count = 1
        if p.champion and p.champion.ability_type == 'card_draw':
            draw_count = p.champion.ability_value
        
        # draw card(s) for the player at start of their turn
        if who == 'player':
            for _ in range(draw_count):
                p.draw_card()
            self.log_action(f"{p.name} draws {draw_count} card(s).")
        
        # move rest_zone -> active_zone, set ready True
        self.activate_rest_zone(p)
        
        # Apply champion passive: summon token
        if p.champion and p.champion.ability_type == 'summon_token':
            token = Card('Token 1/1', 0, 1, health=1, current_health=1, ready=False, in_play=True)
            p.active_zone.append(token)
            self.log_action(f"{p.champion.passive_name}: {p.name} summons a 1/1 Token!")
        
        # Apply champion passive: heal troops
        if p.champion and p.champion.ability_type == 'heal_troops':
            healed = 0
            for card in p.active_zone:
                if card.current_health < card.health:
                    card.current_health = min(card.health, card.current_health + p.champion.ability_value)
                    healed += 1
            if healed > 0:
                self.log_action(f"{p.champion.passive_name}: Heals {healed} troop(s)!")
        
        self.log_action(f"{p.name} start turn. {len(p.active_zone)} active cards.")
        self.on_update()

    def activate_rest_zone(self, p: Player):
        """Untap existing active cards and handle special abilities."""
        for c in p.active_zone:
            # Handle frozen cards countdown and status
            if hasattr(c, 'frozen_turns') and c.frozen_turns > 0:
                c.frozen_turns -= 1
                if c.frozen_turns > 0:
                    self.log_action(f"{c.name} is frozen ({c.frozen_turns} turns remaining)")
                    c.ready = False
                    c.attacked_count = 0
                    continue
                else:
                    self.log_action(f"{c.name} is no longer frozen!")

            # Untap and reset attack counter
            c.ready = True
            c.attacked_count = 0  # reset for Furia

            # Handle Regeneración ability (+1 up to max health)
            if c.ability and ('Regeneracion' in c.ability or 'Regeneración' in c.ability):
                old_health = c.current_health
                c.current_health = min(c.current_health + 1, c.health)
                if c.current_health > old_health:
                    self.log_action(f"{c.name} regenerates 1 health ({old_health} -> {c.current_health})")
    
    def apply_champion_passive_to_card(self, card: Card, player: Player):
        """Apply champion passive abilities to a card when played."""
        if not player.champion:
            return
        
        champion = player.champion
        
        # Brutus: +1 ATK to all troops
        if champion.ability_type == 'troop_buff_attack' and card.card_type == 'troop':
            card.damage += champion.ability_value
        
        # Shadowblade: +1 ATK and Prisa to cheap troops
        if champion.ability_type == 'cheap_troop_buff' and card.card_type == 'troop':
            if card.cost <= champion.ability_value:
                card.damage += 1
                card.ready = True  # Can attack immediately (Prisa)
        
        # Ragnar: All troops have Furia
        if champion.ability_type == 'all_furia' and card.card_type == 'troop':
            card.ability = 'Furia'
            card.ability_desc = 'Puede atacar dos veces por turno'
            card.ability_type = 'triggered'
        
        # Sylvana: Big troops get +1/+1
        if champion.ability_type == 'big_troop_buff' and card.card_type == 'troop':
            if card.health >= champion.ability_value:
                card.damage += 1
                card.health += 1
                card.current_health += 1
    
    def get_spell_cost(self, spell: Card, player: Player) -> int:
        """Get the actual cost of a spell considering champion abilities."""
        cost = spell.cost
        
        # Arcanus: Spells cost 1 less (minimum 1)
        if player.champion and player.champion.ability_type == 'spell_discount':
            cost = max(1, cost - player.champion.ability_value)
        
        return cost

    def play_card(self, card_index: int, spell_target_idx: Optional[int] = None):
        """Player plays a card from hand (troop to board or spell with effect)."""
        if self.turn != 'player':
            return
        
        if card_index < 0 or card_index >= len(self.player.hand):
            return
        card = self.player.hand[card_index]
        
        # Calculate actual cost (considering champion abilities)
        actual_cost = card.cost
        if card.card_type == 'spell':
            actual_cost = self.get_spell_cost(card, self.player)
        
        if actual_cost > self.player.mana:
            return
        
        self.player.mana -= actual_cost
        
        if card.card_type == 'spell':
            # Execute spell effect
            self.execute_spell(card, 'player', spell_target_idx)
            # Spell goes to graveyard
            del self.player.hand[card_index]
            self.player.graveyard.append(card)
            self.log_action(f"Player casts {card.name} (Cost {actual_cost}).")
            
            # Trigger Ladrón de Almas ability for opponent
            self.trigger_absorb_magic(self.ai)
        else:
            # Play troop to board
            card.in_play = True
            card.current_health = card.health if card.health > 0 else card.damage
            card.ready = False
            
            # Apply champion passive abilities to the card
            self.apply_champion_passive_to_card(card, self.player)
            
            self.player.active_zone.append(card)
            del self.player.hand[card_index]
            self.log_action(f"Player plays {card.name} to board (tapped) (Cost {card.cost}).")
            
            # Trigger on_play abilities
            if card.ability_type == 'on_play':
                if 'Curacion al Entrar' in card.ability:
                    before = self.player.life
                    self.player.life = min(self.player.life + 3, self.player.max_life)
                    self.log_action(f"{card.name} heals player for {self.player.life - before} life!")
        
        self.on_update()
    
    def play_card_ai(self, card_index: int, spell_target_idx: Optional[int] = None):
        """AI/Opponent plays a card (used by multiplayer to apply opponent's action)."""
        if card_index < 0 or card_index >= len(self.ai.hand):
            return
        card = self.ai.hand[card_index]
        
        # Calculate actual cost
        actual_cost = card.cost
        if card.card_type == 'spell':
            actual_cost = self.get_spell_cost(card, self.ai)
        
        if actual_cost > self.ai.mana:
            return
        
        self.ai.mana -= actual_cost
        
        if card.card_type == 'spell':
            self.execute_spell(card, 'ai', spell_target_idx)
            del self.ai.hand[card_index]
            self.ai.graveyard.append(card)
            self.log_action(f"Opponent casts {card.name} (Cost {actual_cost}).")
            
            # Trigger Ladrón de Almas ability for opponent
            self.trigger_absorb_magic(self.player)
        else:
            card.in_play = True
            card.current_health = card.health if card.health > 0 else card.damage
            card.ready = False
            self.apply_champion_passive_to_card(card, self.ai)
            self.ai.active_zone.append(card)
            del self.ai.hand[card_index]
            self.log_action(f"Opponent plays {card.name} to board (tapped) (Cost {card.cost}).")
            
            # Trigger on_play abilities
            if card.ability_type == 'on_play':
                if 'Curacion al Entrar' in card.ability:
                    before = self.ai.life
                    self.ai.life = min(self.ai.life + 3, self.ai.max_life)
                    self.log_action(f"{card.name} heals opponent for {self.ai.life - before} life!")
        
        self.on_update()

    def activate_ability(self, card_index: int, owner: str = 'player'):
        """Activate a card's ability by tapping it."""
        p = self.player if owner == 'player' else self.ai
        if card_index < 0 or card_index >= len(p.active_zone):
            return
        card = p.active_zone[card_index]
        if not card.ready or not card.ability or card.ability_type != 'activated':
            return
        # Execute ability effect
        if card.ability == 'Invocar Aliado':
            token = Card('Token 1/1', 0, 1, health=1, current_health=1, ready=False, in_play=True)
            p.active_zone.append(token)
            self.log_action(f"{p.name} activates {card.name}: summons a 1/1 Token!")
        # Tap the card after using ability
        card.ready = False
        self.on_update()

    def execute_spell(self, spell: Card, caster: str, target_idx = None):
        """Execute a spell's effect. target_idx can be int (troop index) or 'player' string."""
        caster_player = self.player if caster == 'player' else self.ai
        target_player = self.ai if caster == 'player' else self.player
        
        print(f"DEBUG execute_spell: name={spell.name}, spell_effect={spell.spell_effect}, spell_target={spell.spell_target}, target_idx={target_idx}")
        
        if spell.spell_effect == 'damage':
            if spell.spell_target == 'enemy_or_player':
                # Can target troops or player
                if target_idx == 'player':
                    # Damage to enemy player
                    target_player.life -= spell.damage
                    self.log_action(f"{spell.name} deals {spell.damage} damage to enemy player!")
                elif target_idx is not None and isinstance(target_idx, int) and 0 <= target_idx < len(target_player.active_zone):
                    # Damage to troop
                    target = target_player.active_zone[target_idx]
                    target.current_health -= spell.damage
                    self.log_action(f"{spell.name} deals {spell.damage} damage to enemy {target.name}!")
                    if target.current_health <= 0:
                        self.destroy_card(target_player, target_idx)
            elif spell.spell_target == 'enemy':
                # Single target damage (troops only)
                if target_idx is not None and isinstance(target_idx, int) and 0 <= target_idx < len(target_player.active_zone):
                    target = target_player.active_zone[target_idx]
                    target.current_health -= spell.damage
                    self.log_action(f"{spell.name} deals {spell.damage} damage to enemy {target.name}!")
                    if target.current_health <= 0:
                        self.destroy_card(target_player, target_idx)
            elif spell.spell_target == 'all_enemies':
                # AoE damage to all enemy troops
                damaged = []
                for card in target_player.active_zone:
                    card.current_health -= spell.damage
                    damaged.append(card.name)
                self.log_action(f"{spell.name} deals {spell.damage} damage to all enemy troops!")
                # Remove dead cards
                target_player.active_zone = [c for c in target_player.active_zone if c.current_health > 0]
        
        elif spell.spell_effect == 'heal':
            if spell.spell_target == 'friendly':
                # Single target healing
                if target_idx is not None and 0 <= target_idx < len(caster_player.active_zone):
                    target = caster_player.active_zone[target_idx]
                    target.current_health = min(target.current_health + spell.damage, target.health)
                    self.log_action(f"{spell.name} heals {target.name} for {spell.damage}!")
            elif spell.spell_target == 'self':
                # Heal caster player (cap to max life)
                before = caster_player.life
                caster_player.life = min(caster_player.life + spell.damage, caster_player.max_life)
                self.log_action(f"{spell.name} heals {caster_player.name} for {caster_player.life - before}!")
        
        elif spell.spell_effect == 'destroy':
            if spell.name == 'Aniquilar':
                # Destroy damaged enemy troop
                if target_idx is not None and 0 <= target_idx < len(target_player.active_zone):
                    target = target_player.active_zone[target_idx]
                    if target.current_health < target.health:
                        self.log_action(f"{spell.name} destroys {target.name}!")
                        self.destroy_card(target_player, target_idx)
                    else:
                        self.log_action(f"{spell.name} has no effect (target not damaged).")
            else:
                # Destierro: Destroy any enemy troop
                if target_idx is not None and 0 <= target_idx < len(target_player.active_zone):
                    target = target_player.active_zone[target_idx]
                    self.log_action(f"{spell.name} destroys {target.name}!")
                    self.destroy_card(target_player, target_idx)
        elif spell.spell_effect == 'draw':
            # Draw cards
            cards_drawn = 0
            for _ in range(spell.damage):  # Using damage field for draw count
                if len(caster_player.deck.cards) > 0:
                    drawn = caster_player.deck.draw()
                    if drawn is not None:
                        caster_player.hand.append(drawn)
                        cards_drawn += 1
            self.log_action(f"{caster_player.name} draws {cards_drawn} cards!")
        
        elif spell.spell_effect == 'freeze':
            # Prisión de Luz: Freeze enemy troop
            if target_idx is not None and 0 <= target_idx < len(target_player.active_zone):
                target = target_player.active_zone[target_idx]
                target.frozen_turns = 2
                target.ready = False  # Immediately tap
                self.log_action(f"{spell.name} freezes {target.name} for 2 turns!")
        
        elif spell.spell_effect == 'sacrifice':
            # Pacto de Sangre: Sacrifice friendly troop
            # Handle negative indices from UI (friendly targets sent as negative)
            print(f"DEBUG sacrifice: target_idx={target_idx}, active_zone size={len(caster_player.active_zone)}")
            actual_idx = target_idx
            if target_idx is not None and target_idx < 0:
                actual_idx = -(target_idx + 1)
                print(f"DEBUG sacrifice: converted negative index to actual_idx={actual_idx}")
            
            if actual_idx is not None and 0 <= actual_idx < len(caster_player.active_zone):
                target = caster_player.active_zone[actual_idx]
                print(f"DEBUG sacrifice: sacrificing {target.name}")
                self.log_action(f"{spell.name} sacrifices {target.name}!")
                self.destroy_card(caster_player, actual_idx)
                
                # Draw 2 cards
                cards_drawn = 0
                for _ in range(2):
                    if len(caster_player.deck.cards) > 0:
                        drawn = caster_player.deck.draw()
                        if drawn is not None:
                            caster_player.hand.append(drawn)
                            cards_drawn += 1
                
                # Gain +2 mana this turn
                caster_player.mana += 2
                self.log_action(f"Draws {cards_drawn} cards and gains +2 mana this turn!")

        # Clamp life values so they never go below 0 and check end after any spell resolution
        if self.player.life < 0:
            self.player.life = 0
        if self.ai.life < 0:
            self.ai.life = 0
        self.check_end()

    def destroy_card(self, player: Player, card_index: int):
        """Remove a card from active zone to graveyard."""
        if 0 <= card_index < len(player.active_zone):
            card = player.active_zone[card_index]
            card.in_play = False
            player.graveyard.append(card)
            del player.active_zone[card_index]
    
    def trigger_absorb_magic(self, player: Player):
        """Trigger Ladrón de Almas ability when opponent casts spell."""
        for card in player.active_zone:
            if card.ability and 'Absorber Magia' in card.ability:
                card.damage += 1
                card.health += 1
                card.current_health += 1
                self.log_action(f"{card.name} absorbs magic! Now {card.damage}/{card.current_health}")

    def end_turn(self):
        """End player turn."""
        if self.turn != 'player':
            return
        # Run AI turn
        self.turn = 'ai'
        self.ai_turn()

    def ai_turn(self):
        """Simple AI turn (non-animated)."""
        if not self.ai_brain:
            return  # No AI brain available
        
        self.ai.max_mana = min(10, self.ai.max_mana + 1)
        self.ai.mana = self.ai.max_mana
        self.ai.draw_card()
        self.activate_rest_zone(self.ai)
        
        # AI decides which cards to play (troops only first)
        troops_to_play = [c for c in self.ai_brain.choose_cards_to_play(self.ai.mana) if c.card_type != 'spell']
        for card in troops_to_play:
            self.ai.mana -= card.cost
            card.in_play = True
            card.current_health = card.health if card.health > 0 else card.damage
            card.ready = False
            
            # Apply champion passive abilities
            self.apply_champion_passive_to_card(card, self.ai)
            
            self.ai.active_zone.append(card)
            self.log_action(f"AI plays {card.name} to board (tapped) (Cost {card.cost}).")
            self.ai.hand.remove(card)
        
        # AI considers casting spells
        while True:
            spell_decision = self.ai_brain.choose_spell_to_cast(
                self.ai.mana, 
                self.ai.active_zone, 
                self.player.active_zone, 
                self.ai.life, 
                self.player.life
            )
            if not spell_decision:
                break
            
            spell, spell_idx, target_idx = spell_decision
            if spell_idx < len(self.ai.hand) and self.ai.hand[spell_idx] == spell:
                self.execute_spell(spell, 'ai', target_idx)
                self.ai.mana -= spell.cost
                self.ai.hand.remove(spell)
                self.ai.graveyard.append(spell)
            else:
                break
        
        # AI chooses targets and attacks
        for card in list(self.ai.active_zone):
            if not card.ready:
                continue
            
            # AI decides target
            target = self.ai_brain.choose_attack_target(card, self.player.active_zone, self.player.life)
            
            if target == 'player':
                # Attack player - can be blocked (unless player is Ragnar with 'all_furia')
                can_block = (self.player.champion is None or 
                            self.player.champion.ability_type != 'all_furia')
                
                if self.player.active_zone and callable(self.ask_blocker) and can_block:
                    choice = self.ask_blocker(card)
                    if choice is None:
                        self.player.life -= card.damage
                        self.log_action(f"AI {card.name} attacks player for {card.damage}")
                        card.ready = False
                    elif 0 <= choice < len(self.player.active_zone):
                        defender = self.player.active_zone[choice]
                        defender.blocked_this_combat = True
                        defender.current_health -= card.damage
                        card.current_health -= defender.damage
                        self.log_action(f"AI {card.name} attacks player but {defender.name} blocks: {card.damage} vs {defender.damage}")
                        if defender.current_health <= 0:
                            self.log_action(f"{defender.name} dies")
                            self.player.active_zone.remove(defender)
                            self.player.graveyard.append(defender)
                        if card.current_health <= 0:
                            self.log_action(f"{card.name} dies")
                            self.ai.active_zone.remove(card)
                            self.ai.graveyard.append(card)
                        else:
                            card.ready = False
                else:
                    self.player.life -= card.damage
                    self.log_action(f"AI {card.name} attacks player for {card.damage}")
                    card.ready = False
            
            elif isinstance(target, tuple) and target[0] == 'card':
                # Direct attack to player card
                _, target_idx = target
                if target_idx is not None and isinstance(target_idx, int) and 0 <= target_idx < len(self.player.active_zone):
                    defender = self.player.active_zone[target_idx]
                    defender.current_health -= card.damage
                    card.current_health -= defender.damage
                    self.log_action(f"AI {card.name} attacks {defender.name}: {card.damage} vs {defender.damage}")
                    if defender.current_health <= 0:
                        self.log_action(f"{defender.name} dies")
                        self.player.active_zone.remove(defender)
                        self.player.graveyard.append(defender)
                    if card.current_health <= 0:
                        self.log_action(f"{card.name} dies")
                        self.ai.active_zone.remove(card)
                        self.ai.graveyard.append(card)
                    else:
                        card.ready = False
        
        self.check_end()
        self.turn = 'player'
        self.start_turn('player')
        for c in self.player.active_zone:
            c.blocked_this_combat = False
        self.on_update()

    def ai_turn_steps(self):
        """Generator that performs the AI turn step-by-step for animations."""
        if not self.ai_brain:
            return  # No AI brain available
        
        self.ai.max_mana = min(10, self.ai.max_mana + 1)
        self.ai.mana = self.ai.max_mana
        self.ai.draw_card()
        self.log_action(f"AI draws a card.")
        yield
        
        self.activate_rest_zone(self.ai)
        self.log_action(f"AI activates rest zone -> {len(self.ai.active_zone)} active cards.")
        yield
        
        # AI decides which cards to play (troops only first)
        troops_to_play = [c for c in self.ai_brain.choose_cards_to_play(self.ai.mana) if c.card_type != 'spell']
        for card in troops_to_play:
            self.ai.mana -= card.cost
            card.in_play = True
            card.current_health = card.health if card.health > 0 else card.damage
            card.ready = False
            
            # Apply champion passive abilities
            self.apply_champion_passive_to_card(card, self.ai)
            
            try:
                self.ai_played.append(card)
            except Exception:
                pass
            self.ai.active_zone.append(card)
            self.log_action(f"AI plays {card.name} to rest zone (Cost {card.cost}).")
            self.ai.hand.remove(card)
            yield
        
        # AI considers casting spells
        while True:
            spell_decision = self.ai_brain.choose_spell_to_cast(
                self.ai.mana, 
                self.ai.active_zone, 
                self.player.active_zone, 
                self.ai.life, 
                self.player.life
            )
            if not spell_decision:
                break
            
            spell, spell_idx, target_idx = spell_decision
            if spell_idx < len(self.ai.hand) and self.ai.hand[spell_idx] == spell:
                self.execute_spell(spell, 'ai', target_idx)
                self.ai.mana -= spell.cost
                self.ai.hand.remove(spell)
                self.ai.graveyard.append(spell)
                yield
            else:
                break
        
        # AI chooses targets and attacks
        for card in list(self.ai.active_zone):
            if not card.ready:
                continue
            
            # AI decides target
            target = self.ai_brain.choose_attack_target(card, self.player.active_zone, self.player.life)
            
            if target == 'player':
                # Attack player - can be blocked (unless player is Ragnar with 'all_furia')
                can_block = (self.player.champion is None or 
                            self.player.champion.ability_type != 'all_furia')
                
                if self.player.active_zone and callable(self.ask_blocker) and can_block:
                    choice = self.ask_blocker(card)
                    if choice is None:
                        self.player.life -= card.damage
                        self.log_action(f"AI {card.name} attacks player for {card.damage}")
                        card.attacked_count += 1
                        if card.ability == 'Furia' and card.attacked_count < 2:
                            pass
                        else:
                            card.ready = False
                        yield
                    elif 0 <= choice < len(self.player.active_zone):
                        defender = self.player.active_zone[choice]
                        defender.blocked_this_combat = True
                        defender.current_health -= card.damage
                        card.current_health -= defender.damage
                        self.log_action(f"AI {card.name} attacks player but {defender.name} blocks: {card.damage} vs {defender.damage}")
                        yield
                        if defender.current_health <= 0:
                            self.log_action(f"{defender.name} dies")
                            self.player.active_zone.remove(defender)
                            self.player.graveyard.append(defender)
                            yield
                        if card.current_health <= 0:
                            self.log_action(f"{card.name} dies")
                            self.ai.active_zone.remove(card)
                            self.ai.graveyard.append(card)
                            yield
                        else:
                            card.attacked_count += 1
                            if card.ability == 'Furia' and card.attacked_count < 2:
                                pass
                            else:
                                card.ready = False
                else:
                    self.player.life -= card.damage
                    self.log_action(f"AI {card.name} attacks player for {card.damage}")
                    card.attacked_count += 1
                    if card.ability == 'Furia' and card.attacked_count < 2:
                        pass
                    else:
                        card.ready = False
                    yield
            
            elif isinstance(target, tuple) and target[0] == 'card':
                # Direct attack to player card
                _, target_idx = target
                if target_idx is not None and isinstance(target_idx, int) and 0 <= target_idx < len(self.player.active_zone):
                    defender = self.player.active_zone[target_idx]
                    defender.current_health -= card.damage
                    card.current_health -= defender.damage
                    self.log_action(f"AI {card.name} attacks {defender.name}: {card.damage} vs {defender.damage}")
                    yield
                    if defender.current_health <= 0:
                        self.log_action(f"{defender.name} dies")
                        self.player.active_zone.remove(defender)
                        self.player.graveyard.append(defender)
                        yield
                    if card.current_health <= 0:
                        self.log_action(f"{card.name} dies")
                        self.ai.active_zone.remove(card)
                        self.ai.graveyard.append(card)
                        yield
                    else:
                        card.attacked_count += 1
                        if card.ability == 'Furia' and card.attacked_count < 2:
                            pass
                        else:
                            card.ready = False
        
        for c in self.player.active_zone:
            c.blocked_this_combat = False
        yield

    def check_end(self):
        """Check if the game has ended."""
        # Don't check during initialization
        if not self.game_started:
            return
        # Clamp negatives to zero before evaluating
        if self.player.life < 0:
            self.player.life = 0
        if self.ai.life < 0:
            self.ai.life = 0

        if self.player.life == 0 or self.ai.life == 0:
            winner = 'AI' if self.player.life <= 0 else 'Player'
            messagebox.showinfo('Game Over', f'{winner} wins!')
            if self.root:
                self.root.quit()

    def log_action(self, text: str):
        """Add an action to the log."""
        self.action_log.append(text)
        if len(self.action_log) > 50:
            self.action_log.pop(0)

    def player_attack(self, attacker_idx: int, target_kind: str, target_idx: Optional[int] = None):
        """Player attacks (legacy method, not currently used)."""
        if attacker_idx < 0 or attacker_idx >= len(self.player.active_zone):
            return
        attacker = self.player.active_zone[attacker_idx]
        if not attacker.ready:
            return
        if target_kind == 'face':
            self.ai.life -= attacker.damage
            attacker.ready = False
            self.log_action(f"Player {attacker.name} attacks AI face for {attacker.damage}")
        elif target_kind == 'ai_card' and target_idx is not None and 0 <= target_idx < len(self.ai.active_zone):
            defender = self.ai.active_zone[target_idx]
            defender.current_health -= attacker.damage
            attacker.current_health -= defender.damage
            self.log_action(f"Player {attacker.name} attacks {defender.name}: {attacker.damage} vs {defender.damage}")
            if defender.current_health <= 0:
                self.log_action(f"{defender.name} dies")
                self.ai.active_zone.remove(defender)
                self.ai.graveyard.append(defender)
            if attacker.current_health <= 0:
                self.log_action(f"{attacker.name} dies")
                self.player.active_zone.remove(attacker)
                self.player.graveyard.append(attacker)
            else:
                attacker.ready = False
        self.check_end()
        self.on_update()

    def player_choose_blocker(self, attacker: Card, available_defenders: List[int]):
        """Player auto-blocking heuristic (not used in current UI)."""
        if not available_defenders:
            return None
        if attacker.damage >= self.player.life:
            survivals = [i for i in available_defenders if self.player.active_zone[i].current_health > attacker.damage and getattr(self.player.active_zone[i], 'ready', False)]
            if survivals:
                return min(survivals, key=lambda i: self.player.active_zone[i].current_health)
            candidates = [i for i in available_defenders if getattr(self.player.active_zone[i], 'ready', False)]
            if candidates:
                return max(candidates, key=lambda i: self.player.active_zone[i].damage)
            return None
        
        kill_and_survive = []
        for idx in available_defenders:
            d = self.player.active_zone[idx]
            if not getattr(d, 'ready', False):
                continue
            attacker_dies = (attacker.current_health - d.damage) <= 0
            defender_survives = (d.current_health - attacker.damage) > 0
            if attacker_dies and defender_survives:
                kill_and_survive.append((d.current_health, idx))
        if kill_and_survive:
            kill_and_survive.sort()
            return kill_and_survive[0][1]
        
        trade_candidates = []
        for idx in available_defenders:
            d = self.player.active_zone[idx]
            if not getattr(d, 'ready', False):
                continue
            attacker_dies = (attacker.current_health - d.damage) <= 0
            defender_dies = (d.current_health - attacker.damage) <= 0
            if attacker_dies and defender_dies and d.cost <= attacker.cost:
                trade_candidates.append((d.cost, idx))
        if trade_candidates:
            trade_candidates.sort()
            return trade_candidates[0][1]
        
        candidates = [i for i in available_defenders if getattr(self.player.active_zone[i], 'ready', False)]
        if not candidates:
            return None
        return max(candidates, key=lambda i: self.player.active_zone[i].damage)

    def ai_choose_blocker(self, attacker: Card, available_defenders: List[int]):
        """Delegate blocking decision to AI brain."""
        if not self.ai_brain:
            return None  # No AI brain - don't block
        return self.ai_brain.choose_blocker(attacker, available_defenders, self.ai.active_zone, self.ai.life)

    def declare_attacks_v2(self, attacker_indices: List[int], targets: List, owner: str = 'player'):
        """
        Process attacks with explicit targets.
        attacker_indices: List of attacker card indices
        targets: List of targets ('player' or ('card', target_idx))
        owner: 'player' or 'ai'
        """
        p = self.player if owner == 'player' else self.ai
        a = self.ai if owner == 'player' else self.player
        
        for i, atk_idx in enumerate(attacker_indices):
            if atk_idx < 0 or atk_idx >= len(p.active_zone):
                continue
            if i >= len(targets):
                continue
                
            attacker = p.active_zone[atk_idx]
            if not attacker.ready:
                continue
            
            # Frozen cards cannot attack
            if hasattr(attacker, 'frozen_turns') and attacker.frozen_turns > 0:
                self.log_action(f"{attacker.name} is frozen and cannot attack!")
                continue
            
            target = targets[i]
            
            if target == 'player':
                # Direct attack to opponent
                a.life -= attacker.damage
                self.log_action(f"{p.name} {attacker.name} hits {a.name} for {attacker.damage}")
                
                # Trigger Cazador de Bestias debuff when hitting champion
                if attacker.ability and 'Debilitar' in attacker.ability:
                    a.max_life = max(1, a.max_life - 1)
                    if a.life > a.max_life:
                        a.life = a.max_life
                    self.log_action(f"{attacker.name} reduces enemy max life by 1 (now {a.max_life})!")
                attacker.attacked_count += 1
                if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                    pass
                else:
                    attacker.ready = False
            
            elif isinstance(target, tuple) and target[0] == 'card':
                # Direct attack to opponent's card
                _, target_idx = target
                if target_idx < 0 or target_idx >= len(a.active_zone):
                    continue
                defender = a.active_zone[target_idx]
                
                # Combat
                defender.current_health -= attacker.damage
                attacker.current_health -= defender.damage
                self.log_action(f"{p.name} {attacker.name} attacks {defender.name}: {attacker.damage} vs {defender.damage}")
                
                if defender.current_health <= 0:
                    self.log_action(f"{defender.name} dies")
                    a.active_zone.remove(defender)
                    a.graveyard.append(defender)
                if attacker.current_health <= 0:
                    self.log_action(f"{attacker.name} dies")
                    p.active_zone.remove(attacker)
                    p.graveyard.append(attacker)
                else:
                    attacker.attacked_count += 1
                    if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                        pass
                    else:
                        attacker.ready = False
        
        self.check_end()
        self.on_update()
    
    def declare_attacks_with_blockers(self, attacker_indices: List[int], targets: List, blockers: dict, owner: str = 'player'):
        """
        Process attacks with blockers.
        attacker_indices: List of attacker card indices
        targets: List of targets ('player' or ('card', target_idx))
        blockers: {attacker_idx: blocker_idx} - which defenders block which attackers
        owner: 'player' or 'ai' (the attacker)
        """
        p = self.player if owner == 'player' else self.ai
        a = self.ai if owner == 'player' else self.player
        
        for i, atk_idx in enumerate(attacker_indices):
            if atk_idx < 0 or atk_idx >= len(p.active_zone):
                continue
            if i >= len(targets):
                continue
                
            attacker = p.active_zone[atk_idx]
            if not attacker.ready:
                continue
            
            # Frozen cards cannot attack
            if hasattr(attacker, 'frozen_turns') and attacker.frozen_turns > 0:
                self.log_action(f"{attacker.name} is frozen and cannot attack!")
                continue
            
            target = targets[i]
            
            # Check if this attacker is blocked
            if atk_idx in blockers:
                blocker_idx = blockers[atk_idx]
                if 0 <= blocker_idx < len(a.active_zone):
                    blocker = a.active_zone[blocker_idx]
                    if blocker.ready:
                        # Combat between attacker and blocker
                        blocker.current_health -= attacker.damage
                        attacker.current_health -= blocker.damage
                        self.log_action(f"{blocker.name} blocks {attacker.name}: {attacker.damage} vs {blocker.damage}")
                        
                        # Frozen blockers cannot block (treat as no block)
                        if hasattr(blocker, 'frozen_turns') and blocker.frozen_turns > 0:
                            self.log_action(f"{blocker.name} is frozen and cannot block {attacker.name}")
                            continue
                        
                        if blocker.current_health <= 0:
                            self.log_action(f"{blocker.name} dies")
                            a.active_zone.remove(blocker)
                            a.graveyard.append(blocker)
                        if attacker.current_health <= 0:
                            self.log_action(f"{attacker.name} dies")
                            p.active_zone.remove(attacker)
                            p.graveyard.append(attacker)
                        else:
                            attacker.attacked_count += 1
                            if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                                pass
                            else:
                                attacker.ready = False
                        continue
            
            # No blocker, proceed with original target
            if target == 'player':
                # Direct attack to opponent
                a.life -= attacker.damage
                self.log_action(f"{p.name} {attacker.name} hits {a.name} for {attacker.damage}")
                
                # Trigger Cazador de Bestias debuff when hitting champion
                if attacker.ability and 'Debilitar' in attacker.ability:
                    a.max_life = max(1, a.max_life - 1)
                    if a.life > a.max_life:
                        a.life = a.max_life
                    self.log_action(f"{attacker.name} reduces enemy max life by 1 (now {a.max_life})!")
                
                attacker.attacked_count += 1
                if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                    pass
                else:
                    attacker.ready = False
            
            elif isinstance(target, tuple) and target[0] == 'card':
                # Direct attack to opponent's card
                _, target_idx = target
                if target_idx < 0 or target_idx >= len(a.active_zone):
                    continue
                defender = a.active_zone[target_idx]
                
                # Combat
                defender.current_health -= attacker.damage
                attacker.current_health -= defender.damage
                self.log_action(f"{p.name} {attacker.name} attacks {defender.name}: {attacker.damage} vs {defender.damage}")
                
                if defender.current_health <= 0:
                    self.log_action(f"{defender.name} dies")
                    a.active_zone.remove(defender)
                    a.graveyard.append(defender)
                if attacker.current_health <= 0:
                    self.log_action(f"{attacker.name} dies")
                    p.active_zone.remove(attacker)
                    p.graveyard.append(attacker)
                else:
                    attacker.attacked_count += 1
                    if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                        pass
                    else:
                        attacker.ready = False
        
        self.check_end()
        self.on_update()

    def declare_attacks_with_targets(self, attack_targets: dict, owner: str = 'player'):
        """
        Process attacks with explicit targets.
        attack_targets: {attacker_idx: 'player' or ('card', target_idx)}
        """
        if owner != 'player':
            return
        p = self.player
        a = self.ai
        
        for atk_idx, target in attack_targets.items():
            if atk_idx < 0 or atk_idx >= len(p.active_zone):
                continue
            attacker = p.active_zone[atk_idx]
            if not attacker.ready:
                continue
            
            # Frozen cards cannot attack
            if hasattr(attacker, 'frozen_turns') and attacker.frozen_turns > 0:
                self.log_action(f"{attacker.name} is frozen and cannot attack!")
                continue
            
            if target == 'player':
                # Attack player - AI can choose to block (Taunt rules apply)
                # Note: AI (not player) is defending here, so Ragnar check not needed
                available = [i for i, c in enumerate(a.active_zone) if c.ready and not (hasattr(c, 'frozen_turns') and c.frozen_turns > 0)]
                taunt_defenders = [i for i in available if a.active_zone[i].ability and 'Taunt' in a.active_zone[i].ability]
                
                # Check Volar
                can_be_blocked = not (attacker.ability == 'Volar' or (attacker.ability and 'Volar' in attacker.ability))
                if attacker.ability == 'Volar' or (attacker.ability and 'Volar' in attacker.ability):
                    volar_defenders = [i for i in available if a.active_zone[i].ability == 'Volar']
                    if volar_defenders:
                        can_be_blocked = True
                        available = volar_defenders
                
                # Taunt forces block
                if taunt_defenders:
                    choice = self.ai_choose_blocker(attacker, taunt_defenders) if can_be_blocked else None
                    if choice is not None:
                        available = [choice]
                
                choice = self.ai_choose_blocker(attacker, available) if available and can_be_blocked else None
                
                if choice is None:
                    # Direct damage to AI player
                    a.life -= attacker.damage
                    self.log_action(f"Player {attacker.name} hits AI player for {attacker.damage}")
                    
                    # Trigger Cazador de Bestias debuff when hitting champion
                    if attacker.ability and 'Debilitar' in attacker.ability:
                        a.max_life = max(1, a.max_life - 1)
                        if a.life > a.max_life:
                            a.life = a.max_life
                        self.log_action(f"{attacker.name} reduces enemy max life by 1 (now {a.max_life})!")
                    
                    attacker.attacked_count += 1
                    if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                        pass
                    else:
                        attacker.ready = False
                else:
                    # Blocked
                    defender = a.active_zone[choice]
                    if choice in available:
                        available.remove(choice)
                    if choice in taunt_defenders:
                        taunt_defenders.remove(choice)
                    defender.current_health -= attacker.damage
                    attacker.current_health -= defender.damage
                    self.log_action(f"Player {attacker.name} attacks AI player but {defender.name} blocks: {attacker.damage} vs {defender.damage}")
                    
                    # Frozen defenders cannot block (should have been filtered, safeguard)
                    if hasattr(defender, 'frozen_turns') and defender.frozen_turns > 0:
                        self.log_action(f"{defender.name} is frozen and should not have blocked")
                    
                    if defender.current_health <= 0:
                        self.log_action(f"{defender.name} dies")
                        a.active_zone.remove(defender)
                        a.graveyard.append(defender)
                    if attacker.current_health <= 0:
                        self.log_action(f"{attacker.name} dies")
                        p.active_zone.remove(attacker)
                        p.graveyard.append(attacker)
                    else:
                        attacker.attacked_count += 1
                        if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                            pass
                        else:
                            attacker.ready = False
            
            elif isinstance(target, tuple) and target[0] == 'card':
                # Direct attack to AI card - no blocking
                _, target_idx = target
                if target_idx < 0 or target_idx >= len(a.active_zone):
                    continue
                defender = a.active_zone[target_idx]
                
                # Direct combat
                defender.current_health -= attacker.damage
                attacker.current_health -= defender.damage
                self.log_action(f"Player {attacker.name} attacks {defender.name}: {attacker.damage} vs {defender.damage}")
                
                if defender.current_health <= 0:
                    self.log_action(f"{defender.name} dies")
                    a.active_zone.remove(defender)
                    a.graveyard.append(defender)
                if attacker.current_health <= 0:
                    self.log_action(f"{attacker.name} dies")
                    p.active_zone.remove(attacker)
                    p.graveyard.append(attacker)
                else:
                    attacker.attacked_count += 1
                    if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                        pass
                    else:
                        attacker.ready = False
        
        self.check_end()
        self.on_update()

    def declare_attacks(self, attacker_indices: List[int], owner: str = 'player'):
        """Legacy method - Process declared attacks with blocking (attacks player by default)."""
        if owner != 'player':
            return
        p = self.player
        a = self.ai
        available = [i for i, c in enumerate(a.active_zone) if c.ready]
        taunt_defenders = [i for i in available if a.active_zone[i].ability == 'Taunt']
        
        for atk_idx in attacker_indices:
            if atk_idx < 0 or atk_idx >= len(p.active_zone):
                continue
            attacker = p.active_zone[atk_idx]
            if not attacker.ready:
                continue
            
            can_be_blocked = attacker.ability != 'Volar'
            if attacker.ability == 'Volar':
                volar_defenders = [i for i in available if a.active_zone[i].ability == 'Volar']
                if volar_defenders:
                    can_be_blocked = True
                    available = volar_defenders
            
            if taunt_defenders:
                choice = self.ai_choose_blocker(attacker, taunt_defenders) if can_be_blocked else None
                if choice is not None:
                    available = [choice]
            
            choice = self.ai_choose_blocker(attacker, available) if available and can_be_blocked else None
            
            if choice is None:
                a.life -= attacker.damage
                self.log_action(f"Player {attacker.name} hits AI for {attacker.damage}")
                attacker.attacked_count += 1
                if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                    pass
                else:
                    attacker.ready = False
            else:
                defender = a.active_zone[choice]
                if choice in available:
                    available.remove(choice)
                if choice in taunt_defenders:
                    taunt_defenders.remove(choice)
                defender.current_health -= attacker.damage
                attacker.current_health -= defender.damage
                self.log_action(f"Player {attacker.name} attacks {defender.name}: {attacker.damage} vs {defender.damage}")
                if defender.current_health <= 0:
                    self.log_action(f"{defender.name} dies")
                    a.active_zone.remove(defender)
                    a.graveyard.append(defender)
                if attacker.current_health <= 0:
                    self.log_action(f"{attacker.name} dies")
                    p.active_zone.remove(attacker)
                    p.graveyard.append(attacker)
                else:
                    attacker.attacked_count += 1
                    if attacker.ability == 'Furia' and attacker.attacked_count < 2:
                        pass
                    else:
                        attacker.ready = False
        
        self.check_end()
        self.on_update()

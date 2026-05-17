export interface CardInfo {
  id: string;
  name: string;
  cost: number;
  card_type: "minion" | "spell" | "relic";
  attack: number;
  health: number;
  keywords: string[];
  text: string;
  speed: string;
}

export interface MinionInfo {
  unit_id: string;
  name: string;
  attack: number;
  health: number;
  max_health: number;
  cost: number;
  keywords: string[];
  can_attack: boolean;
  sleeping: boolean;
  divine_shield: boolean;
  reborn: boolean;
  text: string;
}

export interface RelicInfo {
  name: string;
  text: string;
  activated_available: boolean;
}

export interface PlayerState {
  health: number;
  armor: number;
  mana: number;
  max_mana: number;
  ritual_mana: number;
  hand: CardInfo[];
  board: MinionInfo[];
  relics: RelicInfo[];
  deck_size: number;
  hero_name: string;
  hero_power_used: boolean;
  hero_power_text?: string;
  hand_size?: number;
}

export interface GameState {
  turn: number;
  phase: string;
  active_player: number;
  priority: number;
  winner: number | null;
  you: PlayerState;
  opponent: PlayerState;
  history: string[];
}

export interface ActionInfo {
  id: string;
  label: string;
  type: string;
  hand_index?: number;
  unit_id?: string;
  target?: string;
}

export interface ServerMessage {
  type: "state" | "game_over" | "error";
  state?: GameState;
  actions?: ActionInfo[];
  winner?: string;
  message?: string;
  last_action?: { player: number; action: string };
}

export interface CultureInfo {
  slug: string;
  name: string;
  hero: string;
}

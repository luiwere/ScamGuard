// Client -> Server Frames
export interface TrustedContact {
  name?: string;
  telegram_chat_id?: string;
  phone?: string;
}

export interface StartCallMessage {
  type: 'start';
  contact?: TrustedContact;
  scenario?: string | null;
}

export interface StopCallMessage {
  type: 'stop';
}

export type ClientMessage = StartCallMessage | StopCallMessage;

// Server -> Client Events
export interface TranscriptEvent {
  type: 'transcript';
  text: string;
  is_final: boolean;
  timestamp?: number;
  speaker?: string;
}

export interface TacticItem {
  name: string;
  evidence: string;
  confidence: number;
  source: 'rules' | 'llm';
}

export interface TacticsEvent {
  type: 'tactics';
  items: TacticItem[];
}

export type RiskLevel = 'safe' | 'low' | 'medium' | 'high' | 'critical';

export interface RiskBreakdown {
  hard_flags: number;
  llm_tactics: number;
  call_duration_seconds: number;
  detected_tactics: string[];
}

export interface RiskEvent {
  type: 'risk';
  score: number;
  level: RiskLevel;
  breakdown?: RiskBreakdown;
}

export interface AlertEvent {
  type: 'alert';
  advice: string;
  action: string;
  contact_notified: boolean;
  severity?: 'warning' | 'critical';
}

export interface ErrorEvent {
  type: 'error';
  message: string;
  recoverable?: boolean;
}

export type ServerEvent =
  | TranscriptEvent
  | TacticsEvent
  | RiskEvent
  | AlertEvent
  | ErrorEvent;

export interface ScenarioStep {
  delay_ms: number;
  text: string;
  is_final: boolean;
  expected_risk?: number;
  expected_tactics?: string[];
}

export interface Scenario {
  id: string;
  title: string;
  description: string;
  category: 'scam' | 'legitimate';
  steps?: ScenarioStep[];
}

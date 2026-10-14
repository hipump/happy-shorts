export interface Template {
  id: string;
  name: string;
  category: string;
  description: string;
  layout_type: string;
  badge_style: string;
  badge_prefix: string;
  subtitle_style: string;
  active_color: number[];
  normal_color: number[];
  font_name: string;
  sub_font_name?: string;
  video_box: number[];
}

export interface ScoreBreakdown {
  hook: number;
  flow: number;
  value: number;
  trend: number;
}

export interface Highlight {
  id: number;
  title: string;
  hook_text: string;
  start_time: number;
  end_time: number;
  duration: number;
  virality_score: number;
  score_breakdown: ScoreBreakdown;
  summary_points: string[];
  reason: string;
}

export interface VideoMetadata {
  title: string;
  duration: number;
  width: number;
  height: number;
  local_path: string;
  stream_url?: string;
}

export interface RecentVideo {
  filename: string;
  filepath: string;
  size_mb: number;
  modified_at: number;
  stream_url: string;
}

export interface RenderedOutput {
  filename: string;
  filepath: string;
  size_mb: number;
  modified_at: number;
  stream_url: string;
  cover_url?: string;
  seo_content?: string;
  title?: string;
  virality_score?: number;
  tags?: string[];
  duration?: number;
  aspect_ratio?: string;
  width?: number;
  height?: number;
  id?: number;
  hook_text?: string;
}

export interface SystemStatus {
  status: string;
  ollama_connected: boolean;
  available_llm_models: string[];
  active_llm_default: string;
  active_whisper_default: string;
  output_count: number;
  downloads_count: number;
}

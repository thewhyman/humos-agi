export interface VoiceAnalysisResult {
  text: string;
  mood: string;
  confidence: number;
  emotions: {
    happy: number;
    sad: number;
    angry: number;
    fearful: number;
    neutral: number;
  };
  tone: {
    pitch: number;
    rate: number;
    volume: number;
  };
}

import { Injectable, NgZone } from '@angular/core';
import { BehaviorSubject, Observable, from, of, Subject } from 'rxjs';
import { catchError, switchMap, takeUntil, filter } from 'rxjs/operators';
import * as Tone from 'tone';
import type { VoiceAnalysisResult } from '../models/voice-analysis.model';

declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

export type { VoiceAnalysisResult } from '../models/voice-analysis.model';

@Injectable({
  providedIn: 'root'
})
export class VoiceAnalysisService {
  private recognition: any;
  private isListening = false;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private audioStream: MediaStream | null = null;
  private destroy$ = new Subject<void>();
  private audioData: Float32Array[] = [];
  private scriptProcessor: ScriptProcessorNode | null = null;
  private resultSubject = new BehaviorSubject<VoiceAnalysisResult>({
    text: '',
    mood: 'neutral',
    confidence: 0,
    emotions: {
      happy: 0,
      sad: 0,
      angry: 0,
      fearful: 0,
      neutral: 1
    },
    tone: {
      pitch: 0.5,
      rate: 1.0,
      volume: 0.5
    }
  });
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor(private ngZone: NgZone) {
    this.initializeRecognition();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    this.stopListening();
  }

  private initializeRecognition(): void {
    try {
      // Check for speech recognition support
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (!SpeechRecognition) {
        throw new Error('Speech recognition not supported in this browser');
      }
      
      // Initialize speech recognition
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      
      // Set up event handlers
      this.recognition.onresult = (event: any) => {
        this.ngZone.run(() => {
          const transcript = Array.from(event.results)
            .map((result: any) => result[0])
            .map((result) => result.transcript)
            .join('');
          
          if (event.results[0].isFinal) {
            this.analyzeText(transcript);
          }
          
          const currentResult = this.resultSubject.value;
          this.resultSubject.next({
            ...currentResult,
            text: transcript
          });
        });
      };
      
      this.recognition.onerror = (event: any) => {
        this.ngZone.run(() => {
          console.error('Speech recognition error:', event.error);
          this.resultSubject.next({
            ...this.resultSubject.value,
            text: 'Error: ' + event.error
          });
          this.stopListening();
        });
      };
      
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      
      this.recognition.onresult = (event: any) => {
        const results = event.results;
        const transcript = Array.from(results)
          .map((result: any) => result[0])
          .map((result) => result.transcript)
          .join('');
          
        if (results[0].isFinal) {
          this.analyzeVoice(transcript);
        }
      };
      
      this.recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        this.resultSubject.error(event.error);
      };
      
    } catch (error) {
      console.error('Error initializing speech recognition:', error);
      throw error;
    }
  }

  startListening(): Observable<VoiceAnalysisResult> {
    if (this.isListening) {
        
        const dataArray = new Float32Array(this.analyser.frequencyBinCount);
        this.analyser.getFloatTimeDomainData(dataArray);
        this.audioData.push(dataArray);
        
        // Analyze audio in chunks (e.g., every 10 chunks)
        if (this.audioData.length >= 10) {
          this.analyzeAudioChunk();
          this.audioData = [];
        }
      };
      
      // Start speech recognition
      if (this.recognition) {
        this.recognition.start();
      }
      
      this.isListening = true;
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      this.stopListening();
      throw error;
    }
  }

  stopListening(): void {
    if (!this.isListening) return;
    
    // Stop speech recognition
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        console.warn('Error stopping recognition:', e);
      }
    }
    
    // Stop audio processing
    if (this.scriptProcessor) {
      this.scriptProcessor.disconnect();
      this.scriptProcessor.onaudioprocess = null;
      this.scriptProcessor = null;
    }
    
    // Disconnect audio nodes
    if (this.analyser) {
      this.analyser.disconnect();
    }
    
    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }
    
    // Stop all audio tracks
    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
      this.audioStream = null;
      }
    };
    
    requestAnimationFrame(analyzeTone);
  }

  private calculatePitch(frequencyData: Uint8Array): number {
    // Simple pitch detection (can be enhanced with more sophisticated algorithms)
    let maxIndex = 0;
    let maxValue = 0;
    
    for (let i = 0; i < frequencyData.length; i++) {
      if (frequencyData[i] > maxValue) {
        maxValue = frequencyData[i];
        maxIndex = i;
      }
    }
    
    // Normalize to 0-1 range (very rough approximation)
    return Math.min(1, maxIndex / frequencyData.length);
  }

  private analyzeVoice(text: string): void {
    // This is a simple emotion analysis based on keywords
    // In a real app, you would use a more sophisticated NLP model
    const emotions = {
      happy: this.detectEmotion(text, ['happy', 'joy', 'excited', 'great', 'good', 'wonderful', 'fantastic']),
      sad: this.detectEmotion(text, ['sad', 'unhappy', 'depressed', 'miserable', 'terrible', 'awful']),
      angry: this.detectEmotion(text, ['angry', 'mad', 'furious', 'annoyed', 'irritated']),
      fearful: this.detectEmotion(text, ['scared', 'afraid', 'fear', 'worried', 'anxious']),
      neutral: 0.2 // Base neutral value
    };
    
    // Normalize emotions to sum to 1
    const sum = Object.values(emotions).reduce((a, b) => a + b, 0);
    const normalizedEmotions = Object.fromEntries(
      Object.entries(emotions).map(([k, v]) => [k, v / sum])
    ) as { [key: string]: number };
    
    // Determine dominant emotion
    let dominantEmotion = 'neutral';
    let maxConfidence = 0;
    
    for (const [emotion, confidence] of Object.entries(normalizedEmotions)) {
      if (confidence > maxConfidence) {
        maxConfidence = confidence;
        dominantEmotion = emotion;
      }
    }
    
    // Create result object
    const result: VoiceAnalysisResult = {
      text,
      mood: dominantEmotion,
      confidence: maxConfidence,
      emotions: {
        happy: normalizedEmotions['happy'],
        sad: normalizedEmotions['sad'],
        angry: normalizedEmotions['angry'],
        fearful: normalizedEmotions['fearful'],
        neutral: normalizedEmotions['neutral']
      },
      tone: {
        pitch: 0.5, // Will be updated by the tone analysis
        rate: 1.0,
        volume: 0.5
      }
    };
    
    this.resultSubject.next(result);
  }
  
  private detectEmotion(text: string, keywords: string[]): number {
    const words = text.toLowerCase().split(/\s+/);
    let score = 0;
    
    for (const keyword of keywords) {
      if (words.includes(keyword.toLowerCase())) {
        score += 1;
      }
    }
    
    // Cap the score to avoid extreme values
    return Math.min(1, score * 0.3);
  }

  getResults(): Observable<VoiceAnalysisResult> {
    return this.resultSubject.asObservable();
  }
}

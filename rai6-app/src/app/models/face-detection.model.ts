export interface FaceDetectionResult {
  expressions: {
    neutral: number;
    happy: number;
    sad: number;
    angry: number;
    fearful: number;
    disgusted: number;
    surprised: number;
  };
  age?: number;
  gender?: string;
  genderProbability?: number;
  box: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

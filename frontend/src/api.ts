import type { Learner, RecordState, Subject, Concept } from './engine';

export type ApiState = {
  learners: (Learner & { id?: number })[];
  active: number;
  subject: string;
  subjects?: Subject[];
};

export type AskResponse = {
  subject_id: string;
  concept_id: string;
  response: string;
  action: string;
  hints?: string[];
  is_ai_generated?: boolean;
};

export type SubmitAnswerResponse = {
  learner_id: number;
  subject_id: string;
  concept_id: string;
  is_correct: boolean;
  correct_answer: number;
  explanation: string;
  old_mastery: number;
  new_mastery: number;
  due_at: string;
  record: RecordState;
  detected_misconception?: string;
  ai_feedback?: string;
};

export type RecommendationResponse = {
  learner_id: number;
  subject_id: string;
  recommended_concept?: Concept;
  reason: string;
  priority_level: string;
  weak_concepts: string[];
  mastered_concepts: string[];
};

export type RoadmapStep = {
  concept: Concept;
  record: RecordState;
  status: 'completed' | 'in-progress' | 'ready' | 'locked';
  prerequisites_met: boolean;
  missing_prerequisites: string[];
};

export type RoadmapResponse = {
  learner_id: number;
  subject_id: string;
  steps: RoadmapStep[];
};

export type RevisionItem = {
  concept_id: string;
  concept_title: string;
  mastery: number;
  attempts: number;
  due_at: string;
  is_due_now: boolean;
  status: string;
};

export type RevisionsResponse = {
  learner_id: number;
  subject_id: string;
  due_now: RevisionItem[];
  upcoming: RevisionItem[];
  total_due: number;
};

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers }
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { error?: string; detail?: string } | null;
    throw new Error(payload?.error ?? payload?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  // Compatibility state endpoints
  state: () => request<ApiState>('/api/state'),
  select: (active: number, subject: string) =>
    request<ApiState>('/api/selection', { method: 'PUT', body: JSON.stringify({ active, subject }) }),
  diagnostic: (active: number, subjectId: string, answers: number[]) =>
    request<ApiState>('/api/diagnostic', { method: 'POST', body: JSON.stringify({ active, subjectId, answers }) }),
  practice: (active: number, subjectId: string, conceptId: string, answer: number) =>
    request<ApiState & { correct: boolean; record: RecordState }>('/api/practice', {
      method: 'POST',
      body: JSON.stringify({ active, subjectId, conceptId, answer })
    }),

  // Universal backend REST endpoints
  getSubjects: () => request<Subject[]>('/api/subjects'),
  getSubject: (subjectId: string) => request<Subject>(`/api/subjects/${subjectId}`),
  getSubjectConcepts: (subjectId: string) => request<Concept[]>(`/api/subjects/${subjectId}/concepts`),
  createLearner: (name: string) =>
    request<Learner & { id: number }>('/api/learners', { method: 'POST', body: JSON.stringify({ name }) }),
  getLearnerProgress: (learnerId: number, subjectId?: string) =>
    request<any>(`/api/learners/${learnerId}/progress${subjectId ? `?subject_id=${subjectId}` : ''}`),
  startAssessment: (learnerId: number, subjectId: string, assessmentType = 'diagnostic') =>
    request<any>('/api/assessments/start', {
      method: 'POST',
      body: JSON.stringify({ learner_id: learnerId, subject_id: subjectId, assessment_type: assessmentType })
    }),
  submitAssessment: (assessmentId: string, answers: number[]) =>
    request<any>(`/api/assessments/${assessmentId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers })
    }),
  getRecommendations: (learnerId: number, subjectId?: string) =>
    request<RecommendationResponse>(`/api/learners/${learnerId}/recommendations${subjectId ? `?subject_id=${subjectId}` : ''}`),
  getRoadmap: (learnerId: number, subjectId?: string) =>
    request<RoadmapResponse>(`/api/learners/${learnerId}/roadmap${subjectId ? `?subject_id=${subjectId}` : ''}`),
  askTutor: (learnerId: number, subjectId: string, conceptId: string, query: string, action = 'doubt') =>
    request<AskResponse>('/api/learning/ask', {
      method: 'POST',
      body: JSON.stringify({ learner_id: learnerId, subject_id: subjectId, concept_id: conceptId, query, action })
    }),
  submitAnswer: (learnerId: number, subjectId: string, conceptId: string, answerIndex: number, reasoning?: string) =>
    request<SubmitAnswerResponse>('/api/learning/submit-answer', {
      method: 'POST',
      body: JSON.stringify({ learner_id: learnerId, subject_id: subjectId, concept_id: conceptId, answer_index: answerIndex, reasoning })
    }),
  getRevisions: (learnerId: number, subjectId?: string) =>
    request<RevisionsResponse>(`/api/learners/${learnerId}/revisions${subjectId ? `?subject_id=${subjectId}` : ''}`)
};

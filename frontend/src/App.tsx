import { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, BookOpen, Brain, Check, ChevronDown, CircleHelp, Clock3, Compass, Flame, LayoutDashboard, LockKeyhole, Menu, RotateCcw, Send, Sparkles, Target, X } from 'lucide-react';
import { subjects as defaultSubjects, recordFor, recommend, seedProfiles, type Learner, type Subject, type Concept } from './engine';
import { api, type ApiState, type RecommendationResponse } from './api';

type Page = 'home' | 'subjects' | 'diagnostic' | 'dashboard' | 'lesson' | 'roadmap' | 'revision';

export default function App() {
  const [subjectList, setSubjectList] = useState<Subject[]>(defaultSubjects);
  const [learners, setLearners] = useState<Learner[]>(seedProfiles());
  const [active, setActive] = useState(0);
  const [subjectId, setSubjectId] = useState('algebra');
  const [page, setPage] = useState<Page>('home');
  const [menu, setMenu] = useState(false);
  const [diagIndex, setDiagIndex] = useState(0);
  const [diagResults, setDiagResults] = useState<number[]>([]);
  const [picked, setPicked] = useState<number | null>(null);
  const [answered, setAnswered] = useState(false);
  const [lessonId, setLessonId] = useState('');
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(true);

  // Adaptive recommendation state
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);

  // AI Tutor state
  const [tutorQuery, setTutorQuery] = useState('');
  const [tutorReply, setTutorReply] = useState<{ title: string; text: string; isAi: boolean } | null>(null);
  const [tutorLoading, setTutorLoading] = useState(false);
  const [misconceptionNotice, setMisconceptionNotice] = useState<string | null>(null);

  const applyState = (state: ApiState) => {
    setLearners(state.learners);
    setActive(state.active);
    setSubjectId(state.subject);
  };

  const loadData = () => {
    setLoading(true);
    // Load backend state
    api.state()
      .then(state => {
        applyState(state);
        setApiError('');
      })
      .catch(e => setApiError(e instanceof Error ? e.message : 'Could not connect to the CereBro API.'))
      .finally(() => setLoading(false));

    // Load dynamic subjects from backend
    api.getSubjects()
      .then(async (subs) => {
        if (subs && subs.length > 0) {
          // Fetch full subject details for available subjects
          const detailed = await Promise.all(
            subs.map(s => api.getSubject(s.id).catch(() => null))
          );
          const valid = detailed.filter((s): s is Subject => s !== null);
          if (valid.length > 0) {
            setSubjectList(valid);
          }
        }
      })
      .catch(() => {
        // Fallback to static subjects in engine.ts
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  const learner = learners[active] ?? learners[0];
  const learnerDbId = (learner as any).id ?? (active + 1);

  // Active subject
  const subject = subjectList.find(s => s.id === subjectId) ||
                  defaultSubjects.find(s => s.id === subjectId) ||
                  subjectList[0] ||
                  defaultSubjects[0];

  const concept = subject.concepts.find(c => c.id === lessonId);

  // Fetch adaptive recommendation whenever learner or subject changes
  useEffect(() => {
    if (learnerDbId && subjectId) {
      api.getRecommendations(learnerDbId, subjectId)
        .then(rec => setRecommendation(rec))
        .catch(() => setRecommendation(null));
    }
  }, [learnerDbId, subjectId, active]);

  const goto = (p: Page) => {
    setPage(p);
    setMenu(false);
    setPicked(null);
    setAnswered(false);
    setTutorReply(null);
    setMisconceptionNotice(null);
  };

  const selectLearner = async (index: number) => {
    setActive(index);
    try {
      applyState(await api.select(index, subjectId));
      setApiError('');
    } catch (e) {
      setApiError(e instanceof Error ? e.message : 'Could not save profile selection.');
    }
  };

  const selectSubject = async (id: string) => {
    setSubjectId(id);
    try {
      applyState(await api.select(active, id));
      setApiError('');
    } catch (e) {
      setApiError(e instanceof Error ? e.message : 'Could not save subject selection.');
    }
  };

  const startDiag = () => {
    setDiagIndex(0);
    setDiagResults([]);
    goto('diagnostic');
  };

  const finishDiag = async () => {
    try {
      applyState(await api.diagnostic(active, subjectId, diagResults));
      setApiError('');
      goto('dashboard');
    } catch (e) {
      setApiError(e instanceof Error ? e.message : 'Could not save diagnostic results.');
    }
  };

  const answerDiag = () => {
    if (picked === null) return;
    setAnswered(true);
    setDiagResults(results => {
      const next = [...results];
      next[diagIndex] = picked;
      return next;
    });
  };

  const nextDiag = () => {
    setPicked(null);
    setAnswered(false);
    if (diagIndex + 1 >= subject.diagnostic.length) {
      void finishDiag();
      return;
    }
    setDiagIndex(n => n + 1);
  };

  const openLesson = (c: Concept) => {
    setLessonId(c.id);
    setPicked(null);
    setAnswered(false);
    setTutorReply(null);
    setMisconceptionNotice(null);
    goto('lesson');
  };

  const submitPractice = async () => {
    if (picked === null || !concept) return;
    try {
      // Use learning/submit-answer endpoint for misconception detection & adaptive engine
      const res = await api.submitAnswer(learnerDbId, subject.id, concept.id, picked);
      setAnswered(true);
      setApiError('');

      if (!res.is_correct) {
        const feedback = res.ai_feedback || res.detected_misconception || 'Reviewing the rule above will help clarify this concept.';
        setMisconceptionNotice(feedback);
      } else {
        setMisconceptionNotice(null);
      }

      // Refresh state to sync updated mastery scores across UI
      api.state().then(applyState).catch(() => {});
    } catch (e) {
      // Fallback to compatibility practice endpoint
      try {
        const result = await api.practice(active, subjectId, concept.id, picked);
        applyState(result);
        setAnswered(true);
        setApiError('');
      } catch (err) {
        setApiError(err instanceof Error ? err.message : 'Could not save practice result.');
      }
    }
  };

  // AI Tutor Actions
  const askTutorAction = async (action: 'explain' | 'hint' | 'doubt') => {
    if (!concept) return;
    setTutorLoading(true);
    try {
      const res = await api.askTutor(
        learnerDbId,
        subject.id,
        concept.id,
        tutorQuery,
        action
      );
      setTutorReply({
        title: action === 'explain' ? 'Concept Explanation' : action === 'hint' ? 'Helpful Hint' : 'Tutor Response',
        text: res.response,
        isAi: Boolean(res.is_ai_generated)
      });
      if (action === 'doubt') setTutorQuery('');
    } catch (err) {
      // Offline fallback
      if (action === 'explain') {
        setTutorReply({ title: 'Concept Explanation', text: `${concept.lesson} For example: ${concept.example}`, isAi: false });
      } else if (action === 'hint') {
        const h = concept.practice.hints?.[0] || `Focus on the core rule: ${concept.lesson}`;
        setTutorReply({ title: 'Helpful Hint', text: h, isAi: false });
      } else {
        setTutorReply({ title: 'Tutor Guidance', text: `Keep practicing ${concept.title}! Review the example and try again.`, isAi: false });
      }
    } finally {
      setTutorLoading(false);
    }
  };

  // Adaptive recommendations & concepts
  const nextConcept = recommendation?.recommended_concept || recommend(subject, learner);
  const nextConceptReason = recommendation?.reason || (nextConcept ? `Ready when you are. ${nextConcept.description}` : 'You’ve built strong progress. Keep it fresh with a review.');

  const mastered = subject.concepts.filter(c => recordFor(learner, c.id).mastery >= 80).length;
  const weak = subject.concepts.filter(c => recordFor(learner, c.id).attempts > 0 && recordFor(learner, c.id).mastery < 60);
  const revisionItems = subject.concepts.filter(c => recordFor(learner, c.id).dueAt && new Date(recordFor(learner, c.id).dueAt!) <= new Date());

  return (
    <div className="app-shell">
      <aside className={`sidebar ${menu ? 'show' : ''}`}>
        <div className="brand">
          <div className="brand-icon"><Brain size={20} /></div>
          <span>Adapt<span className="brand-light">IQ</span></span>
          <button className="mobile-close" onClick={() => setMenu(false)}><X size={18} /></button>
        </div>
        <div className="sidebar-label">LEARN</div>
        <nav>
          {([
            ['dashboard', 'Overview', LayoutDashboard],
            ['subjects', 'My subjects', BookOpen],
            ['roadmap', 'Learning path', Compass],
            ['revision', 'Revision', RotateCcw]
          ] as const).map(([p, l, I]) => (
            <button className={`nav-link ${page === p ? 'active' : ''}`} onClick={() => goto(p)} key={p}>
              <I size={17} />{l}
              {p === 'revision' && revisionItems.length > 0 && (
                <span className="nav-count">{revisionItems.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="side-bottom">
          <div className="streak">
            <div className="streak-icon"><Flame size={18} /></div>
            <div>
              <strong>Keep your spark</strong>
              <small>Little steps add up.</small>
            </div>
          </div>
          <div className="profile-row">
            <div className="avatar">{learner.name.split(' ').map(n => n[0]).join('')}</div>
            <div className="profile-info">
              <strong>{learner.name}</strong>
              <small>Learning profile</small>
            </div>
            <button aria-label="Switch learner" className="icon-button" onClick={() => void selectLearner((active + 1) % learners.length)}>
              <ChevronDown size={16} />
            </button>
          </div>
        </div>
      </aside>

      {menu && <button className="scrim" onClick={() => setMenu(false)} aria-label="Close navigation" />}

      <main className="main">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMenu(true)} aria-label="Open navigation"><Menu /></button>
          <div className="breadcrumb">
            My learning <span>/</span> <b>{page === 'home' ? 'Welcome' : page === 'subjects' ? 'Subjects' : page === 'diagnostic' ? 'Quick check-in' : page === 'lesson' ? 'Learning session' : page === 'roadmap' ? 'Learning path' : page === 'revision' ? 'Revision' : 'Overview'}</b>
          </div>
          <div className="top-actions">
            <div className="subject-switch">
              <span className={`mini-dot ${subject.color}`}></span>
              <select value={subjectId} onChange={e => void selectSubject(e.target.value)} aria-label="Choose current subject">
                {subjectList.map(s => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
              <ChevronDown size={14} />
            </div>
            <button className="avatar top-avatar" onClick={() => void selectLearner((active + 1) % learners.length)} title="Switch demo learner">
              {learner.name.split(' ').map(n => n[0]).join('')}
            </button>
          </div>
        </header>

        <div className="content">
          {apiError && (
            <div className="api-alert" role="alert">
              <span>{apiError}</span>
              <button onClick={() => {
                setLoading(true);
                api.state().then(applyState).then(() => setApiError('')).catch(e => setApiError(e instanceof Error ? e.message : 'API unavailable.')).finally(() => setLoading(false));
              }}>
                Reconnect
              </button>
            </div>
          )}
          {loading && <div className="connection-note">Connecting to CereBro learning backend…</div>}

          {/* HOME PAGE */}
          {page === 'home' && (
            <>
              <section className="hero">
                <div className="hero-copy">
                  <div className="eyebrow"><Sparkles size={14} /> A learning space that adapts to you</div>
                  <h1>Make progress<br />that <span>feels like yours.</span></h1>
                  <p>CereBro meets you where you are, finds what to practise next, and helps every small win add up.</p>
                  <button className="primary-button" onClick={() => goto('subjects')}>
                    Start learning <ArrowRight size={17} />
                  </button>
                  <div className="hero-proof">
                    <div className="tiny-avatars"><i>A</i><i>S</i><i>+</i></div>
                    <span>Two demo learners ready to explore</span>
                  </div>
                </div>
                <div className="hero-art">
                  <div className="orbit orbit-one"></div>
                  <div className="orbit orbit-two"></div>
                  <div className="art-glow"></div>
                  <div className="brain-emoji">🧠</div>
                  <div className="float-card float-one">
                    <span className="float-check"><Check size={13} /></span>
                    <span><b>Progress, your pace</b><small>One step at a time</small></span>
                  </div>
                  <div className="float-card float-two">
                    <span className="float-spark">✦</span>
                    <span><b>Next up</b><small>{nextConcept?.title ?? subject.concepts[0].title}</small></span>
                  </div>
                  <span className="art-star star-one">✳</span>
                  <span className="art-star star-two">✦</span>
                  <span className="art-dot dot-one"></span>
                  <span className="art-dot dot-two"></span>
                </div>
              </section>

              <section className="quick-start">
                <div className="section-heading">
                  <div>
                    <span className="eyebrow plain">YOUR LEARNING SPACE</span>
                    <h2>A good place to begin</h2>
                  </div>
                  <button className="text-button" onClick={() => goto('subjects')}>
                    Explore subjects <ArrowRight size={15} />
                  </button>
                </div>
                <div className="subject-grid">
                  {subjectList.map(s => (
                    <SubjectCard key={s.id} subject={s} onClick={() => { void selectSubject(s.id); goto('subjects'); }} />
                  ))}
                </div>
              </section>
            </>
          )}

          {/* SUBJECTS PAGE */}
          {page === 'subjects' && (
            <>
              <PageIntro
                eyebrow="CHOOSE YOUR DIRECTION"
                title="What would you like to learn?"
                description="Pick a subject to see your learning path and get a quick sense of what you already know."
              />
              <div className="subject-grid large">
                {subjectList.map(s => (
                  <SubjectCard key={s.id} subject={s} selected={s.id === subjectId} onClick={() => void selectSubject(s.id)} />
                ))}
              </div>
              <div className="selection-bar">
                <div>
                  <strong>{subject.name}</strong>
                  <span>{subject.domain} · {subject.concepts.length} learning concepts</span>
                </div>
                <button className="primary-button" onClick={startDiag}>
                  Take a quick check-in <ArrowRight size={16} />
                </button>
              </div>
            </>
          )}

          {/* DIAGNOSTIC CHECK-IN */}
          {page === 'diagnostic' && (
            <div className="quiz-wrap">
              <button className="back-link" onClick={() => goto('subjects')}>
                <ArrowLeft size={15} /> All subjects
              </button>
              <div className="quiz-card">
                <div className="quiz-top">
                  <div className={`subject-symbol ${subject.color}`}>{subject.icon}</div>
                  <span className="pill">{subject.name}</span>
                  <span className="quiz-count">{diagIndex + 1} <span>of {subject.diagnostic.length}</span></span>
                </div>
                <div className="progress-track">
                  <div style={{ width: `${((diagIndex + 1) / subject.diagnostic.length) * 100}%` }} />
                </div>
                <div className="quiz-label">QUICK CHECK-IN</div>
                <h2>{subject.diagnostic[diagIndex].prompt}</h2>
                <div className="answers">
                  {subject.diagnostic[diagIndex].choices.map((ans, i) => (
                    <button
                      key={ans}
                      disabled={answered}
                      className={`answer-option ${picked === i ? 'chosen' : ''} ${answered && i === subject.diagnostic[diagIndex].answer ? 'right' : ''} ${answered && picked === i && picked !== subject.diagnostic[diagIndex].answer ? 'wrong' : ''}`}
                      onClick={() => setPicked(i)}
                    >
                      <span className="answer-letter">{String.fromCharCode(65 + i)}</span>
                      {ans}
                      {answered && i === subject.diagnostic[diagIndex].answer && <Check size={17} />}
                    </button>
                  ))}
                </div>
                {answered && (
                  <div className={`feedback ${picked === subject.diagnostic[diagIndex].answer ? 'good' : 'try-again'}`}>
                    <b>{picked === subject.diagnostic[diagIndex].answer ? 'That’s right!' : 'Good try — here’s why'}</b>
                    <span>{subject.diagnostic[diagIndex].explanation}</span>
                  </div>
                )}
                <button className="primary-button full" disabled={picked === null} onClick={answered ? nextDiag : answerDiag}>
                  {answered ? (diagIndex === subject.diagnostic.length - 1 ? 'See my learning path' : 'Next question') : 'Check answer'} <ArrowRight size={16} />
                </button>
                <p className="quiz-foot"><LockKeyhole size={12} /> Adaptive learner profile stored securely in local database</p>
              </div>
            </div>
          )}

          {/* DASHBOARD PAGE */}
          {page === 'dashboard' && (
            <>
              <div className="dashboard-welcome">
                <div>
                  <div className="eyebrow plain">YOUR LEARNING OVERVIEW</div>
                  <h1>Good to see you, {learner.name.split(' ')[0]} <span className="wave">✳</span></h1>
                  <p>Small, steady steps make a real difference. Let’s find yours.</p>
                </div>
                <button className="soft-button" onClick={startDiag}>
                  <Target size={16} /> Refresh check-in
                </button>
              </div>

              <div className="stat-grid">
                <Stat icon={<BookOpen />} label="Learning concepts" value={`${mastered} / ${subject.concepts.length}`} caption="mastered" color="violet" />
                <Stat icon={<Target />} label="Overall mastery" value={`${Math.round(subject.concepts.reduce((n, c) => n + recordFor(learner, c.id).mastery, 0) / subject.concepts.length)}%`} caption="across this subject" color="mint" />
                <Stat icon={<Clock3 />} label="Practice sessions" value={`${Object.values(learner.records).reduce((n, r) => n + r.attempts, 0)}`} caption="questions answered" color="peach" />
              </div>

              <div className="dash-columns">
                <div className="panel concepts-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Your concepts</h3>
                      <p>Mastery grows with practice over time</p>
                    </div>
                    <button className="text-button" onClick={() => goto('roadmap')}>
                      View path <ArrowRight size={14} />
                    </button>
                  </div>
                  {subject.concepts.map(c => (
                    <ConceptRow key={c.id} concept={c} learner={learner} onClick={() => openLesson(c)} />
                  ))}
                </div>

                <div className="right-stack">
                  {/* Adaptive Recommendation Card */}
                  <div className="recommend-card">
                    <div className="recommend-top">
                      <span className="recommend-icon"><Sparkles size={18} /></span>
                      <span className="pill green-pill">FOR YOU</span>
                    </div>
                    <div className="eyebrow plain">YOUR NEXT STEP</div>
                    <h3>{nextConcept?.title ?? 'A little review goes a long way'}</h3>
                    <p>{nextConceptReason}</p>
                    <button className="primary-button compact" onClick={() => nextConcept ? openLesson(nextConcept) : goto('revision')}>
                      {nextConcept ? 'Continue learning' : 'Review concepts'} <ArrowRight size={15} />
                    </button>
                  </div>

                  {/* Weak concepts */}
                  <div className="panel focus-panel">
                    <div className="panel-heading">
                      <div>
                        <h3>Worth another look</h3>
                        <p>Concepts to strengthen next</p>
                      </div>
                      <CircleHelp size={17} className="muted-icon" />
                    </div>
                    {weak.length ? (
                      weak.slice(0, 3).map(c => (
                        <button className="focus-item" key={c.id} onClick={() => openLesson(c)}>
                          <span className={`focus-mark ${subject.color}`}></span>
                          <span>{c.title}</span>
                          <span className="focus-score">{recordFor(learner, c.id).mastery}%</span>
                        </button>
                      ))
                    ) : (
                      <div className="empty-note"><Check size={15} /> No weak spots yet. Keep practising!</div>
                    )}
                  </div>

                  {/* Activity panel */}
                  <div className="panel activity-panel">
                    <div className="panel-heading">
                      <h3>Recent activity</h3>
                      <Clock3 size={16} className="muted-icon" />
                    </div>
                    {learner.activity && learner.activity.length ? (
                      learner.activity.slice(0, 3).map((a, i) => (
                        <div className="activity-item" key={`${a}${i}`}>
                          <span className="activity-dot"></span>
                          <span>{a}</span>
                        </div>
                      ))
                    ) : (
                      <div className="empty-note">Your practice activity will show up here.</div>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}

          {/* LESSON & PRACTICE PAGE */}
          {page === 'lesson' && concept && (
            <>
              <button className="back-link" onClick={() => goto('roadmap')}>
                <ArrowLeft size={15} /> Back to learning path
              </button>
              <div className="lesson-layout">
                <div>
                  <div className="lesson-head">
                    <span className={`subject-symbol ${subject.color}`}>{subject.icon}</span>
                    <span className="pill">{concept.level}</span>
                    <div className="eyebrow plain">{subject.name.toUpperCase()}</div>
                    <h1>{concept.title}</h1>
                    <p>{concept.description}</p>
                  </div>

                  {/* Lesson Concept Panel */}
                  <div className="panel lesson-panel">
                    <div className="lesson-section-label">
                      <BookOpen size={16} /> THE IDEA
                    </div>
                    <p className="lesson-copy">{concept.lesson}</p>
                    <div className="example-box">
                      <span>EXAMPLE</span>
                      <p>{concept.example}</p>
                    </div>

                    {/* Integrated AI Teaching Assistant */}
                    <div className="ai-tutor-panel">
                      <div className="ai-tutor-header">
                        <span className="ai-tutor-badge">
                          <Brain size={13} /> AI Tutor (CereBro)
                        </span>
                        <small style={{ color: '#999dac', fontSize: '9px' }}>Adapts to your level</small>
                      </div>

                      <div className="tutor-quick-actions">
                        <button
                          className="soft-button"
                          disabled={tutorLoading}
                          onClick={() => askTutorAction('explain')}
                        >
                          💡 Explain simply
                        </button>
                        <button
                          className="soft-button"
                          disabled={tutorLoading}
                          onClick={() => askTutorAction('hint')}
                        >
                          🔍 Need a hint
                        </button>
                      </div>

                      {tutorLoading && (
                        <div className="connection-note">Thinking with pedagogical context…</div>
                      )}

                      {tutorReply && (
                        <div className="tutor-bubble">
                          <b>{tutorReply.title} {tutorReply.isAi && '✦ AI'}</b>
                          {tutorReply.text}
                        </div>
                      )}

                      <div className="tutor-input-row">
                        <input
                          type="text"
                          className="tutor-input"
                          placeholder="Ask the AI Tutor any doubt about this concept..."
                          value={tutorQuery}
                          onChange={e => setTutorQuery(e.target.value)}
                          onKeyDown={e => { if (e.key === 'Enter' && tutorQuery.trim()) askTutorAction('doubt'); }}
                        />
                        <button
                          className="primary-button compact"
                          disabled={!tutorQuery.trim() || tutorLoading}
                          onClick={() => askTutorAction('doubt')}
                        >
                          <Send size={13} /> Ask
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Practice Panel */}
                  <div className="panel practice-panel">
                    <div className="lesson-section-label">
                      <Target size={16} /> YOUR TURN <span className="practice-tag">Practice</span>
                    </div>
                    <h3>{concept.practice.prompt}</h3>
                    <div className="answers practice-answers">
                      {concept.practice.choices.map((ans, i) => (
                        <button
                          key={ans}
                          disabled={answered}
                          className={`answer-option ${picked === i ? 'chosen' : ''} ${answered && i === concept.practice.answer ? 'right' : ''} ${answered && picked === i && picked !== concept.practice.answer ? 'wrong' : ''}`}
                          onClick={() => setPicked(i)}
                        >
                          <span className="answer-letter">{String.fromCharCode(65 + i)}</span>
                          {ans}
                          {answered && i === concept.practice.answer && <Check size={17} />}
                        </button>
                      ))}
                    </div>

                    {answered && (
                      <div className={`feedback ${picked === concept.practice.answer ? 'good' : 'try-again'}`}>
                        <b>{picked === concept.practice.answer ? 'Exactly right!' : 'Let’s learn from that'}</b>
                        <span>{concept.practice.explanation}</span>
                        {misconceptionNotice && (
                          <div className="misconception-box">
                            <b>💡 Misconception analysis:</b> {misconceptionNotice}
                          </div>
                        )}
                        <span className="mastery-change">
                          Mastery is now {recordFor(learner, concept.id).mastery}% · {picked === concept.practice.answer ? 'Review in 3 days' : 'Review tomorrow'}
                        </span>
                      </div>
                    )}

                    <button
                      className="primary-button"
                      disabled={picked === null}
                      onClick={answered ? () => goto('dashboard') : submitPractice}
                    >
                      {answered ? 'Back to overview' : 'Check answer'} <ArrowRight size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* ROADMAP PAGE */}
          {page === 'roadmap' && (
            <>
              <PageIntro
                eyebrow="YOUR LEARNING PATH"
                title={`${subject.name}, one step at a time`}
                description="Concepts unlock as you build the foundations. Your mastery sets the pace."
              />
              <div className="roadmap-card">
                {subject.concepts.map((c, i) => {
                  const r = recordFor(learner, c.id);
                  const ready = c.prerequisites.every(p => recordFor(learner, p).mastery >= 60);
                  const status = r.mastery >= 80 ? 'completed' : r.attempts ? 'in-progress' : ready ? 'ready' : 'locked';
                  return (
                    <div className="roadmap-step" key={c.id}>
                      <div className="roadmap-rail">
                        <div className={`roadmap-node ${status}`}>
                          {status === 'completed' ? <Check size={15} /> : status === 'locked' ? <LockKeyhole size={14} /> : <span>{String(i + 1).padStart(2, '0')}</span>}
                        </div>
                        {i < subject.concepts.length - 1 && (
                          <div className={`rail-line ${status === 'completed' ? 'filled' : ''}`} />
                        )}
                      </div>
                      <div className={`roadmap-concept ${status === 'locked' ? 'locked' : ''}`}>
                        <div className="roadmap-meta">
                          <span className={`status-pill ${status}`}>
                            {status === 'completed' ? 'Completed' : status === 'in-progress' ? 'In progress' : status === 'locked' ? 'Not yet ready' : 'Ready to start'}
                          </span>
                          <span className="concept-level">{c.level}</span>
                        </div>
                        <h3>{c.title}</h3>
                        <p>{c.description}</p>
                        <div className="roadmap-bottom">
                          <div className="mastery-line">
                            <div><span>Mastery</span><b>{r.mastery}%</b></div>
                            <Progress value={r.mastery} color={subject.color} />
                          </div>
                          <button className="soft-button small" disabled={!ready} onClick={() => openLesson(c)}>
                            {r.attempts ? 'Keep practising' : 'Start concept'} <ArrowRight size={14} />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="roadmap-note">
                <LockKeyhole size={13} /> Unlock the next step by reaching 60% mastery on its prerequisites.
              </p>
            </>
          )}

          {/* REVISION PAGE */}
          {page === 'revision' && (
            <>
              <PageIntro
                eyebrow="A MOMENT TO REVISIT"
                title="Keep the good stuff fresh"
                description="Your practice results schedule reviews dynamically: missed concepts return tomorrow, while mastered concepts return with spaced intervals."
              />
              <div className="revision-card">
                {subject.concepts.filter(c => recordFor(learner, c.id).dueAt).length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon"><RotateCcw /></div>
                    <h3>Your review list is ready for practice</h3>
                    <p>Try a concept in a learning session, and it’ll appear here when it’s time to revisit.</p>
                    <button className="primary-button" onClick={() => goto('roadmap')}>
                      Explore your learning path <ArrowRight size={15} />
                    </button>
                  </div>
                ) : (
                  <>
                    {revisionItems.length > 0 && (
                      <div className="revision-section">
                        <h3>Due now <span>{revisionItems.length}</span></h3>
                        {revisionItems.map(c => (
                          <RevisionRow key={c.id} c={c} r={recordFor(learner, c.id)} onClick={() => openLesson(c)} />
                        ))}
                      </div>
                    )}
                    <div className="revision-section">
                      <h3>Coming up</h3>
                      {subject.concepts.filter(c => recordFor(learner, c.id).dueAt && new Date(recordFor(learner, c.id).dueAt!) > new Date()).map(c => (
                        <RevisionRow key={c.id} c={c} r={recordFor(learner, c.id)} onClick={() => openLesson(c)} />
                      ))}
                    </div>
                  </>
                )}
              </div>
            </>
          )}
        </div>

        <footer className="footer">
          <span>© 2026 CereBro Universal Adaptive Tutor</span>
          <span>Curiosity, at your pace.</span>
        </footer>
      </main>
    </div>
  );
}

function PageIntro({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <div className="page-intro">
      <div className="eyebrow plain">{eyebrow}</div>
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  );
}

function SubjectCard({ subject: s, selected, onClick }: { subject: Subject; selected?: boolean; onClick: () => void }) {
  return (
    <button className={`subject-card ${selected ? 'selected' : ''}`} onClick={onClick}>
      <div className="subject-card-top">
        <span className={`subject-symbol ${s.color}`}>{s.icon}</span>
        <span className="level-chip">{s.level}</span>
      </div>
      <span className="subject-domain">{s.domain}</span>
      <h3>{s.name}</h3>
      <p>{s.description}</p>
      <div className="card-bottom">
        <span>{s.concepts.length} concepts</span>
        <span className="card-arrow"><ArrowRight size={16} /></span>
      </div>
    </button>
  );
}

function Progress({ value, color }: { value: number; color: string }) {
  return (
    <div className="progress-bar">
      <i className={color} style={{ width: `${value}%` }} />
    </div>
  );
}

function ConceptRow({ concept: c, learner: l, onClick }: { concept: Concept; learner: Learner; onClick: () => void }) {
  const r = recordFor(l, c.id);
  return (
    <button className="concept-row" onClick={onClick}>
      <span className="concept-mark">{r.mastery >= 80 ? <Check size={14} /> : <span />}</span>
      <span className="concept-name">
        <b>{c.title}</b>
        <small>{r.attempts ? `${r.attempts} practice ${r.attempts === 1 ? 'question' : 'questions'}` : 'Not started'}</small>
      </span>
      <span className="row-progress">
        <b>{r.mastery}%</b>
        <Progress value={r.mastery} color="violet" />
      </span>
      <ArrowRight size={15} className="row-arrow" />
    </button>
  );
}

function Stat({ icon, label, value, caption, color }: { icon: React.ReactNode; label: string; value: string; caption: string; color: string }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${color}`}>{icon}</div>
      <div>
        <span className="stat-label">{label}</span>
        <strong>{value}</strong>
        <small>{caption}</small>
      </div>
    </div>
  );
}

function RevisionRow({ c, r, onClick }: { c: Concept; r: ReturnType<typeof recordFor>; onClick: () => void }) {
  return (
    <div className="revision-row">
      <span className="revision-check"><RotateCcw size={17} /></span>
      <span className="revision-name">
        <b>{c.title}</b>
        <small>{r.mastery}% mastery · {r.attempts} attempts</small>
      </span>
      <span className="due-date">
        {r.dueAt && new Date(r.dueAt) <= new Date() ? 'Ready to review' : new Date(r.dueAt!).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
      </span>
      <button className="soft-button small" onClick={onClick}>
        Review now <ArrowRight size={14} />
      </button>
    </div>
  );
}

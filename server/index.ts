import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { subjects, emptyLearner, recordFor, updateMastery, type Learner } from '../src/engine';
import { loadStore, saveStore, type Store } from './store';

const app = express();
const port = Number(process.env.PORT ?? 3001);
const root = path.dirname(fileURLToPath(import.meta.url));
const storePath = path.resolve(root, '../data/cerebro.json');
app.use(express.json({ limit: '32kb' }));

function validLearner(index: unknown, store: Store): index is number {
  return Number.isInteger(index) && Number(index) >= 0 && Number(index) < store.learners.length;
}
function validSubject(id: unknown): id is string { return typeof id === 'string' && subjects.some(subject => subject.id === id); }
function publicState(store: Store) { return { learners: store.learners, active: store.active, subject: store.subject }; }

app.get('/api/health', (_req, res) => res.json({ ok: true, name: 'CereBro API' }));
app.get('/api/state', async (_req, res, next) => {
  try { res.json(publicState(await loadStore(storePath))); } catch (error) { next(error); }
});

app.put('/api/selection', async (req, res, next) => {
  try {
    const store = await loadStore(storePath);
    const { active, subject } = req.body as { active?: unknown; subject?: unknown };
    if (!validLearner(active, store) || !validSubject(subject)) return res.status(400).json({ error: 'Choose a valid learner and subject.' });
    store.active = active; store.subject = subject;
    await saveStore(storePath, store);
    res.json(publicState(store));
  } catch (error) { next(error); }
});

app.post('/api/diagnostic', async (req, res, next) => {
  try {
    const store = await loadStore(storePath);
    const { active, subjectId, answers } = req.body as { active?: unknown; subjectId?: unknown; answers?: unknown };
    if (!validLearner(active, store) || !validSubject(subjectId)) return res.status(400).json({ error: 'Choose a valid learner and subject.' });
    const subject = subjects.find(item => item.id === subjectId)!;
    if (!Array.isArray(answers) || answers.length !== subject.diagnostic.length || answers.some(answer => !Number.isInteger(answer) || answer < 0 || answer > 4)) return res.status(400).json({ error: 'Diagnostic answers are incomplete or invalid.' });
    const learner = store.learners[active];
    subject.diagnostic.forEach((item, i) => {
      learner.records[item.conceptId] = updateMastery(recordFor(learner, item.conceptId), answers[i] === item.answer);
    });
    learner.activity = [`Completed ${subject.name} check-in`, ...learner.activity].slice(0, 6);
    store.active = active; store.subject = subjectId;
    await saveStore(storePath, store);
    res.json(publicState(store));
  } catch (error) { next(error); }
});

app.post('/api/practice', async (req, res, next) => {
  try {
    const store = await loadStore(storePath);
    const { active, subjectId, conceptId, answer } = req.body as { active?: unknown; subjectId?: unknown; conceptId?: unknown; answer?: unknown };
    if (!validLearner(active, store) || !validSubject(subjectId) || typeof conceptId !== 'string' || !Number.isInteger(answer)) return res.status(400).json({ error: 'Practice answer is invalid.' });
    const subject = subjects.find(item => item.id === subjectId)!;
    const concept = subject.concepts.find(item => item.id === conceptId);
    if (!concept || Number(answer) < 0 || Number(answer) >= concept.practice.choices.length) return res.status(400).json({ error: 'That practice question does not exist.' });
    const learner = store.learners[active];
    const correct = answer === concept.practice.answer;
    learner.records[concept.id] = updateMastery(recordFor(learner, concept.id), correct);
    learner.activity = [`${correct ? 'Practised' : 'Reviewed'} ${concept.title}`, ...learner.activity].slice(0, 6);
    store.active = active; store.subject = subjectId;
    await saveStore(storePath, store);
    res.json({ ...publicState(store), correct, record: learner.records[concept.id] });
  } catch (error) { next(error); }
});

app.use((error: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error(error);
  res.status(500).json({ error: 'CereBro could not save that change. Please try again.' });
});

app.listen(port, () => console.log(`CereBro API listening at http://localhost:${port}`));

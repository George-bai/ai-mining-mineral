// One attempt through DeepSeek Harness (dsh): starts `dsh --profile sdk`, sends the drawing and the prompt as one user
// message (the image first, then the text, as dsh's own clients send them), waits until the agent is done, shuts dsh down.
// Every message dsh sends goes to stdout as one JSON line (the record of the run); the driver's own steps are logged as
// {"driver": ...} lines. dsh's headless mode takes text only; its SDK mode is how a script attaches an image.
// Usage (in the attempt folder): node driver.mjs <model> <prompt file> <image> <session id> [skill name]
//   With a skill, the prompt starts with "/<skill name> ", dsh's own way to invoke a skill (Pi: /skill:<name>).
// Node standard library only.
import { spawn } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { createInterface } from 'node:readline'

const [model, promptFile, image, sessionId, skill] = process.argv.slice(2)
const prompt = readFileSync(promptFile, 'utf8').trim()
const text = skill ? `/${skill} ${prompt}` : prompt
const log = (o) => process.stdout.write(JSON.stringify({ driver: o.step, t: Date.now() / 1000, ...o }) + '\n')

const dsh = spawn('node', ['/opt/dsh/lib/bin.js', '--profile', 'sdk', '--patch', '/opt/data/patch.yml'],
  { stdio: ['pipe', 'pipe', 'inherit'] })
const pending = new Map()
let next = 1, running, stopped, exited = false
const sawRunning = new Promise((resolve, reject) => { running = resolve; stopped = reject })
sawRunning.catch(() => {})                                       // handled where it is awaited
dsh.stdin.on('error', () => {})                                  // dsh gone: the exit handler reports it
const call = (method, params) => new Promise((resolve, reject) => {
  if (exited) return reject(new Error('dsh has exited'))
  const id = next++
  pending.set(id, { resolve, reject })
  dsh.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n')
})

createInterface({ input: dsh.stdout }).on('line', (line) => {
  let m
  try { m = JSON.parse(line) } catch { return }
  if (m.id !== undefined && m.method === undefined) {          // a reply to one of ours
    const p = pending.get(m.id); pending.delete(m.id)
    if (p) (m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result))
    return
  }
  process.stdout.write(line + '\n')                              // a notification or a request from dsh: the record
  if (m.id !== undefined) {                                       // no answerer here: approvals are off ("never")
    dsh.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: m.id, error: { code: -32601, message: 'no client answerer' } }) + '\n')
  }
  if (m.method === 'session.status' && m.params?.sessionId === sessionId && m.params.status === 'running') running()
})
dsh.on('exit', (code, signal) => {
  exited = true
  stopped(new Error(`dsh exited (${code ?? signal}) before the agent ran`))
  for (const p of pending.values()) p.reject(new Error(`dsh exited (${code ?? signal})`))
  log({ step: 'dsh exited', code, signal })
  process.exitCode = code ?? 1
})

try {
  log({ step: 'initialize', model })
  await call('initialize', { cwd: process.cwd(), provider: 'fence', model, maxTokens: 32768 })
  log({ step: 'prompt', text, image })
  await call('session/prompt', { sessionId, contentBlocks: [
    { type: 'image', data: readFileSync(image).toString('base64'), mimeType: 'image/png', name: image },
    { type: 'text', text },
  ] })
  await sawRunning
  await call('session/wait', { sessionId })
  log({ step: 'done' })
} catch (e) {
  log({ step: 'error', error: String(e?.message ?? e) })
}
await call('shutdown').catch(() => {})

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');

async function main() {
const root = path.resolve(__dirname, '..');
const htmlPath = path.join(root, 'index.html');
assert.ok(fs.existsSync(htmlPath), 'Electron entrypoint index.html must exist');
const html = fs.readFileSync(htmlPath, 'utf8');
assert.match(html, /<title>SS1 Department Placement Test System/);
assert.match(html, /const PASSWORD_HASH_ITERATIONS = 310000/);
assert.match(html, /name: 'PBKDF2'/);
assert.match(html, /passwordIterations/);
assert.doesNotMatch(html, /passwordPlain\s*=/, 'plain passwords must not be persisted');
assert.doesNotMatch(html, /s\.passwordPlain/, 'student CSV export must not read plaintext passwords');
assert.match(html, /deadline: new Date\(Date\.now\(\) \+ exam\.durationMinutes \* 60 \* 1000\)/);
assert.match(html, /function startExamTimer\(\)/);
assert.match(html, /autoSubmitExam\(true\)/);

const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1].trim())
  .filter(Boolean);
assert.ok(scripts.length > 0, 'HTML must include application JavaScript');
for (const [index, source] of scripts.entries()) {
  const check = spawnSync(process.execPath, ['--check'], {
    input: source,
    encoding: 'utf8'
  });
  assert.equal(check.status, 0, `inline script ${index + 1} must parse: ${check.stderr}`);
}

const hashCode = html.split('// -------------------- Password Hashing (Web Crypto) --------------------')[1]
  ?.split('// -------------------- IndexedDB Layer --------------------')[0];
assert.ok(hashCode, 'password hashing implementation must be present');
const hashContext = vm.createContext({
  crypto: webcrypto,
  TextEncoder,
  Uint8Array,
  atob,
  btoa
});
vm.runInContext(hashCode, hashContext);
const hashChecks = await vm.runInContext(`(async () => {
  const current = await hashPassword('correct horse battery staple');
  const currentValid = await verifyPassword('correct horse battery staple', current.hash, current.salt, current.iterations);
  const currentInvalid = await verifyPassword('wrong password', current.hash, current.salt, current.iterations);
  const legacy = await hashPassword('legacy-password', undefined, 100000);
  const legacyValid = await verifyPassword('legacy-password', legacy.hash, legacy.salt);
  return { currentIterations: current.iterations, currentValid, currentInvalid, legacyValid };
})()`, hashContext);
assert.deepEqual({ ...hashChecks }, {
  currentIterations: 310000,
  currentValid: true,
  currentInvalid: false,
  legacyValid: true
});

const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
assert.equal(pkg.main, 'main.js');
assert.ok(pkg.build.files.includes('index.html'), 'Electron package must include index.html');
assert.match(fs.readFileSync(path.join(root, 'main.js'), 'utf8'), /loadFile\(path\.join\(__dirname, 'index\.html'\)\)/);
console.log(`Checks passed: entrypoint, ${scripts.length} inline script(s), PBKDF2 current/legacy verification, password storage, exam timer, and Electron packaging.`);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

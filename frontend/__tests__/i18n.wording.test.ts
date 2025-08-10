import fs from 'node:fs';
import path from 'node:path';

const enDir = path.join(process.cwd(), 'locales', 'en');
const esDir = path.join(process.cwd(), 'locales', 'es');

const allowEvidenceEN = new Set(['learn-cbt.json']);
const allowEvidenceES = new Set(['learn-cbt.json']);

function scan(dir: string, allow: Set<string>) {
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.json'))) {
    const txt = fs.readFileSync(path.join(dir, f), 'utf8');
    if (!allow.has(f)) {
      // English
      expect(txt).not.toMatch(/\bevidence-based\b/i);
      expect(txt).not.toMatch(/\bevidence[-\s]?informed\b/i);
      // Spanish
      expect(txt).not.toMatch(/basad[ao]s?\s+en\s+evidencia/i);
    }
  }
}

test('no clinical claims outside educational pages', () => {
  scan(enDir, allowEvidenceEN);
  scan(esDir, allowEvidenceES);
});
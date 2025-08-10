import fs from 'node:fs';
import path from 'node:path';

function loadJSON(p: string) { return JSON.parse(fs.readFileSync(p, 'utf8')); }
function flatten(obj: Record<string, unknown>, prefix = ''): Record<string, true> {
  return Object.entries(obj).reduce<Record<string, true>>((acc, [k, v]) => {
    const key = prefix ? (prefix + '.' + k) : k;
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      Object.assign(acc, flatten(v as Record<string, unknown>, key));
    } else {
      acc[key] = true as const;
    }
    return acc;
  }, Object.create(null) as Record<string, true>);
}

const enDir = path.join(process.cwd(), 'locales', 'en');
const esDir = path.join(process.cwd(), 'locales', 'es');

test('all JSON files have matching key sets (EN ↔ ES)', () => {
  const enFiles = fs.readdirSync(enDir).filter(f => f.endsWith('.json'));
  const esFiles = fs.readdirSync(esDir).filter(f => f.endsWith('.json'));
  expect(new Set(enFiles)).toEqual(new Set(esFiles));
  for (const name of enFiles) {
    const en = flatten(loadJSON(path.join(enDir, name)) as Record<string, unknown>);
    const es = flatten(loadJSON(path.join(esDir, name)) as Record<string, unknown>);
    expect(Object.keys(en).sort()).toEqual(Object.keys(es).sort());
  }
});
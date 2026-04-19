const { spawn } = require('child_process');
const fs = require('fs');

const API_KEY = 'ik_c5eec8dda05677da28915bfbb952aa2a';
const API_BASE = 'https://ad2w6rt5.ap-southeast.insforge.app';

const data = JSON.parse(fs.readFileSync('tmp_db_export.json', 'utf8'));

function escVal(v) {
  if (v === null || v === undefined) return 'NULL';
  // JSON booleans from Python export (true/false)
  if (v === true  || v === 'true')  return 'TRUE';
  if (v === false || v === 'false') return 'FALSE';
  if (typeof v === 'number') return String(v);
  // Escape single quotes
  return "'" + String(v).replace(/'/g, "''") + "'";
}

function buildInserts(table, rows) {
  if (!rows || rows.length === 0) return [];
  const sqls = [];
  for (const row of rows) {
    const cols = Object.keys(row).join(', ');
    const vals = Object.values(row).map(escVal).join(', ');
    sqls.push(`INSERT INTO ${table} (${cols}) VALUES (${vals}) ON CONFLICT DO NOTHING`);
  }
  return sqls;
}

function runSql(sql) {
  return new Promise((resolve, reject) => {
    const server = spawn('npx.cmd', [
      '-y', '@insforge/mcp@latest',
      '--api_key', API_KEY,
      '--api_base_url', API_BASE
    ], { shell: true });

    let output = '';
    let resolved = false;

    server.stdout.on('data', (d) => {
      output += d.toString();
      if (output.includes('"id":2')) {
        if (!resolved) {
          resolved = true;
          try {
            const lines = output.trim().split('\n');
            const resp = JSON.parse(lines.find(l => l.includes('"id":2')));
            resolve(resp);
          } catch(e) { resolve({ raw: output.substring(0, 500) }); }
          server.kill();
        }
      }
    });

    server.stderr.on('data', () => {});
    server.on('error', reject);

    const req1 = { jsonrpc:'2.0', id:1, method:'initialize',
      params:{ protocolVersion:'2024-11-05', capabilities:{}, clientInfo:{ name:'seeder', version:'1.0.0' } } };
    const req2 = { jsonrpc:'2.0', id:2, method:'tools/call',
      params:{ name:'run-raw-sql', arguments:{ query: sql } } };

    server.stdin.write(JSON.stringify(req1) + '\n');
    setTimeout(() => {
      server.stdin.write(JSON.stringify({ jsonrpc:'2.0', method:'notifications/initialized' }) + '\n');
      server.stdin.write(JSON.stringify(req2) + '\n');
    }, 3000);

    setTimeout(() => {
      if (!resolved) { resolved = true; server.kill(); resolve({ timeout: true }); }
    }, 25000);
  });
}

// Reset sequences after insert
function buildSequenceReset(table, idCol = 'id') {
  return `SELECT setval(pg_get_serial_sequence('${table}', '${idCol}'), COALESCE(MAX(${idCol}), 1)) FROM ${table}`;
}

async function main() {
  const ORDER = [
    'users', 'subjects', 'students', 'teachers', 'timetable',
    'attendance_sessions', 'attendance', 'session_activity_log',
    'notification_prefs', 'assignments', 'submissions',
    'announcements', 'notifications', 'announcement_reads'
  ];

  // Clear all tables in reverse FK order first
  const REVERSE = [...ORDER].reverse();
  console.log('🗑️  Clearing existing data...');
  const truncateSql = REVERSE.map(t => `TRUNCATE TABLE ${t} RESTART IDENTITY CASCADE`).join('; ');
  try {
    for (const t of REVERSE) {
      await runSql(`TRUNCATE TABLE ${t} RESTART IDENTITY CASCADE`);
      process.stdout.write(`  cleared ${t}\n`);
    }
  } catch(e) { console.log('  (truncate error — continuing)', e.message); }
  console.log('');

  const log = [];
  let total = 0, ok = 0, fail = 0;

  for (const table of ORDER) {
    const rows = data[table] || [];
    console.log(`\n📦 ${table}: ${rows.length} rows`);
    const inserts = buildInserts(table, rows);

    for (let i = 0; i < inserts.length; i++) {
      const sql = inserts[i];
      process.stdout.write(`  [${i+1}/${inserts.length}] `);
      try {
        const res = await runSql(sql);
        const text = JSON.stringify(res);
        if (text.toLowerCase().includes('error')) {
          console.log('⚠️  ' + text.substring(0, 150));
          log.push({ table, i, status:'error', res: text.substring(0, 300) });
          fail++;
        } else {
          process.stdout.write('✅\n');
          ok++;
        }
      } catch(e) {
        console.log('❌ ' + e.message);
        log.push({ table, i, status:'exception', err: e.message });
        fail++;
      }
      total++;
    }

    // Reset sequence
    if (rows.length > 0) {
      try {
        await runSql(buildSequenceReset(table));
        console.log(`  ↺  sequence reset`);
      } catch(e) {}
    }
  }

  fs.writeFileSync('tmp_data_migration_log.json', JSON.stringify(log, null, 2));
  console.log(`\n════════════════════════════════`);
  console.log(`Total: ${total} | ✅ OK: ${ok} | ❌ Fail: ${fail}`);
  console.log(`Log saved to tmp_data_migration_log.json`);
}

main().catch(console.error);

const { spawn } = require('child_process');
const fs = require('fs');

const API_KEY = 'ik_c5eec8dda05677da28915bfbb952aa2a';
const API_BASE = 'https://ad2w6rt5.ap-southeast.insforge.app';

const data = JSON.parse(fs.readFileSync('tmp_db_export.json', 'utf8'));

function escVal(v) {
  if (v === null || v === undefined) return 'NULL';
  if (v === true  || v === 'true')  return 'TRUE';
  if (v === false || v === 'false') return 'FALSE';
  if (typeof v === 'number') return String(v);
  return "'" + String(v).replace(/'/g, "''") + "'";
}

function buildInsert(table, row) {
  const cols = Object.keys(row).join(', ');
  const vals = Object.values(row).map(escVal).join(', ');
  return `INSERT INTO ${table} (${cols}) VALUES (${vals}) ON CONFLICT DO NOTHING`;
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
      params:{ protocolVersion:'2024-11-05', capabilities:{}, clientInfo:{ name:'fixer', version:'1.0.0' } } };
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

async function run(label, sql) {
  process.stdout.write(`  ${label}... `);
  const res = await runSql(sql);
  const text = JSON.stringify(res);
  if (text.toLowerCase().includes('error')) {
    console.log('⚠️  ' + text.substring(0, 200));
    return false;
  }
  console.log('✅');
  return true;
}

async function main() {
  console.log('\n🔧 Step 1: Fix column sizes\n');

  // Widen password_hash to 256 chars (bcrypt 60 chars, but allow longer legacy hashes)
  await run('ALTER users.password_hash → VARCHAR(256)',
    `ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(256)`);

  // Widen timetable.class_section to 100 chars
  await run('ALTER timetable.class_section → VARCHAR(100)',
    `ALTER TABLE timetable ALTER COLUMN class_section TYPE VARCHAR(100)`);

  // Also fix attendance_sessions.class_section just to be safe
  await run('ALTER attendance_sessions.class_section → VARCHAR(100)',
    `ALTER TABLE attendance_sessions ALTER COLUMN class_section TYPE VARCHAR(100)`);

  console.log('\n🔧 Step 2: Re-insert user 12 (TCH-1223 Swaruuu Sir)\n');
  const user12 = data['users'].find(u => u.id === 12);
  if (user12) {
    await run(`INSERT user id=12 (${user12.name})`, buildInsert('users', user12));
  }

  console.log('\n🔧 Step 3: Re-insert teacher row for user 12\n');
  const teacher12 = data['teachers'].find(t => t.user_id === 12);
  if (teacher12) {
    await run(`INSERT teacher user_id=12`, buildInsert('teachers', teacher12));
  }

  console.log('\n🔧 Step 4: Re-insert all 4 students\n');
  for (const s of data['students']) {
    await run(`INSERT student id=${s.id} user_id=${s.user_id}`, buildInsert('students', s));
  }

  console.log('\n🔧 Step 5: Re-insert timetable rows (all 10, class_section now widened)\n');
  for (const t of data['timetable']) {
    await run(`INSERT timetable id=${t.id} (${t.day_of_week} ${t.class_section})`,
      buildInsert('timetable', t));
  }

  console.log('\n🔧 Step 6: Re-insert all attendance records\n');
  for (const a of data['attendance']) {
    await run(`INSERT attendance id=${a.id}`, buildInsert('attendance', a));
  }

  console.log('\n🔧 Step 7: Re-insert session activity log\n');
  for (const s of data['session_activity_log']) {
    await run(`INSERT activity log id=${s.id}`, buildInsert('session_activity_log', s));
  }

  console.log('\n🔧 Step 8: Re-insert all submissions\n');
  for (const s of data['submissions']) {
    await run(`INSERT submission id=${s.id}`, buildInsert('submissions', s));
  }

  console.log('\n🔧 Step 9: Reset all sequences\n');
  const tables = ['users','subjects','students','teachers','timetable',
    'attendance_sessions','attendance','session_activity_log',
    'notification_prefs','assignments','submissions',
    'announcements','notifications','announcement_reads'];
  for (const t of tables) {
    await run(`reset seq ${t}`,
      `SELECT setval(pg_get_serial_sequence('${t}', 'id'), COALESCE(MAX(id), 1)) FROM ${t}`);
  }

  console.log('\n✅ All fixes applied!');
}

main().catch(console.error);

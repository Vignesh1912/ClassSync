const { spawn } = require('child_process');
const fs = require('fs');

const API_KEY = 'ik_c5eec8dda05677da28915bfbb952aa2a';
const API_BASE = 'https://ad2w6rt5.ap-southeast.insforge.app';

const results = [];
let reqId = 1;

// ── SQL statements to run in order ─────────────────────────────────────────
const sqlStatements = [

// 1. ENUM TYPE
`DO $$ BEGIN
  CREATE TYPE user_roles AS ENUM ('student', 'teacher', 'hod', 'admin');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$`,

// 2. USERS
`CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(128),
  role user_roles NOT NULL,
  is_verified BOOLEAN DEFAULT FALSE,
  department VARCHAR(100),
  college_user_id VARCHAR(50) UNIQUE NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
)`,

// 3. SUBJECTS
`CREATE TABLE IF NOT EXISTS subjects (
  id SERIAL PRIMARY KEY,
  subject_code VARCHAR(20) UNIQUE NOT NULL,
  subject_name VARCHAR(150) NOT NULL,
  credits INTEGER NOT NULL,
  semester INTEGER NOT NULL,
  department VARCHAR(100) NOT NULL
)`,

// 4. STUDENTS
`CREATE TABLE IF NOT EXISTS students (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  class_section VARCHAR(20),
  semester INTEGER,
  roll_number VARCHAR(50),
  batch VARCHAR(50)
)`,

// 5. TEACHERS
`CREATE TABLE IF NOT EXISTS teachers (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  designation VARCHAR(100),
  cabin_no VARCHAR(50)
)`,

// 6. TIMETABLE
`CREATE TABLE IF NOT EXISTS timetable (
  id SERIAL PRIMARY KEY,
  teacher_id INTEGER NOT NULL REFERENCES teachers(id),
  subject_id INTEGER NOT NULL REFERENCES subjects(id),
  day_of_week VARCHAR(20) NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  room_number VARCHAR(50) NOT NULL,
  class_section VARCHAR(20) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
)`,

// 7. ATTENDANCE SESSIONS
`CREATE TABLE IF NOT EXISTS attendance_sessions (
  id SERIAL PRIMARY KEY,
  teacher_id INTEGER NOT NULL REFERENCES teachers(id),
  subject_id INTEGER NOT NULL REFERENCES subjects(id),
  session_date DATE NOT NULL,
  start_time TIMESTAMPTZ NOT NULL,
  end_time_limit TIMESTAMPTZ NOT NULL,
  classroom_name VARCHAR(100) NOT NULL,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  radius_meters DOUBLE PRECISION DEFAULT 50.0,
  status VARCHAR(20) DEFAULT 'active',
  total_present INTEGER DEFAULT 0,
  class_section VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
)`,

// 8. ATTENDANCE
`CREATE TABLE IF NOT EXISTS attendance (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES attendance_sessions(id),
  student_id INTEGER NOT NULL REFERENCES students(id),
  marked_at TIMESTAMPTZ DEFAULT NOW(),
  student_latitude DOUBLE PRECISION NOT NULL,
  student_longitude DOUBLE PRECISION NOT NULL,
  distance_from_class DOUBLE PRECISION NOT NULL,
  status VARCHAR(20) DEFAULT 'present',
  is_valid BOOLEAN DEFAULT TRUE,
  ip_address VARCHAR(45),
  CONSTRAINT uix_session_student UNIQUE (session_id, student_id)
)`,

// 9. SESSION ACTIVITY LOG
`CREATE TABLE IF NOT EXISTS session_activity_log (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES attendance_sessions(id),
  student_id INTEGER REFERENCES students(id),
  action VARCHAR(50) NOT NULL,
  reason VARCHAR(255),
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  ip_address VARCHAR(45),
  logged_at TIMESTAMPTZ DEFAULT NOW()
)`,

// 10. NOTIFICATION PREFS
`CREATE TABLE IF NOT EXISTS notification_prefs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
  email_enabled BOOLEAN DEFAULT TRUE,
  remind_3days BOOLEAN DEFAULT TRUE,
  remind_2days BOOLEAN DEFAULT TRUE,
  remind_1day BOOLEAN DEFAULT TRUE,
  remind_deadline BOOLEAN DEFAULT TRUE
)`,

// 11. ASSIGNMENTS
`CREATE TABLE IF NOT EXISTS assignments (
  id SERIAL PRIMARY KEY,
  teacher_id INTEGER NOT NULL REFERENCES teachers(id),
  subject_id INTEGER NOT NULL REFERENCES subjects(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  deadline TIMESTAMPTZ NOT NULL,
  classroom_link VARCHAR(500),
  resource_path VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW()
)`,

// 12. SUBMISSIONS
`CREATE TABLE IF NOT EXISTS submissions (
  id SERIAL PRIMARY KEY,
  assignment_id INTEGER NOT NULL REFERENCES assignments(id),
  student_id INTEGER NOT NULL REFERENCES students(id),
  self_reported BOOLEAN DEFAULT FALSE,
  submitted_at TIMESTAMPTZ,
  status VARCHAR(20) DEFAULT 'pending',
  CONSTRAINT uix_assignment_student UNIQUE (assignment_id, student_id)
)`,

// 13. ANNOUNCEMENTS
`CREATE TABLE IF NOT EXISTS announcements (
  id SERIAL PRIMARY KEY,
  posted_by INTEGER NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  priority VARCHAR(20) DEFAULT 'normal',
  target_audience VARCHAR(20) DEFAULT 'all',
  target_class VARCHAR(100),
  target_department VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
)`,

// 14. NOTIFICATIONS
`CREATE TABLE IF NOT EXISTS notifications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  type VARCHAR(50) DEFAULT 'general',
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
)`,

// 15. ANNOUNCEMENT READS
`CREATE TABLE IF NOT EXISTS announcement_reads (
  id SERIAL PRIMARY KEY,
  announcement_id INTEGER NOT NULL REFERENCES announcements(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  read_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT uix_ann_user UNIQUE (announcement_id, user_id)
)`,

];

// ── MCP runner ──────────────────────────────────────────────────────────────
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
          } catch(e) { resolve({ raw: output }); }
          server.kill();
        }
      }
    });

    server.stderr.on('data', () => {});
    server.on('error', reject);

    const req1 = { jsonrpc:'2.0', id:1, method:'initialize',
      params:{ protocolVersion:'2024-11-05', capabilities:{}, clientInfo:{ name:'migrator', version:'1.0.0' } } };
    const req2 = { jsonrpc:'2.0', id:2, method:'tools/call',
      params:{ name:'run-raw-sql', arguments:{ query: sql } } };

    server.stdin.write(JSON.stringify(req1) + '\n');
    setTimeout(() => {
      server.stdin.write(JSON.stringify({ jsonrpc:'2.0', method:'notifications/initialized' }) + '\n');
      server.stdin.write(JSON.stringify(req2) + '\n');
    }, 3000);

    setTimeout(() => {
      if (!resolved) {
        resolved = true;
        server.kill();
        resolve({ timeout: true, raw: output });
      }
    }, 20000);
  });
}

async function main() {
  console.log(`Running ${sqlStatements.length} SQL statements on InsForge...\n`);
  const log = [];

  for (let i = 0; i < sqlStatements.length; i++) {
    const sql = sqlStatements[i];
    const label = sql.trim().split('\n')[0].substring(0, 80);
    process.stdout.write(`[${i+1}/${sqlStatements.length}] ${label}... `);
    try {
      const res = await runSql(sql);
      const text = JSON.stringify(res);
      if (text.includes('error') || text.includes('Error')) {
        console.log('⚠️  ' + text.substring(0, 200));
        log.push({ i, label, status: 'error', res: text });
      } else {
        console.log('✅');
        log.push({ i, label, status: 'ok' });
      }
    } catch(e) {
      console.log('❌ ' + e.message);
      log.push({ i, label, status: 'exception', err: e.message });
    }
  }

  fs.writeFileSync('tmp_schema_migration_log.json', JSON.stringify(log, null, 2));
  console.log('\nDone! Log saved to tmp_schema_migration_log.json');
}

main().catch(console.error);

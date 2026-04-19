const { spawn } = require('child_process');

const API_KEY = 'ik_c5eec8dda05677da28915bfbb952aa2a';
const API_BASE = 'https://ad2w6rt5.ap-southeast.insforge.app';

const statements = [
  'ALTER TABLE students ALTER COLUMN class_section TYPE VARCHAR(100);',
  'ALTER TABLE timetable ALTER COLUMN class_section TYPE VARCHAR(100);',
  'ALTER TABLE attendance_sessions ALTER COLUMN class_section TYPE VARCHAR(100);'
];

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
          } catch(e) { resolve({ raw: output.substring(0, 800) }); }
          server.kill();
        }
      }
    });

    server.stdin.write(JSON.stringify({ jsonrpc:'2.0', id:1, method:'initialize', params:{ protocolVersion:'2024-11-05', capabilities:{}, clientInfo:{ name:'fixer', version:'1' } } }) + '\n');
    setTimeout(() => {
      server.stdin.write(JSON.stringify({ jsonrpc:'2.0', method:'notifications/initialized' }) + '\n');
      server.stdin.write(JSON.stringify({ jsonrpc:'2.0', id:2, method:'tools/call', params:{ name:'run-raw-sql', arguments:{ query: sql } } }) + '\n');
    }, 3000);

    setTimeout(() => {
      if (!resolved) { resolved = true; server.kill(); resolve({ timeout: true }); }
    }, 20000);
  });
}

async function main() {
  for (const sql of statements) {
    console.log(`Running: ${sql}`);
    const res = await runSql(sql);
    console.log(JSON.stringify(res).substring(0, 200));
  }
}

main().catch(console.error);

const { spawn } = require('child_process');

const API_KEY = 'ik_c5eec8dda05677da28915bfbb952aa2a';
const API_BASE = 'https://ad2w6rt5.ap-southeast.insforge.app';

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
    server.stderr.on('data', () => {});
    server.on('error', reject);

    const req1 = { jsonrpc:'2.0', id:1, method:'initialize',
      params:{ protocolVersion:'2024-11-05', capabilities:{}, clientInfo:{ name:'checker', version:'1.0.0' } } };
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

async function q(label, sql) {
  process.stdout.write(`\n── ${label} ──\n`);
  const res = await runSql(sql);
  try {
    const text = res.result.content[0].text;
    const parsed = JSON.parse(text.replace('SQL query executed completed successfully:\n', ''));
    console.log(JSON.stringify(parsed.rows, null, 2));
  } catch(e) {
    console.log(JSON.stringify(res).substring(0, 600));
  }
}

async function main() {
  // Find all user IDs currently on InsForge
  await q('All user IDs on InsForge', 'SELECT id, college_user_id, name FROM users ORDER BY id');
  await q('Students table', 'SELECT * FROM students ORDER BY id');
}

main().catch(console.error);

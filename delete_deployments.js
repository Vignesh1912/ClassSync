const { spawn } = require('child_process');

const server = spawn('npx.cmd', [
  '-y',
  '@insforge/mcp@latest',
  '--api_key', 'ik_9437f7267eaab43f45641eeb1506c8dc',
  '--api_base_url', 'https://a4k6xpce.ap-southeast.insforge.app'
], { shell: true });

let output = '';

server.stdout.on('data', (d) => {
  const str = d.toString();
  output += str;
  if(str.includes('"id":2')) {
    const fs = require('fs');
    fs.writeFileSync('c:/Users/vigne/classSync/delete_deployments_out.txt', output);
    server.kill();
    process.exit(0);
  }
});

server.stderr.on('data', (d) => {
  console.error('STDERR:', d.toString());
});

const req1 = {
  jsonrpc: '2.0', id: 1, method: 'initialize',
  params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'test', version: '1.0.0' } }
};

const req2 = {
  jsonrpc: '2.0', id: 2, method: 'tools/call',
  params: { 
    name: 'run-raw-sql', 
    arguments: { 
      sql: "DELETE FROM system.deployments;"
    } 
  }
};

server.stdin.write(JSON.stringify(req1) + '\n');
setTimeout(() => {
  server.stdin.write(JSON.stringify({jsonrpc: '2.0', method: 'notifications/initialized'}) + '\n');
  server.stdin.write(JSON.stringify(req2) + '\n');
}, 3000);

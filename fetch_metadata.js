const { spawn } = require('child_process');

const server = spawn('npx.cmd', [
  '-y',
  '@insforge/mcp@latest',
  '--api_key', 'ik_c5eec8dda05677da28915bfbb952aa2a',
  '--api_base_url', 'https://ad2w6rt5.ap-southeast.insforge.app'
], { shell: true });

let output = '';

server.stdout.on('data', (d) => {
  const str = d.toString();
  output += str;
  if(str.includes('"id":2')) {
    const fs = require('fs');
    fs.writeFileSync('c:/Users/vigne/classSync/metadata_out.txt', output);
    server.kill();
    process.exit(0);
  }
});

const req1 = {
  jsonrpc: '2.0', id: 1, method: 'initialize',
  params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'test', version: '1.0.0' } }
};

const req2 = {
  jsonrpc: '2.0', id: 2, method: 'tools/call',
  params: { 
    name: 'get-backend-metadata', 
    arguments: {} 
  }
};

server.stdin.write(JSON.stringify(req1) + '\n');
setTimeout(() => {
  server.stdin.write(JSON.stringify({jsonrpc: '2.0', method: 'notifications/initialized'}) + '\n');
  server.stdin.write(JSON.stringify(req2) + '\n');
}, 3000);

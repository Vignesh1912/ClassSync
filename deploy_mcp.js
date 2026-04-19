const { spawn } = require('child_process');
const fs = require('fs');
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
    fs.writeFileSync('deploy_mcp_out2.txt', output);
    console.log('Got response for id 2, writing to file');
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
    name: 'create-deployment', 
    arguments: { 
      sourceDirectory: 'c:/Users/vigne/classSync/empty_deploy'
    } 
  }
};

server.stdin.write(JSON.stringify(req1) + '\n');
setTimeout(() => {
  server.stdin.write(JSON.stringify({jsonrpc: '2.0', method: 'notifications/initialized'}) + '\n');
  server.stdin.write(JSON.stringify(req2) + '\n');
}, 3000);

setTimeout(() => {
  server.kill();
  fs.writeFileSync('deploy_mcp_out2_timeout.txt', output);
  console.log('Timeout');
}, 60000);

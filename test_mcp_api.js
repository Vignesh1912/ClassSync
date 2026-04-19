const { spawn } = require('child_process');
const server = spawn('npx.cmd', ['-y', '@insforge/mcp@latest', '--api_key', 'ik_9437f7267eaab43f45641eeb1506c8dc', '--api_base_url', 'https://a4k6xpce.ap-southeast.insforge.app'], { shell: true });
let output = '';
server.stdout.on('data', (d) => {
  output += d.toString();
  if(output.includes('"id":2')) {
    console.log(output);
    server.kill();
    process.exit(0);
  }
});
const req1 = { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'test', version: '1.0.0' } } };
const req2 = { jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: 'fetch-sdk-docs', arguments: { featureType: 'deployment', language: 'rest-api' } } };
server.stdin.write(JSON.stringify(req1) + '\n');
setTimeout(() => {
  server.stdin.write(JSON.stringify({jsonrpc: '2.0', method: 'notifications/initialized'}) + '\n');
  server.stdin.write(JSON.stringify(req2) + '\n');
}, 2000);

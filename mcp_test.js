const { spawn } = require('child_process');

const server = spawn('npx.cmd', [
  '-y',
  '@insforge/mcp@latest',
  '--api_key', 'ik_9437f7267eaab43f45641eeb1506c8dc',
  '--api_base_url', 'https://a4k6xpce.ap-southeast.insforge.app'
], { shell: true });

const fs = require('fs');
const outStream = fs.createWriteStream('mcp_out.log');
server.stdout.on('data', (data) => {
  outStream.write(data);
});
server.stderr.on('data', (data) => {
  console.error(`STDERR: ${data}`);
});

const req1 = {
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "test", version: "1.0.0" }
  }
};

const req2 = {
  jsonrpc: "2.0",
  id: 2,
  method: "tools/call",
  params: {
    name: "fetch-docs",
    arguments: { docType: "instructions" }
  }
};

server.stdin.write(JSON.stringify(req1) + '\n');
setTimeout(() => {
  server.stdin.write(JSON.stringify({jsonrpc: "2.0", method: "notifications/initialized"}) + '\n');
  server.stdin.write(JSON.stringify(req2) + '\n');
}, 2000);

setTimeout(() => {
  server.kill();
}, 8000);

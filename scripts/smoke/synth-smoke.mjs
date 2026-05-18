import { execSync } from 'node:child_process';

function run(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
}

try {
  const output = run('npx aws-cdk synth');
  const checks = [
    'AWS::BedrockAgentCore::Memory',
    'AWS::BedrockAgentCore::Runtime',
    'AWS::BedrockAgentCore::RuntimeEndpoint',
    'poc_memory_writer_runtime',
    'poc_memory_reader_runtime',
  ];

  const missing = checks.filter((token) => !output.includes(token));

  if (missing.length > 0) {
    console.error(`SMOKE FAILED: missing tokens in synthesized template: ${missing.join(', ')}`);
    process.exit(2);
  }

  if (output.includes('claude-code-runtime') || output.includes('gitlab-runtime')) {
    console.error('SMOKE FAILED: stable runtime names leaked into POC template.');
    process.exit(3);
  }

  console.log('SMOKE PASSED: synthesized template includes expected AgentCore resources.');
} catch (err) {
  console.error('SMOKE FAILED: cdk synth command failed.');
  console.error(String(err?.stderr || err?.message || err));
  process.exit(1);
}

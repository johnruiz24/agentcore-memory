import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { AgentCoreSharedMemoryPocStack } from '../lib/agentcore-shared-memory-poc-stack';

describe('AgentCoreSharedMemoryPocStack', () => {
  const app = new cdk.App();
  const stack = new AgentCoreSharedMemoryPocStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  test('creates one shared memory and two runtimes', () => {
    template.resourceCountIs('AWS::BedrockAgentCore::Memory', 1);
    template.resourceCountIs('AWS::BedrockAgentCore::Runtime', 2);
    template.resourceCountIs('AWS::BedrockAgentCore::RuntimeEndpoint', 2);
  });

  test('uses new POC runtime names and never stable names', () => {
    template.hasResourceProperties('AWS::BedrockAgentCore::Runtime', {
      AgentRuntimeName: 'poc_memory_writer_runtime',
    });

    template.hasResourceProperties('AWS::BedrockAgentCore::Runtime', {
      AgentRuntimeName: 'poc_memory_reader_runtime',
    });

    const json = JSON.stringify(template.toJSON());
    expect(json).not.toContain('claude-code-runtime');
    expect(json).not.toContain('gitlab-runtime');
  });

  test('exports memory and endpoint outputs for smoke/e2e execution', () => {
    template.hasOutput('SharedMemoryId', {});
    template.hasOutput('WriterRuntimeArn', {});
    template.hasOutput('ReaderRuntimeArn', {});
    template.hasOutput('WriterRuntimeEndpointArn', {});
    template.hasOutput('ReaderRuntimeEndpointArn', {});
  });
});

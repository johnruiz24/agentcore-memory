import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { AgentCoreSharedMemoryPocStack } from '../lib/agentcore-shared-memory-poc-stack';

describe('E2E contract (synth-level)', () => {
  test('memory strategy namespaces are present for semantic and summary retrieval flows', () => {
    const app = new cdk.App();
    const stack = new AgentCoreSharedMemoryPocStack(app, 'E2EContractStack');
    const template = Template.fromStack(stack);

    template.hasResourceProperties('AWS::BedrockAgentCore::Memory', {
      MemoryStrategies: [
        {
          SemanticMemoryStrategy: {
            Namespaces: ['/org/{actorId}/workflow/{sessionId}/semantic/'],
          },
        },
        {
          SummaryMemoryStrategy: {
            Namespaces: ['/org/{actorId}/workflow/{sessionId}/summary/'],
          },
        },
      ],
    });
  });
});

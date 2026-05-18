import { Stack, StackProps, CfnOutput, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrockagentcore from 'aws-cdk-lib/aws-bedrockagentcore';
import * as s3assets from 'aws-cdk-lib/aws-s3-assets';

export class AgentCoreSharedMemoryPocStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const writerModelId =
      this.node.tryGetContext('writerModelId') ?? 'eu.anthropic.claude-haiku-4-5-20251001-v1:0';
    const readerModelId =
      this.node.tryGetContext('readerModelId') ?? 'eu.anthropic.claude-haiku-4-5-20251001-v1:0';

    const writerRuntimeAsset = new s3assets.Asset(this, 'WriterRuntimeAsset', {
      path: 'runtime-src/writer',
    });

    const readerRuntimeAsset = new s3assets.Asset(this, 'ReaderRuntimeAsset', {
      path: 'runtime-src/reader',
    });

    const runtimeRole = new iam.Role(this, 'AgentCoreRuntimeRole', {
      assumedBy: new iam.ServicePrincipal('bedrock-agentcore.amazonaws.com'),
      description: 'Execution role for POC AgentCore runtimes only',
    });

    runtimeRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('CloudWatchLogsFullAccess'));
    runtimeRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));
    runtimeRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          'bedrock-agentcore:CreateEvent',
          'bedrock-agentcore:RetrieveMemoryRecords',
          'bedrock-agentcore:ListMemoryRecords',
          'bedrock-agentcore:GetMemoryRecord',
        ],
        resources: ['*'],
      }),
    );
    writerRuntimeAsset.grantRead(runtimeRole);
    readerRuntimeAsset.grantRead(runtimeRole);

    const sharedMemory = new bedrockagentcore.CfnMemory(this, 'SharedLongTermMemory', {
      name: 'pocSharedMemory',
      description: 'Shared long-term memory for writer/reader AgentCore runtime POC',
      eventExpiryDuration: 30,
      memoryStrategies: [
        {
          semanticMemoryStrategy: {
            name: 'PocSemanticStrategy',
            description: 'Semantic long-term strategy for shared runtime memory',
            namespaces: ['/org/{actorId}/workflow/{sessionId}/semantic/'],
          },
        },
        {
          summaryMemoryStrategy: {
            name: 'PocSummaryStrategy',
            description: 'Summary long-term strategy for shared runtime memory',
            namespaces: ['/org/{actorId}/workflow/{sessionId}/summary/'],
          },
        },
      ],
      tags: {
        Purpose: 'agentcore-shared-memory-poc',
        Scope: 'new-runtimes-only',
      },
    });

    const writerRuntime = new bedrockagentcore.CfnRuntime(this, 'WriterRuntime', {
      agentRuntimeName: 'poc_memory_writer_runtime',
      description: 'Dedicated writer runtime for shared-memory POC',
      roleArn: runtimeRole.roleArn,
      protocolConfiguration: 'HTTP',
      networkConfiguration: {
        networkMode: 'PUBLIC',
      },
      lifecycleConfiguration: {
        idleRuntimeSessionTimeout: 900,
        maxLifetime: 3600,
      },
      environmentVariables: {
        SHARED_MEMORY_ID: sharedMemory.attrMemoryId,
        RUNTIME_ROLE: 'writer',
        WRITER_MODEL_ID: writerModelId,
      },
      agentRuntimeArtifact: {
        codeConfiguration: {
          runtime: 'PYTHON_3_12',
          entryPoint: ['app.py'],
          code: {
            s3: {
              bucket: writerRuntimeAsset.s3BucketName,
              prefix: writerRuntimeAsset.s3ObjectKey,
            },
          },
        },
      },
      tags: {
        Purpose: 'agentcore-shared-memory-poc',
        RuntimeRole: 'writer',
      },
    });

    const readerRuntime = new bedrockagentcore.CfnRuntime(this, 'ReaderRuntime', {
      agentRuntimeName: 'poc_memory_reader_runtime',
      description: 'Dedicated reader runtime for shared-memory POC',
      roleArn: runtimeRole.roleArn,
      protocolConfiguration: 'HTTP',
      networkConfiguration: {
        networkMode: 'PUBLIC',
      },
      lifecycleConfiguration: {
        idleRuntimeSessionTimeout: 900,
        maxLifetime: 3600,
      },
      environmentVariables: {
        SHARED_MEMORY_ID: sharedMemory.attrMemoryId,
        RUNTIME_ROLE: 'reader',
        READER_MODEL_ID: readerModelId,
      },
      agentRuntimeArtifact: {
        codeConfiguration: {
          runtime: 'PYTHON_3_12',
          entryPoint: ['app.py'],
          code: {
            s3: {
              bucket: readerRuntimeAsset.s3BucketName,
              prefix: readerRuntimeAsset.s3ObjectKey,
            },
          },
        },
      },
      tags: {
        Purpose: 'agentcore-shared-memory-poc',
        RuntimeRole: 'reader',
      },
    });

    const writerEndpoint = new bedrockagentcore.CfnRuntimeEndpoint(this, 'WriterRuntimeEndpoint', {
      name: 'pocMemoryWriterEndpoint',
      description: 'Endpoint for writer runtime in shared-memory POC',
      agentRuntimeId: writerRuntime.attrAgentRuntimeId,
      agentRuntimeVersion: writerRuntime.attrAgentRuntimeVersion,
      tags: {
        Purpose: 'agentcore-shared-memory-poc',
      },
    });

    const readerEndpoint = new bedrockagentcore.CfnRuntimeEndpoint(this, 'ReaderRuntimeEndpoint', {
      name: 'pocMemoryReaderEndpoint',
      description: 'Endpoint for reader runtime in shared-memory POC',
      agentRuntimeId: readerRuntime.attrAgentRuntimeId,
      agentRuntimeVersion: readerRuntime.attrAgentRuntimeVersion,
      tags: {
        Purpose: 'agentcore-shared-memory-poc',
      },
    });

    writerRuntime.addDependency(sharedMemory);
    readerRuntime.addDependency(sharedMemory);
    writerEndpoint.addDependency(writerRuntime);
    readerEndpoint.addDependency(readerRuntime);

    new CfnOutput(this, 'SharedMemoryId', {
      value: sharedMemory.attrMemoryId,
      description: 'Shared AgentCore Memory ID used by both new POC runtimes',
    });

    new CfnOutput(this, 'WriterRuntimeArn', {
      value: writerRuntime.attrAgentRuntimeArn,
      description: 'Writer runtime ARN',
    });

    new CfnOutput(this, 'ReaderRuntimeArn', {
      value: readerRuntime.attrAgentRuntimeArn,
      description: 'Reader runtime ARN',
    });

    new CfnOutput(this, 'WriterModelId', {
      value: writerModelId,
      description: 'Model ID used by writer runtime',
    });

    new CfnOutput(this, 'ReaderModelId', {
      value: readerModelId,
      description: 'Model ID used by reader runtime',
    });

    new CfnOutput(this, 'WriterRuntimeEndpointArn', {
      value: writerEndpoint.ref,
      description: 'Writer runtime endpoint ARN',
    });

    new CfnOutput(this, 'ReaderRuntimeEndpointArn', {
      value: readerEndpoint.ref,
      description: 'Reader runtime endpoint ARN',
    });

    new CfnOutput(this, 'SmokeWaitHintSeconds', {
      value: Duration.seconds(90).toSeconds().toString(),
      description: 'Suggested wait for async long-term extraction during smoke demo',
    });
  }
}

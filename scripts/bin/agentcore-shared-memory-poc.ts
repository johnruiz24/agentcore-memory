#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AgentCoreSharedMemoryPocStack } from '../lib/agentcore-shared-memory-poc-stack';

const app = new cdk.App();

new AgentCoreSharedMemoryPocStack(app, 'AgentCoreSharedMemoryPocStack', {
  description: 'POC stack: shared Bedrock AgentCore Memory + two new dedicated runtimes',
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

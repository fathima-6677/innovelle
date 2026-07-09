#!/usr/bin/env source-map-support/register
import * as cdk from 'aws-cdk-lib';
import { NetworkingStack } from '../lib/networking-stack';
import { AuthStack } from '../lib/auth-stack';
import { DatabaseStack } from '../lib/database-stack';
//import { IngestionStack } from '../lib/ingestion-stack';
import { ComputeStack } from '../lib/compute-stack';
import { SecurityStack } from '../lib/security-stack';
import { FrontendStack } from '../lib/frontend-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'ap-south-1',
};

// 1. Networking Stack
const networking = new NetworkingStack(app, 'AutiGuardNetworkingStack', { env });

// 2. Auth Stack
const auth = new AuthStack(app, 'AutiGuardAuthStack', { env });

// 3. Database Stack
const database = new DatabaseStack(app, 'AutiGuardDatabaseStack', { env });

// 4. Security Stack (KMS keys, Secrets, WAF)
const security = new SecurityStack(app, 'AutiGuardSecurityStack', { env });

// 5. Ingestion Stack (IoT Core, Kinesis, S3)
// const ingestion = new IngestionStack(app, 'AutiGuardIngestionStack', {
//   env,
//   rawTelemetryBucket: security.rawTelemetryBucket,
// });

// 6. Compute Stack (ECS Fargate + Lambdas)
const compute = new ComputeStack(app, 'AutiGuardComputeStack', {
  env,
  vpc: networking.vpc,
  table: database.table,
  kmsKey: security.kmsKey,
  userPool: auth.userPool,
  userPoolClient: auth.userPoolClient,
});

// 7. Frontend Stack (S3, CloudFront)
const frontend = new FrontendStack(app, 'AutiGuardFrontendStack', {
  env,
  apiGatewayUrl: compute.apiGatewayUrl,
});

app.synth();

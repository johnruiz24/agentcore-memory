# Stage 2: Reorganization Planning
**Date**: 2026-05-18  
**Status**: Planning Phase (No Changes Yet)  
**Approval**: Required Before Stage 3 Execution

---

## Executive Summary

Transform root directory from cluttered (12+ config files visible) to professional (clean root, organized ./config/ subdirectory). Zero breaking changes to imports or runtime behavior.

**Files to Move**: 5  
**Files to Update**: 2  
**Risk Level**: 🟢 LOW  
**Estimated Time**: 30 minutes execution  

---

## File Reorganization Plan

### Current State (Before)
```
ROOT (cluttered)
├── .env.example
├── .gitignore
├── .git
├── cdk.json           ← MOVE to config/
├── eslint.config.js   ← MOVE to config/
├── jest.config.js     ← MOVE to config/
├── tsconfig.json      ← MOVE to config/
├── package.json
├── package-lock.json
├── README.md
├── ARCHITECTURE.md
├── SETUP.md
├── CONTRIBUTING.md
├── EXAMPLES.md
├── AGENTS.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── reference.md
├── bin/
├── lib/
├── test/
├── runtime-src/
├── scripts/
├── docs/
├── deployment/
├── assets/
├── evidence/
└── node_modules/
```

### Target State (After)
```
ROOT (clean)
├── .git
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── SETUP.md
├── CONTRIBUTING.md
├── EXAMPLES.md
├── AGENTS.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── package.json
├── package-lock.json
├── reference.md
├── config/              ← NEW DIRECTORY
│   ├── .env.example
│   ├── cdk.json
│   ├── eslint.config.js
│   ├── jest.config.js
│   └── tsconfig.json
├── bin/
├── lib/
├── test/
├── runtime-src/
├── scripts/
├── docs/
├── deployment/
├── assets/
├── evidence/
└── node_modules/
```

---

## Step-by-Step Migration Strategy

### Step 1: Create config Directory
```bash
mkdir -p config
```

**Verification**: `ls -d config/`

### Step 2: Move Configuration Files
```bash
mv tsconfig.json config/
mv jest.config.js config/
mv eslint.config.js config/
mv cdk.json config/
mv .env.example config/.env.example
```

**Verification**: `ls -la config/` should show 5 files

### Step 3: Update package.json Script References

**File**: `package.json`  
**Current** (lines 12-18):
```json
"scripts": {
  "build": "tsc --pretty false",
  "lint": "eslint bin lib test --ext .ts",
  "test": "jest --runInBand",
  "e2e": "jest --runInBand test/e2e-contract.test.ts",
  "smoke": "node scripts/smoke/synth-smoke.mjs",
  "synth": "npx aws-cdk synth",
  "deploy": "npx aws-cdk deploy --require-approval never"
}
```

**Updated**:
```json
"scripts": {
  "build": "tsc --pretty false --project config/tsconfig.json",
  "lint": "eslint bin lib test --ext .ts",
  "test": "jest --runInBand",
  "e2e": "jest --runInBand test/e2e-contract.test.ts",
  "smoke": "node scripts/smoke/synth-smoke.mjs",
  "synth": "npx aws-cdk synth",
  "deploy": "npx aws-cdk deploy --require-approval never"
}
```

**Why**: TypeScript compiler needs explicit path to config/tsconfig.json

### Step 4: Update jest.config.js

**File**: `config/jest.config.js`  
**Current** (line 6):
```javascript
'^.+\\.tsx?$': ['ts-jest', { tsconfig: 'tsconfig.json' }],
```

**Updated**:
```javascript
'^.+\\.tsx?$': ['ts-jest', { tsconfig: '../tsconfig.json' }],
```

**Why**: Jest in config/ needs to reference parent directory tsconfig

### Step 5: Verify cdk.json Path

**File**: `config/cdk.json`  
**Current** (line 2):
```json
"app": "npx ts-node --prefer-ts-exts bin/agentcore-shared-memory-poc.ts",
```

**Status**: ✅ NO CHANGE NEEDED  
**Reason**: Path is relative to project root where CDK runs

### Step 6: Update .gitignore (if needed)

**File**: `.gitignore`  
**Add** (if not present):
```
config/.env
config/.env.local
```

**Status**: Review existing .gitignore to avoid conflicts

---

## Configuration References (Validation Map)

| File | Reference Point | Old Path | New Path | Update Required |
|------|-----------------|----------|----------|-----------------|
| package.json | build script | `tsc` | `tsc --project config/tsconfig.json` | ✅ YES |
| config/jest.config.js | tsconfig ref | `tsconfig.json` | `../tsconfig.json` | ✅ YES |
| config/cdk.json | app entry | `bin/agentcore-shared-memory-poc.ts` | unchanged | ❌ NO |
| lib/agentcore-shared-memory-poc-stack.ts | S3 assets | `runtime-src/writer` | unchanged | ❌ NO |
| lib/agentcore-shared-memory-poc-stack.ts | S3 assets | `runtime-src/reader` | unchanged | ❌ NO |

---

## Verification Strategy (Before/After)

### Before Migration
```bash
npm run build      # ✅ Should succeed
npm run lint       # ✅ Should succeed
npm run test       # ✅ Should succeed
npm run synth      # ✅ Should succeed
```

### After Migration
Execute in exact order to catch issues early:
```bash
npm run build      # Tests tsc path resolution
npm run lint       # Tests eslint paths
npm run test       # Tests jest config changes
npm run synth      # Tests cdk.json and CDK asset paths
```

**Success Criteria**: All 4 commands complete without errors

---

## Parallel Work Planning (For Stage 3 Execution)

While reorganization happens, prepare in parallel:

### Work Stream A: Reorganization (Sequential)
1. Create config/ directory
2. Move 5 config files
3. Update 2 files (package.json, jest.config.js)
4. Run verification scripts
5. Fix any issues

**Owner**: Main executor  
**Duration**: ~30 minutes

### Work Stream B: Diagram Generation (Parallel)
1. Invoke gpt-image-2 skill for system-architecture diagram
2. Generate component-interactions diagram
3. Generate memory-flow diagram
4. Generate agent-lifecycle diagram
5. Generate api-request-flow diagram

**Owner**: Diagram generation task  
**Duration**: ~45 minutes  
**Dependency**: None - can run independently

### Work Stream C: README Rewrite (Sequential, after B)
1. Analyze agentcore-identity README structure
2. Identify sections to rewrite
3. Rewrite README with professional standards
4. Add diagram references
5. Validate markdown formatting

**Owner**: Documentation task  
**Duration**: ~60 minutes  
**Dependency**: Requires new diagrams

### Work Stream D: Contributors Cleanup (Parallel to B)
1. Analyze git history for actual contributors
2. Update package.json or CONTRIBUTING.md with real authors
3. Remove non-contributors from authors field

**Owner**: Git analysis task  
**Duration**: ~15 minutes  
**Dependency**: None

---

## Stage 3 Execution Order

After approval of this plan, execute in this order:

```
START
  │
  ├─ 1. Create config/ directory (sequential)
  │
  ├─ 2. Move config files (sequential)
  │   │
  │   ├─ 3a. Update package.json (sequential)
  │   ├─ 3b. Update jest.config.js (sequential)
  │   │
  │   └─ 4. Verify scripts (sequential)
  │
  ├─ 5. Generate diagrams (parallel with 3a-3b)
  ├─ 6. Rewrite README (after diagrams)
  ├─ 7. Fix contributors (parallel with diagram work)
  │
  └─ 8. Final QA verification
     └─ Build + Lint + Test + Synth
```

---

## Rollback Plan (If Anything Breaks)

Rollback is simple and safe due to file isolation:

```bash
# Step 1: Restore config files to root
mv config/tsconfig.json .
mv config/jest.config.js .
mv config/eslint.config.js .
mv config/cdk.json .
mv config/.env.example .

# Step 2: Revert package.json
git checkout package.json

# Step 3: Restore jest config
git checkout jest.config.js

# Step 4: Remove config directory
rmdir config

# Step 5: Verify
npm run build
npm run test
```

**Rollback Duration**: < 5 minutes

---

## Risk Mitigation

### Risk 1: TypeScript Compilation Fails
**Mitigation**: Test `npm run build` immediately after package.json change  
**Severity**: 🟡 MEDIUM → Easily fixed if caught immediately

### Risk 2: Jest Tests Fail  
**Mitigation**: Test `npm run test` immediately after jest.config.js change  
**Severity**: 🟡 MEDIUM → Revert jest config change if needed

### Risk 3: CDK Synthesis Fails
**Mitigation**: Test `npm run synth` after all file moves  
**Severity**: 🟡 MEDIUM → S3 asset paths unaffected, unlikely

### Risk 4: Git History Lost
**Mitigation**: NO CHANGES TO GIT - all file moves preserve git history  
**Severity**: 🟢 LOW → File history remains accessible via `git log --follow`

---

## Success Criteria

✅ **Reorganization Complete When**:
1. Root directory contains only essential files (no config files)
2. `config/` directory contains all 5 configuration files
3. `npm run build` completes without errors
4. `npm run test` passes all tests
5. `npm run lint` shows no new issues
6. `npm run synth` generates CloudFormation successfully
7. Git commits made with clear messages showing file moves

---

## Next Steps

1. **Review this plan** ← YOU ARE HERE
2. **Approve/request changes** ← WAITING FOR USER
3. **Execute Stage 3** (if approved)
4. **Run QA verification** (Stage 4)
5. **Final validation** (Stage 5)

---

## Appendix: Reference Implementation

Compare target structure with agentcore-identity:
- **agentcore-identity**: Config files in root (not optimized) ❌
- **Our target**: Config files in `./config/` (professional) ✅

This represents an IMPROVEMENT over the reference implementation while maintaining compatibility with existing TypeScript/Node.js tooling.

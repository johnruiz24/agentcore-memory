---
name: Technical Article Generator
description: Generate high-quality technical articles following the AgentCore Identity/Memory pattern - story-driven narrative, 3-4 problem sections, architecture deep dive, production evidence, honest tradeoffs, and 10-12 professional images via gpt-image-2.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Technical Article Generator

This skill generates enterprise-quality technical articles following the proven AgentCore Identity/Memory pattern: story-driven narrative, problem-solution structure, architecture diagrams, production evidence, and honest cost analysis.

## When to Use

Use this skill when you need to:
- Document a complex technical architecture for Medium/blog publication
- Transform a working POC/implementation into a compelling technical narrative
- Explain engineering decisions with production evidence
- Generate professional diagrams with gpt-image-2

## Article Structure

### 1. Hero Section (Story-Driven Introduction)

**Pattern:** Introduce a relatable character facing the core problem.

**Example:** Marcus at 3:14 AM watching OAuth fail. Sarah watching users repeat context.

**Components:**
- Character name + situation (specific time/place)
- Initial success → Production ask → Impossible reality
- Core problem statement (bold, one sentence)
- What the broken architecture looked like
- Preview of the 3-4 main problems
- Solution teaser: the architecture that changed everything
- Implementation stats (e.g., "36 scenarios covered, 6 weeks iteration")

**Image 1 - Hero:** Architecture overview showing all major components (1792x1024, landscape)
*Caption format:* "Component A, Component B, and Component C coordinating through [pattern]."

**Image 2 - Broken State:** Traditional approach showing the problem (1792x1024)
*Caption format:* "The broken traditional approach: [what's wrong]."

### 2. Problem Sections (3-4 Problems)

Each problem follows the pattern:

**Problem Statement:** Clear title - "Problem N: The [Descriptive Name]"

**Narrative:** Story showing how the problem manifests in production.

**Traditional Approach:** Numbered steps showing broken flow.

**Core Issue (bold):** "You can't debug it. You can't audit it." (make it visceral)

**Image - Broken Flow:** Diagram showing traditional broken approach

**Solution Preview:** AgentCore's answer (deceptively simple statement)

**Image - Clean Solution:** Diagram showing the fixed architecture

**Code Snippet:** Real implementation code (10-30 lines) showing the fix

**Format:**
```python
# Context comment
def actual_function():
    # Real implementation
    pass
```

### 3. Architecture Deep Dive

**Pattern:** "The Solution in One Picture" → comprehensive architecture diagram

**Components:**
- Layer-by-layer breakdown
- Each layer gets: name, responsibility, what it does NOT do
- "Together, these N components produce a system that is [qualities]."

**Image - Full Architecture:** Complete system diagram (1792x1024)
*Caption:* "Complete architecture: [layers listed with their responsibilities]."

**Subsection - Internal Flow:**
- Step-by-step lifecycle explanation
- Timing details (e.g., "async extraction ~90s")
- What happens behind the scenes

**Image - Sequence Diagram:** Flow with timing annotations (1024x1792, portrait)
*Caption:* "Complete sequence: [steps with timing]."

**Code Snippet - Infrastructure:** CDK/Terraform showing deployment

### 4. Production Flow with Real Evidence

**Pattern:** "Proof: a Real [Type] Flow"

**Components:**
- Actual user input (blockquote)
- Real API response (JSON with evidence fields)
- Timing annotations (t0, t90, t100)
- Behind-the-scenes explanation
- Model answer (blockquote)

**Image - Production Trace:** Real flow with request IDs and latencies (1792x1024)
*Caption:* "Real production trace: [flow summary with timing]."

**Evidence source:** Reference actual files (e.g., `evidence/e2e/file.json`)

**Test coverage statement:** "Our test suite covers N scenarios: [list types]. All N pass before every deploy."

### 5. What This Costs: The Honest Tradeoffs

**Pattern:** "No architecture is free. If someone tries to sell you one that is, walk away."

**Components:**
- Real numbers (latency p95, storage costs, timing delays)
- Operational complexity (N services, deploy pipelines, IAM roles)
- Specific failure modes (e.g., "token refresh races", "consent denial 4-7%")

**Image - Tradeoffs Infographic:** Costs + when to use/not use (1792x1024)
*Caption:* "Real costs: [list 3-4 key tradeoffs], when to use vs skip."

**Format:**
```
**Cost Category.** Description with specifics. 
In our setup (region, scale), p95 sits around NNNms. 
Your numbers will vary with [factors].
```

**When NOT to use:** Bulleted list (3-4 items)
**When to use:** Bulleted list (3-4 items)

**Closing:** "These are the price of the guarantees. None is a dealbreaker. All of them matter on day 30."

### 6. Five Things We Got Wrong

**Pattern:** Numbered mistakes (1-5) with specific fixes

**Format per mistake:**
```
**N. We [what we did wrong].** Consequence. 
Fix: [specific change with technical detail].
```

**Optional Image - Mistakes Infographic:** Red X → Green check pattern (1792x1024)

**Tone:** Honest, production-learned, specific (not generic "we learned to test better")

### 7. Conclusion

**Pattern:** "[Character] Ships"

**Components:**
- Time reference ("That was N weeks ago")
- Today's state: "runs in production with real enterprise users"
- Security/compliance approval
- CTO's new questions (showing scale)
- What's left after iteration (bulleted list, 4 items)

**Call to Action:**
```
> So here's the question: which [problem] have you been avoiding?

Build this for that one. The next five [things] become hours of work, not months.
```

**Future-proofing statement:** "Whatever comes after [Service] (and something always does), the pattern of [core principles] outlives any specific AWS service."

**Closing:** "If you try it, come back and tell us what broke on day 30. That's where the real architecture lives."

**References:** Links to AWS docs, GitHub repos, related tutorials

**Services Used:** Bulleted list of AWS services

**Design Qualities:** Bulleted list of architectural guarantees

## Image Generation Pattern (10-12 images)

### Required Images (10 minimum)

1. **Hero** (1792x1024): Full architecture overview
2. **Broken State** (1792x1024): Traditional approach showing problem
3. **Problem 1 Diagram** (1792x1024): Specific failure mode
4. **Problem 2 Diagram** (1792x1024): Coordination failure
5. **Problem 3 Diagram** (1024x1792): Strategy/flow decision
6. **Architecture** (1792x1024): 3-4 layer complete system
7. **Sequence Diagram** (1024x1792): Flow with timing
8. **Production Trace** (1792x1024): Real evidence with request IDs
9. **Tradeoffs Infographic** (1792x1024): Costs + when to use
10. **Mistakes (Optional)** (1792x1024): Before/after red X → green check

### Image Style Guidelines

**Consistency:**
- White or light gray backgrounds (NEVER black)
- Enterprise professional style
- Minimal modern design
- High contrast
- Clean sans-serif typography
- Organized grid/flow layout

**Colors:**
- Success: Green (#00AA00)
- Warning/Cost: Orange (#FF8800)
- Error/Broken: Red (#CC0000)
- Primary components: Purple, Cyan, Blue
- Data stores: Green cylinder
- Arrows: Blue/Cyan for success, Red for broken

**Text in Images:**
- Labels: Bold sans-serif
- Component names: Title case
- Arrows: Verb phrases ("CreateEvent", "Retrieve")
- Timing: Explicit numbers ("90s", "150ms")

### gpt-image-2 Prompts

**Hero/Architecture prompts:**
```
Professional enterprise architecture diagram showing [components]. 
LEFT: [Component A] with [icon/label]. 
CENTER: [Component B] with [features]. 
RIGHT: [Component C] with [capabilities]. 
[Data flow description]. 
Clean white background, modern enterprise infographic style, 
minimal flat design, sharp clean lines, high contrast, organized layout.
```

**Sequence diagram prompts:**
```
Professional sequence diagram showing [flow] with timing. 
LEFT SIDE: Actor boxes for [participants]. 
VERTICAL TIMELINE with numbered steps: 
1. [Step] at t0. 2. [Step]. 3. [Async box spanning t0-t90]. 
4. [Step] at t100. 
Clean white background, professional UML sequence style, 
blue/green arrows, timing annotations.
```

**Infographic prompts:**
```
Professional infographic showing [topic]. 
FOUR BOXES LAYOUT: TOP LEFT: [Item 1]. TOP RIGHT: [Item 2]. 
BOTTOM LEFT: [Item 3]. BOTTOM RIGHT: [Item 4 with comparison]. 
Clean white background, professional infographic style, 
[color scheme], organized grid.
```

### API Call Pattern

```bash
cd docs/assets
export OPENAI_API_KEY="[key from .env]"

cat > /tmp/openai_request.json << 'JSONEOF'
{
  "model": "gpt-image-2",
  "prompt": "[detailed prompt from above]",
  "size": "1792x1024",
  "n": 1
}
JSONEOF

curl -s -X POST https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/openai_request.json > /tmp/openai_response.json

python3 -c "
import json, base64
with open('/tmp/openai_response.json') as f:
    data = json.load(f)
if 'error' in data:
    print(f'ERROR: {data[\"error\"][\"message\"]}')
    exit(1)
img_data = data['data'][0]['b64_json']
with open('filename.png', 'wb') as f:
    f.write(base64.b64decode(img_data))
print('✓ filename.png')
"
```

**Critical:** gpt-image-2 returns `b64_json` (base64 encoded), NOT `url`.

## Caption Format

### Markdown
```markdown
![Alt Text](assets/filename.png)
*Caption text describing what the image shows.*
```

### HTML
```html
<figure>
  <img src="assets/filename.png" alt="Alt Text">
  <figcaption>Caption text describing what the image shows.</figcaption>
</figure>
```

**Caption Guidelines:**
- Describe what's shown, not obvious facts
- Technical precision (component names, numbers)
- Active voice preferred
- One sentence, occasionally two
- Match reference article style

## Tone and Style

**Voice:** Technical but accessible. Senior engineer explaining to senior engineer.

**Sentence structure:** Mix short punchy sentences with longer explanatory ones.

**Bold for emphasis:** Core problems, impossibilities, what breaks.

**Repetition for impact:** "You can't debug it. You can't replay it. You can't audit it."

**Numbers are specific:** "210ms Gateway latency, 55ms Identity cached" not "low latency"

**Honest about problems:** "This is overkill for X. This is the right choice for Y."

**Story-driven but technical:** Marcus/Sarah facing real problems, not abstract concepts.

**Production over theory:** Real logs, real evidence files, real test counts.

## Reference Examples

**AgentCore Identity Article:** `/Users/john.ruiz/.claude/worktrees/agentcore-identity/feat-auth-atlassian/docs/medium-article-agentcore-refined.md`

**AgentCore Memory Article:** `/Users/john.ruiz/.claude/worktrees/cost-optimization-bedrock-agents/feat-agentic-memory/docs/medium-article-agentic-memory.md`

## Workflow

1. **Analyze codebase:** Read README, implementation files, evidence logs
2. **Structure problems:** Identify 3-4 core problems the system solves
3. **Write hero section:** Create story character, show problem
4. **Generate images 1-2:** Hero + broken state
5. **Write problem sections:** One section per problem with images + code
6. **Generate images 3-5:** Problem diagrams
7. **Write architecture section:** Deep dive with lifecycle explanation
8. **Generate images 6-7:** Architecture + sequence
9. **Write production section:** Real evidence with timing
10. **Generate image 8:** Production trace
11. **Write tradeoffs section:** Honest costs + when to use
12. **Generate image 9:** Tradeoffs infographic
13. **Write mistakes section:** 5 numbered production lessons
14. **Generate image 10 (optional):** Mistakes infographic
15. **Write conclusion:** Character ships, call to action
16. **Create HTML version:** Convert markdown with figcaptions
17. **Verify:** 10 images, 10 captions in markdown, 10 figcaptions in HTML

## Success Criteria

- [ ] Story-driven hero section with relatable character
- [ ] 3-4 problem sections with broken → fixed pattern
- [ ] Architecture deep dive with lifecycle explanation
- [ ] Production evidence with real logs/timing
- [ ] Honest tradeoffs with specific numbers
- [ ] Five mistakes with specific fixes
- [ ] Conclusion with call to action
- [ ] 10-12 professional images (white backgrounds)
- [ ] All images have captions (markdown + HTML synchronized)
- [ ] Code snippets are real implementation code
- [ ] Tone matches reference articles (honest, technical, story-driven)

## Common Mistakes to Avoid

❌ Generic problem descriptions ("memory is hard")  
✅ Specific production failure modes ("user repeats context 5 times")

❌ Black backgrounds on diagrams  
✅ White/light backgrounds only

❌ Vague tradeoffs ("it's slower")  
✅ Specific numbers ("p95 150ms retrieval latency")

❌ Generic lessons ("we learned to test")  
✅ Specific fixes ("changed from topK=5 to topK=6 after testing")

❌ Abstract architecture diagrams  
✅ Real component names, API calls, code snippets

❌ Marketing tone ("amazing", "revolutionary")  
✅ Engineering tone ("deceptively simple", "honest tradeoffs")

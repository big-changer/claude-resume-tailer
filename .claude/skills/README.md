# Claude Skills - Resume Generator Suite

**Shareable Claude skills for the resume-generator project.**

---

## 📦 Available Skills

### Resume-JD Optimizer
**File**: `resume-jd-optimizer.md`

Complete resume optimization skill that analyzes job descriptions and master resumes, then generates ATS-optimized resumes with strategic keyword emphasis.

**What it does:**
- Analyzes job descriptions to extract requirements and keywords
- Parses master resumes to identify relevant experience
- Identifies gaps and asks for clarification
- Generates ATS-optimized content (summaries, competencies, skills, achievements)
- Applies strategic keyword emphasis (Phase 5.5)
- Outputs production-ready Markdown resumes

**Input:**
- `input/jd.txt` - Job description
- `input/master-resume.md` - Master resume

**Output:**
- `output_{YYYYMMDD}/{company}-{position}-{name}-emphasize.md`
- Optimized resume with ATS keyword emphasis

**Key Features:**
- ✅ 7-phase optimization workflow
- ✅ Role-specific optimization (Frontend/Backend/DevOps/AI/Mobile)
- ✅ ATS-optimized keyword placement
- ✅ Strategic keyword emphasis (bold MUST-HAVE keywords)
- ✅ Achievement quantification and reordering
- ✅ Intelligent certificate generation
- ✅ 100% factual integrity
- ✅ Complete transparency (AI-generated content marked)

**Research-backed:**
All recommendations are based on current ATS research (2024-2026):
- Modern ATS use ML for contextual relevance scoring
- Quantified metrics score higher (parsed as structured data)
- Keywords naturally integrated (1-3 times max) work better than stuffing
- Strategic formatting improves both ATS and human recruiter assessment

---

## 🚀 How to Use

### Option 1: Direct Prompt
```
1. Open resume-jd-optimizer.md
2. Copy the IMPLEMENTATION PROMPT section
3. Paste as system prompt in Claude
4. Provide your job description and master resume
5. Get optimized resume with keyword emphasis
```

### Option 2: Formal Skill Setup
```
1. Copy resume-jd-optimizer.md to your project's skills directory
2. Configure input/output paths
3. Users invoke via `/run-resume-optimizer` or similar
4. Automated 7-phase processing
```

### Option 3: Team/Partner Sharing
```
1. Share the entire .claude/skills_v2 directory
2. Partners can copy to their projects
3. Use with any master resume + job description
4. No additional setup needed
```

---

## 📋 Skill File Structure

Each skill file includes:
- **Overview**: What it does and key features
- **Quick Start**: For users and developers
- **Implementation Prompt**: Complete system prompt (copy this)
- **7-Phase Workflow**:
  1. Job Description Analysis
  2. Master Resume Parsing
  3. Gap Analysis & Matching
  4. Certification Handling
  5. Content Generation
  6. Phase 5.5: ATS-Critical Keyword Emphasis ⭐
  7. Quality Assurance & Output
- **Edge Cases**: Handling for special scenarios
- **Success Indicators**: Quality metrics
- **Quick Reference**: Examples by role type

---

## 🎯 Phase 5.5: ATS-Critical Keyword Emphasis (Unique Feature)

Strategically bolds MUST-HAVE keywords from the job description for:
- **ATS Systems**: Keywords remain parseable; bold is formatting only
- **Recruiters**: Can assess fit in 30-45 seconds (visual scanning)
- **Candidates**: Interview prep guide (know what to emphasize)
- **Professional Look**: Strategic emphasis, not forced or desperate

Uses three-tier keyword system:
- **TIER 1 (Always Bold)**: Primary language, core platform, essential methodology
- **TIER 2 (Selective Bold)**: Secondary technologies, testing frameworks
- **TIER 3 (Don't Bold)**: Nice-to-have skills, generic terms

---

## 📖 Quick Reference: Role-Specific Keywords

### Frontend Engineer
```
Keywords to Emphasize:
React, Next.js, TypeScript, Tailwind CSS, Web Vitals, 
Accessibility, Jest, Playwright
```

### Backend Engineer
```
Keywords to Emphasize:
Go/Python/Java, PostgreSQL, Redis, gRPC, microservices, 
REST APIs, CI/CD, Docker, Kubernetes
```

### DevOps/SRE
```
Keywords to Emphasize:
Kubernetes, Terraform, Prometheus, Grafana, incident response,
SLO/SLI, CI/CD, Infrastructure as Code
```

### AI/LLM Engineer
```
Keywords to Emphasize:
LangChain, LLamaIndex, RAG, Vector Databases, Prompt Engineering,
LLM Evaluation, Fine-tuning
```

---

## ✨ Example Workflow

### Input Files
**input/jd.txt:**
```
Software Developer
Cap Index
Exton, PA • Remote

CAP Index is looking for a software developer with a strong backend foundation.
You should have experience with C#, .NET, React, SQL Server, and PostgreSQL.
```

**input/master-resume.md:**
```
[Complete master resume with all skills, experience, education]
```

### Skill Execution
```
Phase 1: Analyzes JD → Extracts keywords, requirements
Phase 2: Parses resume → Identifies relevant experience
Phase 3: Gap analysis → Flags missing skills/metrics
Phase 4: Certifications → Handles missing certs
Phase 5: Content generation → Optimizes content sections
Phase 5.5: Keyword emphasis → Bolds critical keywords ⭐
Phase 6: QA → Verifies compliance and accuracy
Phase 7: Output → Saves optimized resume
```

### Output Resume
```
# John Doe
**Senior .NET Software Engineer**

## PROFESSIONAL SUMMARY
Full-stack software engineer with 8+ years specializing in **backend systems**, 
**microservices architecture**, and containerized deployments. Proficient in **C#**, 
**.NET Core**, **React**, and **TypeScript**...

## CORE COMPETENCIES
**Backend & Full-Stack**: **C#**, **.NET Core**, **ASP.NET Core**, **Microservices**...
**Frontend**: **React**, **TypeScript**, JavaScript...
**DevOps & Infrastructure**: **Docker**, **Kubernetes**, **CI/CD**...

## PROFESSIONAL EXPERIENCE
- Architected full-stack **.NET Core microservices** platform...
[...rest of optimized resume with strategic emphasis...]
```

---

## 🔍 Quality Assurance

Each optimized resume is verified for:
- ✅ ATS compliance (simple formatting, no graphics)
- ✅ Keyword coverage (all MUST-HAVE keywords included)
- ✅ Factual accuracy (100% matches master resume)
- ✅ Achievement quantification (80%+ of bullets quantified)
- ✅ Professional appearance (emphasis is balanced and intentional)
- ✅ Production-ready (safe to submit to real jobs)

---

## 📊 Research Foundation

Based on current ATS research (2024-2026):

**Modern ATS Evolution:**
- Uses machine learning for contextual relevance scoring
- Detects keyword manipulation/stuffing (triggers penalties)
- Quantified metrics score higher (parsed as structured data)
- Semantic understanding of job relevance (related terms matter)

**Best Practices:**
- Simple formatting (Arial/Calibri, no graphics, no complex layouts)
- Plain text technical skills (comma-separated, optimal for parsing)
- Consistent date format (MM/YYYY)
- Standard bullet points, contact info in body
- Keywords naturally integrated (1-3 times, not stuffed)

**Sources:**
- [Scale.jobs ATS Algorithms](https://scale.jobs/blog/understanding-ats-scoring-algorithms)
- [ATS Resume Optimization 2025](https://scale.jobs/ats-resume-optimization-guide)
- [JobWizard Keywords](https://jobwizard.ai/blog/ats-resume-keywords-for-software-engineers)

---

## ⚙️ Setup for Your Team

### 1. Copy Skills Directory
```bash
# Copy .claude/skills_v2 to your project or share with partners
cp -r .claude/skills_v2 /path/to/partner/project/.claude/
```

### 2. Use in Claude Code
```
1. Open Claude Code
2. Load the skill file as a system prompt
3. Provide your inputs (JD + master resume)
4. Run the 7-phase optimization
5. Get optimized resume with emphasis
```

### 3. Or Integrate into Your App
```
1. Use the implementation prompt in your application
2. Accept JD + master resume as inputs
3. Process through 7 phases
4. Output optimized resume + metadata
```

---

## 🤝 Sharing with Partners

**What to Share:**
- Copy entire `.claude/skills_v2` directory
- Include this README.md file
- Partners can use immediately

**What Partners Need:**
- Job description file (`input/jd.txt`)
- Master resume file (`input/master-resume.md`)
- Claude access (through API or Claude.ai)

**Output:**
- Optimized resume ready for submission
- All keywords strategically emphasized
- Production-ready Markdown file

---

## 📝 Example: Evan Singleton → Cap Index

**Test case completed:**
- Master Resume: Evan Singleton (blockchain specialist)
- Job Description: Cap Index Software Developer (.NET/React role)
- Output: Fully optimized resume with emphasis applied
- Result: 86% skill match coverage (trainable gaps only)

See `output_20260722/cap-index-software-developer-evan-singleton-emphasize.md` for example.

---

## ✅ Constraints & Best Practices

### Never
- ✗ Fabricate experience or dates
- ✗ Claim skills without confirmation
- ✗ Use keyword stuffing or manipulation
- ✗ Hide content or use formatting tricks
- ✗ Oversell or exaggerate achievements

### Always
- ✓ Ask before adding new information
- ✓ Mark AI-generated content clearly
- ✓ Maintain 100% factual accuracy
- ✓ Keep career narrative authentic
- ✓ Use quantified metrics when possible

---

## 📞 Support & Questions

**How to use with your resume:**
1. Prepare master resume (all skills, all experience)
2. Find target job description
3. Save as `input/jd.txt` and `input/master-resume.md`
4. Run the skill
5. Review optimized resume
6. Customize if desired
7. Convert to PDF and submit

**Best Results:**
- Comprehensive master resume (don't omit skills)
- Clear job description (use full job posting)
- Honest feedback on gaps and metrics
- Review before submitting to real jobs

---

## 📦 Files in This Directory

```
.claude/skills_v2/
├── resume-jd-optimizer.md (The main skill - 1,500+ lines)
├── README.md (This file - quick reference and setup guide)
└── manifest.json (Optional - metadata for tool compatibility)
```

---

**Ready to optimize resumes?** Start with `resume-jd-optimizer.md` and your job description!

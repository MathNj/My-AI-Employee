# LinkedIn Post Templates

Complete library of post templates with examples and usage guidance.

## How to Use Templates

### Command Line
```bash
python generate_post.py --template achievement \
    --achievement "Completed Bronze Tier AI Employee" \
    --impact "24/7 automated task processing"
```

### Via Claude Code
Simply ask:
- "Create a LinkedIn post about [achievement]"
- "Post to LinkedIn celebrating [milestone]"
- "Share [insight] on LinkedIn"

Claude will automatically select the appropriate template.

---

## Template Library

### 1. Achievement Post

**Use for:** Celebrating completed projects, milestones, wins

**Template:**
```
🎉 Excited to share: {achievement}!

{details}

Impact: {impact}

{call_to_action}
```

**Variables:**
- `achievement` - What you accomplished
- `details` - Additional context (1-2 sentences)
- `impact` - Measurable result or benefit
- `call_to_action` - Engagement question (optional)

**Example:**
```
🎉 Excited to share: Completed Bronze Tier AI Employee system!

Built an autonomous agent using Claude Code and Obsidian that monitors
files and emails 24/7, processes tasks automatically, and maintains
full audit logs.

Impact: Saves 10+ hours per week on routine task management

What automation projects are you working on?

#Achievement #BusinessGrowth #AIAutomation
```

**Usage:**
```bash
python generate_post.py --template achievement \
    --achievement "Completed Bronze Tier AI Employee system" \
    --details "Built autonomous agent with Claude Code and Obsidian" \
    --impact "Saves 10+ hours per week"
```

---

### 2. Service Announcement

**Use for:** Launching new services, announcing features, promoting offerings

**Template:**
```
🚀 Introducing: {service}

{description}

Key benefits:
{benefit}

{call_to_action}
```

**Variables:**
- `service` - Name of service/product
- `description` - What it does (2-3 sentences)
- `benefit` - Main benefits (can be bullet points)
- `call_to_action` - How to learn more

**Example:**
```
🚀 Introducing: Personal AI Employee Automation

An autonomous system that manages your business tasks 24/7 using
Claude Code and Obsidian. Monitors emails, processes files, creates
action plans, and handles approvals automatically.

Key benefits:
• Save 20+ hours/week on routine tasks
• 24/7 monitoring and processing
• Human-in-the-loop for critical decisions
• Complete audit trail

Interested? Drop a comment or DM to learn more!

#NewService #BusinessAutomation #Innovation
```

**Usage:**
```bash
python generate_post.py --template service \
    --service "Personal AI Employee Automation" \
    --description "Autonomous system managing business tasks 24/7" \
    --benefit "Save 20+ hours/week, 24/7 monitoring, HITL for decisions"
```

---

### 3. Thought Leadership

**Use for:** Sharing insights, industry trends, expert opinions

**Template:**
```
💡 {topic}

My take: {insight}

{elaboration}

{question}
```

**Variables:**
- `topic` - Subject you're discussing
- `insight` - Your main point/opinion
- `elaboration` - Supporting details (2-3 sentences)
- `question` - Engagement question

**Example:**
```
💡 The Future of Work: AI Employees in 2026

My take: Personal AI employees will be as common as smartphones by 2027.

We're seeing a shift from "AI assistants" to "AI employees" - autonomous
agents that don't just answer questions but proactively manage entire
workflows. The barrier to entry is dropping fast with tools like Claude
Code making it accessible to anyone who can write prompts.

What's your perspective on AI autonomy in business?

#ThoughtLeadership #FutureOfWork #AIAutomation
```

**Usage:**
```bash
python generate_post.py --template thought-leadership \
    --topic "The Future of Work: AI Employees in 2026" \
    --insight "Personal AI employees will be common by 2027" \
    --elaboration "Shift from assistants to autonomous agents..."
```

---

### 4. Behind The Scenes

**Use for:** Showing your process, humanizing your brand, building connection

**Template:**
```
👀 Behind the scenes: {activity}

{description}

{insight}

{engagement_question}
```

**Variables:**
- `activity` - What you're working on
- `description` - What's happening (2-3 sentences)
- `insight` - Learning or interesting finding
- `engagement_question` - Ask for others' experiences

**Example:**
```
👀 Behind the scenes: Building an AI Employee from scratch

Spent the weekend setting up watcher scripts, approval workflows,
and agent skills. The trickiest part? Getting the OAuth flows
working for Gmail and LinkedIn APIs.

Key learning: Start with the simplest version that works, then add
complexity. My first version had 3 files. Now it's a full system
with 9 agent skills and multiple integrations.

How do you approach building complex systems?

#BehindTheScenes #WorkCulture #BuildInPublic
```

---

### 5. Engagement Post

**Use for:** Driving comments, starting discussions, polls

**Template:**
```
❓ Question for my network: {question}

{context}

{options}

Drop your thoughts in the comments! 👇
```

**Variables:**
- `question` - Your question
- `context` - Why you're asking (1-2 sentences)
- `options` - Possible answers (optional)

**Example:**
```
❓ Question for my network: What's your biggest time sink at work?

I'm researching automation opportunities for small businesses.
Curious what tasks consume the most time but feel "automatable."

Some common answers:
• Email management
• Data entry & reporting
• Scheduling & calendar
• Social media posting
• Invoice processing

Drop your thoughts in the comments! 👇

#CommunityEngagement #Discussion #Productivity
```

---

### 6. Case Study / Results

**Use for:** Sharing success stories, demonstrating ROI, proving concept

**Template:**
```
📊 Case Study: {title}

Challenge: {challenge}

Solution: {solution}

Results: {results}

{takeaway}
```

**Variables:**
- `title` - Case study name
- `challenge` - Problem to solve
- `solution` - How you solved it
- `results` - Measurable outcomes
- `takeaway` - Key learning

**Example:**
```
📊 Case Study: Automating Business Task Management

Challenge: Spending 15+ hours/week on routine tasks like email
triage, file processing, and status updates. Needed solution that
wouldn't break the bank.

Solution: Built Personal AI Employee using Claude Code (existing
subscription) and Obsidian (free). Implemented watchers for Gmail
and filesystem, approval workflows, and scheduled tasks.

Results:
• 80% reduction in manual task time
• Zero tasks missed or forgotten
• Complete audit trail
• $0 additional monthly cost

Key learning: The best automation is the one you actually build.
Start small, iterate quickly, and focus on your actual workflows.

#CaseStudy #Results #BusinessAutomation
```

---

### 7. Quick Tip

**Use for:** Sharing actionable advice, productivity hacks, lessons learned

**Template:**
```
💡 Quick tip: {tip_title}

{tip_content}

Why it works: {reason}

Try it this week and let me know how it goes!
```

**Example:**
```
💡 Quick tip: The 2-Minute Rule for Task Processing

If a task takes less than 2 minutes, do it immediately instead
of adding it to your todo list. The overhead of tracking,
remembering, and context-switching costs more than just doing it.

Why it works: Reduces cognitive load and prevents small tasks
from piling up into an overwhelming backlog.

Try it this week and let me know how it goes!

#ProductivityTip #QuickWin #TimeManagement
```

---

### 8. Business Milestone

**Use for:** Company growth, team achievements, anniversaries

**Template:**
```
🎯 Milestone achieved: {milestone}!

When we started: {starting_point}

Where we are now: {current_state}

Grateful for: {gratitude}

{future_outlook}
```

**Example:**
```
🎯 Milestone achieved: 1000 followers on LinkedIn!

When we started: Sharing automation tips with just friends
and colleagues 6 months ago.

Where we are now: A community of builders, entrepreneurs, and
automation enthusiasts sharing knowledge daily.

Grateful for: Every comment, share, and conversation. Your
engagement and feedback have shaped how we approach automation.

Excited for what's next! Planning to share more in-depth case
studies and tutorials. What topics would you like to see?

#Milestone #BusinessGrowth #Gratitude
```

---

## Template Selection Guide

### Based on Content Type

| Content Type | Recommended Template |
|--------------|---------------------|
| Completed project | Achievement |
| New offering | Service Announcement |
| Industry insight | Thought Leadership |
| Work process | Behind The Scenes |
| Question to network | Engagement |
| Client success | Case Study |
| Quick advice | Quick Tip |
| Company growth | Business Milestone |

### Based on Goal

| Goal | Recommended Template |
|------|---------------------|
| Build authority | Thought Leadership, Case Study |
| Drive engagement | Engagement, Quick Tip |
| Generate leads | Service Announcement, Case Study |
| Build connection | Behind The Scenes, Engagement |
| Celebrate wins | Achievement, Business Milestone |

### Based on Audience

| Audience | Recommended Templates |
|----------|---------------------|
| Entrepreneurs | Case Study, Quick Tip, Achievement |
| Potential clients | Service Announcement, Case Study |
| Industry peers | Thought Leadership, Behind The Scenes |
| General network | Engagement, Achievement, Quick Tip |

---

## Best Practices

### Length
- **Optimal:** 150-300 characters (best engagement)
- **Maximum:** 3000 characters (LinkedIn limit)
- **Sweet spot:** 200-250 characters

### Formatting
- Use emojis strategically (1-2 per post)
- Break into short paragraphs (2-3 lines max)
- Use bullet points for lists
- Add whitespace for readability

### Hashtags
- Use 3-5 relevant hashtags
- Mix broad (#BusinessAutomation) and specific (#ClaudeCode)
- Place at end of post
- First 3 hashtags are most important

### Call-to-Action
- Ask a question (drives comments)
- Request specific action (share, follow, DM)
- Make it easy to respond
- Be authentic, not salesy

### Timing
- **Best days:** Tuesday, Wednesday, Thursday
- **Best times:** 9 AM - 12 PM local time
- **Worst times:** Weekends, late evenings
- **Frequency:** 3-5 posts per week

---

## Customization

### Adding Your Own Templates

Edit this file and add new templates following this structure:

```markdown
### Template Name

**Use for:** When to use this template

**Template:**
```
Your template with {variables}
```

**Variables:**
- `variable_name` - Description

**Example:**
```
Filled example
```

**Usage:**
```bash
Command to generate
```
```

Then add to `generate_post.py` TEMPLATES dict.

### Template Variables

Common variables across templates:
- `{achievement}` - What was accomplished
- `{details}` - Additional context
- `{impact}` - Measurable result
- `{call_to_action}` - Engagement prompt
- `{question}` - Discussion question
- `{insight}` - Key takeaway
- `{topic}` - Subject matter

---

## Examples by Industry

### For Consultants
- Focus on: Case studies, Quick tips, Thought leadership
- Highlight: Results, expertise, frameworks
- Avoid: Overly promotional content

### For Entrepreneurs
- Focus on: Behind the scenes, Milestones, Achievements
- Highlight: Journey, learnings, authenticity
- Avoid: Fake success stories

### For Service Providers
- Focus on: Service announcements, Case studies, Quick tips
- Highlight: Value delivered, customer success
- Avoid: Feature lists without benefits

---

**Need help?** Review the examples above or ask Claude Code to generate a post for your specific situation.

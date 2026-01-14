# Social Media Templates Library

Complete template library for all platforms with variables and examples.

## Template Structure

Each template includes:
- **Name**: Template identifier
- **Use Case**: When to use this template
- **Variables**: Required and optional fields
- **Platform Versions**: Customized for LinkedIn, Facebook, Instagram, Twitter/X
- **Best Times**: Recommended posting schedule

---

## 1. Achievement Post Template

**Use When:**
- Company milestones reached
- Awards or recognition received
- Growth metrics to celebrate
- Team accomplishments

**Variables:**
- `achievement` (required): What was accomplished
- `impact` (required): Quantifiable result or impact
- `team_shoutout` (optional): Team member or department to recognize
- `cta` (optional): Call-to-action

### LinkedIn Version (Professional)

```markdown
Exciting news! We've just {achievement}! 🎉

This milestone represents {impact} and demonstrates our commitment to delivering exceptional value to our clients.

{team_shoutout ? `Huge congratulations to ${team_shoutout} for making this possible.` : ''}

We're grateful to every customer who believed in our vision. This is just the beginning!

{cta ? cta : 'Learn more about our journey →'}

#Achievement #BusinessGrowth #Milestone #Success
```

**Example:**
```
Exciting news! We've just reached 1,000 customers! 🎉

This milestone represents 300% growth in just 6 months and demonstrates our commitment to delivering exceptional value to our clients.

Huge congratulations to our engineering team for making this possible.

We're grateful to every customer who believed in our vision. This is just the beginning!

Learn more about our journey → [link]

#Achievement #BusinessGrowth #Milestone #Success
```

### Facebook Version (Celebratory)

```markdown
🎊 BIG NEWS! 🎊

We just {achievement}!

{impact} - and we couldn't have done it without YOU! Every single one of our amazing customers made this possible.

{team_shoutout ? `Special shoutout to ${team_shoutout} 👏` : ''}

Thank you for being part of our journey! Here's to the next milestone! 🚀

{cta}

#Milestone #ThankYou #CustomerLove
```

### Instagram Version (Visual + Brief)

```markdown
{achievement}! 🎉🎉🎉

{impact} and we're just getting started! 💪

Your trust means everything. Thank you! 💙

{team_shoutout ? `📸 Celebrating with ${team_shoutout}` : ''}

[Image: Team celebration, milestone graphic, or achievement visualization]

#Milestone #Achievement #Success #Growth #ThankYou #Celebrate #TeamWork #Business #Entrepreneur #SmallBusiness
```

### Twitter/X Version (Concise)

```markdown
🎉 {achievement}!

{impact in 1 line}

{team_shoutout ? `Thanks to ${team_shoutout}!` : 'Thanks to our amazing team!'}

This is just the beginning! 🚀

#Milestone #Success
```

**Best Times:**
- LinkedIn: Tuesday-Thursday 9-11 AM
- Facebook: Wednesday 2 PM
- Instagram: Wednesday 12 PM
- Twitter/X: Wednesday 9 AM

---

## 2. Service Announcement Template

**Use When:**
- Launching new products or features
- Announcing service updates
- Introducing new offerings
- Price changes or promotions

**Variables:**
- `service_name` (required): Name of product/service
- `key_benefit` (required): Main value proposition
- `features` (optional): List of key features
- `availability` (optional): Launch date or availability
- `cta_link` (required): Call-to-action URL

### LinkedIn Version

```markdown
Introducing {service_name}! 🚀

We're excited to announce our latest solution designed to help businesses {key_benefit}.

**Key Features:**
{features ? features.map(f => `• ${f}`).join('\n') : ''}

{availability ? `Available starting ${availability}.` : 'Available now.'}

This represents months of development and customer feedback. We can't wait for you to try it!

{cta_link}

#ProductLaunch #Innovation #BusinessSolutions #Technology
```

### Facebook Version

```markdown
📢 New Release Alert! 📢

Say hello to {service_name}! ✨

{key_benefit} - it's been built with your needs in mind.

{availability ? `Launching ${availability}!` : 'Available RIGHT NOW!'}

{features ? `What you'll love:\n${features.map(f => `✅ ${f}`).join('\n')}` : ''}

Ready to transform how you work? Check it out! 👇

{cta_link}

#NewProduct #Launch #Innovation
```

### Instagram Version

```markdown
NEW: {service_name}! 🚀✨

{key_benefit in 1 sentence} 💡

{availability ? `Coming ${availability}` : 'Available NOW'}

Tap the link in bio to learn more! 👆

[Image: Product screenshot, demo, or promotional graphic]

#NewProduct #ProductLaunch #Innovation #Business #Technology #Startup #Entrepreneur #LaunchDay #NewRelease #ComingSoon
```

### Twitter/X Version

```markdown
🚀 Introducing {service_name}!

{key_benefit in 1 line}

{availability ? `Launching ${availability}` : 'Available now'}

{cta_link}

#ProductLaunch #Innovation
```

---

## 3. Customer Success Story Template

**Use When:**
- Sharing testimonials
- Highlighting case studies
- Demonstrating ROI
- Building social proof

**Variables:**
- `customer_name` (required): Client name or "A leading company"
- `industry` (optional): Customer's industry
- `problem` (required): Challenge they faced
- `solution` (required): How you helped
- `result` (required): Measurable outcome
- `quote` (optional): Customer testimonial

### LinkedIn Version

```markdown
Customer Success Story: {customer_name} 🎯

{industry ? `As a ${industry} company, ` : ''}{customer_name} faced a common challenge: {problem}.

**The Solution:**
{solution}

**The Results:**
{result}

{quote ? `"${quote}" - ${customer_name}` : ''}

Ready to achieve similar results? Let's talk about how we can help your business succeed.

#CustomerSuccess #CaseStudy #Results #ROI #BusinessGrowth
```

### Facebook Version

```markdown
💪 Success Story Time!

Meet {customer_name} - they were struggling with {problem}.

We worked together to {solution}.

The results? {result} 📊

{quote ? `Here's what they said:\n"${quote}"` : ''}

Your success story could be next! Drop us a message 👇

#CustomerSuccess #Results #Testimonial
```

### Instagram Version

```markdown
Client Success: {customer_name} 🎉

Problem: {problem in 5 words} ❌
Solution: {solution in 5 words} ✅
Result: {result in 5 words} 📈

{quote ? `"${quote}"` : 'Another happy customer! 💙'}

[Image: Customer logo, results graphic, or testimonial card]

#CustomerSuccess #CaseStudy #Results #ClientLove #Testimonial #BusinessResults #Success #ClientStory #ROI #Happy
```

### Twitter/X Version

```markdown
💪 {customer_name} Case Study:

Problem: {problem in 1 line}
Result: {result in 1 line}

{quote ? `"${quote}"` : ''}

Your turn? Let's talk 👉 {link}

#CustomerSuccess
```

---

## 4. Thought Leadership Template

**Use When:**
- Sharing industry insights
- Establishing expertise
- Starting conversations
- Commenting on trends

**Variables:**
- `topic` (required): Industry trend or insight
- `perspective` (required): Your unique take
- `data` (optional): Supporting statistics
- `cta_question` (required): Engagement question

### LinkedIn Version

```markdown
{topic} 💭

Here's my take: {perspective}

{data ? `The numbers back this up: ${data}` : ''}

I've seen this play out firsthand with our clients. The companies that adapt early gain a significant competitive advantage.

**What I'm watching:**
• [Key factor 1]
• [Key factor 2]
• [Key factor 3]

{cta_question}

Looking forward to hearing your perspectives in the comments.

#ThoughtLeadership #IndustryInsights #BusinessStrategy #Innovation
```

### Facebook Version

```markdown
Let's talk about {topic} 🗣️

{perspective}

{data ? `Did you know? ${data}` : ''}

I'm curious - {cta_question}

Drop your thoughts below! 👇

#BusinessTalk #IndustryInsights #Discussion
```

### Instagram Version

```markdown
💭 {topic}

{perspective in 2 sentences}

{data ? `📊 ${data}` : ''}

{cta_question}

Share your thoughts in comments! 👇

[Image: Quote graphic, infographic, or data visualization]

#ThoughtLeadership #Industry #Business #Insights #Opinion #Discussion #BusinessStrategy #Innovation #Trend #Future
```

### Twitter/X Version

```markdown
Hot take on {topic}:

{perspective in 2 lines}

{data ? `📊 ${data}` : ''}

{cta_question}

#ThoughtLeadership #Industry
```

---

## 5. Behind-the-Scenes Template

**Use When:**
- Showcasing company culture
- Humanizing your brand
- Building team connection
- Sharing process insights

**Variables:**
- `activity` (required): What's happening
- `team_member` (optional): Person to spotlight
- `insight` (required): What makes it interesting
- `fun_fact` (optional): Interesting tidbit

### LinkedIn Version

```markdown
Behind the Scenes: {activity} 🎬

{insight}

{team_member ? `Meet ${team_member}, who leads this initiative. Their dedication to excellence shows in every detail.` : 'Our team pours their heart into every project.'}

{fun_fact ? `Fun fact: ${fun_fact}` : ''}

This is what building something great looks like - one detail at a time.

What does "behind the scenes" look like at your company?

#CompanyCulture #BehindTheScenes #TeamWork #BuildingInPublic
```

### Facebook Version

```markdown
🎥 Behind the Scenes

Want to see what {activity} really looks like?

{insight}

{team_member ? `Shoutout to ${team_member} for making it happen! 👏` : ''}

{fun_fact ? `Fun fact: ${fun_fact} 😄` : ''}

This is the real work that goes into what we do!

#BTS #BehindTheScenes #TeamLife
```

### Instagram Version

```markdown
BTS: {activity} 🎬

{insight in 1 sentence}

{team_member ? `📸 Featuring ${team_member}` : ''}

{fun_fact ? `💡 ${fun_fact}` : ''}

[Image: Workspace photo, team in action, or process shot]

#BehindTheScenes #BTS #CompanyCulture #TeamLife #WorkLife #Team #Office #BuildingInPublic #Workplace #TeamWork
```

### Twitter/X Version

```markdown
🎬 BTS: {activity}

{insight in 1 line}

{team_member ? `Thanks to ${team_member}!` : ''}

{fun_fact ? `Fun fact: ${fun_fact}` : ''}

#BTS #TeamLife
```

---

## Template Usage Examples

### Example 1: Achievement Post

**Input Variables:**
```json
{
  "achievement": "reached $100K MRR",
  "impact": "300% growth in 6 months",
  "team_shoutout": "our engineering team",
  "cta": "Read our growth story →"
}
```

**Generated for LinkedIn:**
```
Exciting news! We've just reached $100K MRR! 🎉

This milestone represents 300% growth in 6 months and demonstrates our commitment to delivering exceptional value to our clients.

Huge congratulations to our engineering team for making this possible.

We're grateful to every customer who believed in our vision. This is just the beginning!

Read our growth story → [link]

#Achievement #BusinessGrowth #Milestone #Success
```

### Example 2: Service Announcement

**Input Variables:**
```json
{
  "service_name": "AutoFlow Pro",
  "key_benefit": "automate repetitive business tasks and save 10+ hours per week",
  "features": ["Smart automation engine", "Pre-built templates", "24/7 operation"],
  "availability": "January 15, 2026",
  "cta_link": "https://example.com/autoflow"
}
```

---

## Template Customization Guide

### Adding New Templates

1. Define clear use case
2. Identify required variables
3. Create platform-specific versions
4. Test with real data
5. Gather feedback and iterate

### Platform-Specific Tips

**LinkedIn:**
- Professional tone, 3-5 hashtags
- Include data and insights
- Ask thought-provoking questions

**Facebook:**
- Conversational, friendly tone
- Engage with questions
- Use emojis moderately

**Instagram:**
- Visual-first, brief text
- 10-30 relevant hashtags
- Strong call-to-action

**Twitter/X:**
- Ultra-concise, impactful
- 2-3 hashtags max
- Use threads for longer content

---

## Template Performance Tracking

Track these metrics per template:

- **Engagement Rate**: Likes + Comments + Shares / Impressions
- **Click-Through Rate**: Link clicks / Impressions
- **Conversion Rate**: Desired actions / Total engagement
- **Best Performing Platform**: Platform with highest engagement
- **Optimal Time**: Best posting time per platform

Update templates based on performance data quarterly.

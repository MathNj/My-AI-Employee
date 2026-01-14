#!/usr/bin/env python3
"""
Generate social media posts from templates

Usage:
    # Achievement post
    python generate_from_template.py --template achievement --data '{"achievement": "reached 1000 customers", "impact": "300% growth"}'

    # Service announcement
    python generate_from_template.py --template service --data '{"service_name": "AutoFlow Pro", "key_benefit": "automate tasks"}'

    # With specific platforms
    python generate_from_template.py --template achievement --data '{"achievement": "..."}' --platforms linkedin,facebook

    # Create approval request
    python generate_from_template.py --template achievement --data '{"achievement": "..."}' --create-approval
"""

import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Template definitions
TEMPLATES = {
    'achievement': {
        'name': 'Achievement Post',
        'description': 'Celebrate milestones, goals, and accomplishments',
        'required_vars': ['achievement', 'impact'],
        'optional_vars': ['team_shoutout', 'cta'],
        'platforms': {
            'linkedin': """Exciting news! We've just {achievement}! 🎉

This milestone represents {impact} and demonstrates our commitment to delivering exceptional value to our clients.

{team_shoutout}

We're grateful to every customer who believed in our vision. This is just the beginning!

{cta}

#Achievement #BusinessGrowth #Milestone #Success""",

            'facebook': """🎊 BIG NEWS! 🎊

We just {achievement}!

{impact} - and we couldn't have done it without YOU! Every single one of our amazing customers made this possible.

{team_shoutout}

Thank you for being part of our journey! Here's to the next milestone! 🚀

{cta}

#Milestone #ThankYou""",

            'instagram': """{achievement}! 🎉🎉🎉

{impact} and we're just getting started! 💪

Your trust means everything. Thank you! 💙

{team_shoutout}""",

            'twitter': """🎉 {achievement}!

{impact_short}

{team_shoutout_short}

This is just the beginning! 🚀

#Milestone #Success""",
        }
    },

    'service': {
        'name': 'Service Announcement',
        'description': 'Announce new products, features, or services',
        'required_vars': ['service_name', 'key_benefit'],
        'optional_vars': ['features', 'availability', 'cta_link'],
        'platforms': {
            'linkedin': """Introducing {service_name}! 🚀

We're excited to announce our latest solution designed to help businesses {key_benefit}.

{features}

{availability}

This represents months of development and customer feedback. We can't wait for you to try it!

{cta_link}

#ProductLaunch #Innovation #BusinessSolutions #Technology""",

            'facebook': """📢 New Release Alert! 📢

Say hello to {service_name}! ✨

{key_benefit} - it's been built with your needs in mind.

{availability}

{features}

Ready to transform how you work? Check it out! 👇

{cta_link}

#NewProduct #Launch""",

            'instagram': """NEW: {service_name}! 🚀✨

{key_benefit_short} 💡

{availability_short}

Tap the link in bio to learn more! 👆""",

            'twitter': """🚀 Introducing {service_name}!

{key_benefit_short}

{availability_short}

{cta_link}

#ProductLaunch #Innovation""",
        }
    },

    'customer_success': {
        'name': 'Customer Success Story',
        'description': 'Share testimonials and case studies',
        'required_vars': ['customer_name', 'problem', 'solution', 'result'],
        'optional_vars': ['industry', 'quote'],
        'platforms': {
            'linkedin': """Customer Success Story: {customer_name} 🎯

{industry_prefix}{customer_name} faced a common challenge: {problem}.

**The Solution:**
{solution}

**The Results:**
{result}

{quote}

Ready to achieve similar results? Let's talk about how we can help your business succeed.

#CustomerSuccess #CaseStudy #Results #ROI""",

            'facebook': """💪 Success Story Time!

Meet {customer_name} - they were struggling with {problem}.

We worked together to {solution}.

The results? {result} 📊

{quote}

Your success story could be next! Drop us a message 👇

#CustomerSuccess #Results""",

            'instagram': """Client Success: {customer_name} 🎉

Problem: {problem_short} ❌
Solution: {solution_short} ✅
Result: {result_short} 📈

{quote_short}""",

            'twitter': """💪 {customer_name} Case Study:

Problem: {problem_short}
Result: {result_short}

{quote_short}

Your turn? Let's talk 👉 [link]

#CustomerSuccess""",
        }
    },

    'thought_leadership': {
        'name': 'Thought Leadership',
        'description': 'Share industry insights and expertise',
        'required_vars': ['topic', 'perspective', 'cta_question'],
        'optional_vars': ['data'],
        'platforms': {
            'linkedin': """{topic} 💭

Here's my take: {perspective}

{data}

I've seen this play out firsthand with our clients. The companies that adapt early gain a significant competitive advantage.

{cta_question}

Looking forward to hearing your perspectives in the comments.

#ThoughtLeadership #IndustryInsights #BusinessStrategy""",

            'facebook': """Let's talk about {topic} 🗣️

{perspective}

{data}

I'm curious - {cta_question}

Drop your thoughts below! 👇

#BusinessTalk #IndustryInsights""",

            'instagram': """💭 {topic}

{perspective_short}

{data_short}

{cta_question_short}

Share your thoughts in comments! 👇""",

            'twitter': """Hot take on {topic}:

{perspective_short}

{data_short}

{cta_question_short}

#ThoughtLeadership""",
        }
    },

    'behind_the_scenes': {
        'name': 'Behind-the-Scenes',
        'description': 'Showcase company culture and process',
        'required_vars': ['activity', 'insight'],
        'optional_vars': ['team_member', 'fun_fact'],
        'platforms': {
            'linkedin': """Behind the Scenes: {activity} 🎬

{insight}

{team_member}

{fun_fact}

This is what building something great looks like - one detail at a time.

What does "behind the scenes" look like at your company?

#CompanyCulture #BehindTheScenes #TeamWork""",

            'facebook': """🎥 Behind the Scenes

Want to see what {activity} really looks like?

{insight}

{team_member}

{fun_fact}

This is the real work that goes into what we do!

#BTS #BehindTheScenes""",

            'instagram': """BTS: {activity} 🎬

{insight_short}

{team_member_short}

{fun_fact_short}""",

            'twitter': """🎬 BTS: {activity}

{insight_short}

{team_member_short}

{fun_fact_short}

#BTS #TeamLife""",
        }
    },
}


def load_env():
    """Load environment variables"""
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def list_templates():
    """List all available templates"""
    print("\nAvailable Templates:\n")
    for key, template in TEMPLATES.items():
        print(f"  {key}:")
        print(f"    Name: {template['name']}")
        print(f"    Description: {template['description']}")
        print(f"    Required: {', '.join(template['required_vars'])}")
        if template['optional_vars']:
            print(f"    Optional: {', '.join(template['optional_vars'])}")
        print()


def shorten_for_twitter(text: str, max_length: int = 50) -> str:
    """Shorten text for Twitter's character limit"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def generate_post(template_key: str, data: dict, platform: str) -> str:
    """Generate post from template for specific platform"""
    template = TEMPLATES.get(template_key)
    if not template:
        raise ValueError(f"Unknown template: {template_key}")

    # Validate required variables
    for var in template['required_vars']:
        if var not in data:
            raise ValueError(f"Missing required variable: {var}")

    # Get platform template
    platform_template = template['platforms'].get(platform)
    if not platform_template:
        raise ValueError(f"Template not available for platform: {platform}")

    # Prepare variables for substitution
    variables = {}

    for key, value in data.items():
        # Store original
        variables[key] = value

        # Create shortened versions for Twitter
        if isinstance(value, str):
            variables[f"{key}_short"] = shorten_for_twitter(value, 50)

    # Add optional variables with defaults
    for var in template.get('optional_vars', []):
        if var not in variables:
            variables[var] = ""
            variables[f"{var}_short"] = ""

    # Special handling for specific fields
    if 'team_shoutout' in variables and variables['team_shoutout']:
        if platform == 'linkedin':
            variables['team_shoutout'] = f"Huge congratulations to {variables['team_shoutout']} for making this possible."
        elif platform == 'facebook':
            variables['team_shoutout'] = f"Special shoutout to {variables['team_shoutout']} 👏"
        elif platform in ['instagram', 'twitter']:
            variables['team_shoutout_short'] = f"Thanks to {shorten_for_twitter(variables['team_shoutout'], 30)}!"

    if 'features' in variables and variables['features']:
        if isinstance(variables['features'], list):
            if platform == 'linkedin':
                variables['features'] = "**Key Features:**\n" + "\n".join(f"• {f}" for f in variables['features'])
            elif platform == 'facebook':
                variables['features'] = "What you'll love:\n" + "\n".join(f"✅ {f}" for f in variables['features'])
            else:
                variables['features'] = ""

    if 'industry' in variables and variables['industry']:
        variables['industry_prefix'] = f"As a {variables['industry']} company, "
    else:
        variables['industry_prefix'] = ""

    if 'quote' in variables and variables['quote']:
        if platform == 'linkedin':
            variables['quote'] = f'"{variables["quote"]}" - {data.get("customer_name", "Customer")}'
        elif platform == 'facebook':
            variables['quote'] = f'Here\'s what they said:\n"{variables["quote"]}"'
        else:
            variables['quote_short'] = f'"{shorten_for_twitter(variables["quote"], 80)}"'

    if 'availability' in variables and variables['availability']:
        if platform in ['linkedin', 'facebook']:
            variables['availability'] = f"Available starting {variables['availability']}."
        else:
            variables['availability_short'] = f"Coming {shorten_for_twitter(variables['availability'], 20)}"
    else:
        variables['availability'] = "Available now."
        variables['availability_short'] = "Available NOW"

    if 'data' in variables and variables['data']:
        if platform == 'linkedin':
            variables['data'] = f"The numbers back this up: {variables['data']}"
        elif platform == 'facebook':
            variables['data'] = f"Did you know? {variables['data']}"
        else:
            variables['data_short'] = f"📊 {shorten_for_twitter(variables['data'], 40)}"

    # Format template with variables
    try:
        post = platform_template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing variable in template: {e}")

    return post


def generate_all_platforms(template_key: str, data: dict, platforms: list = None) -> dict:
    """Generate posts for all specified platforms"""
    if platforms is None:
        platforms = ['linkedin', 'facebook', 'instagram', 'twitter']

    posts = {}
    for platform in platforms:
        try:
            post = generate_post(template_key, data, platform)
            posts[platform] = post
        except Exception as e:
            logger.error(f"Error generating post for {platform}: {e}")
            posts[platform] = None

    return posts


def create_approval_file(template_key: str, posts: dict):
    """Create approval request file"""
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    approval_dir = vault_path / 'Pending_Approval'
    approval_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SOCIAL_POST_{template_key}_{timestamp}.md"
    filepath = approval_dir / filename

    template = TEMPLATES[template_key]

    content = f"""---
type: social_post
template: {template_key}
platforms: {json.dumps(list(posts.keys()))}
created: {datetime.now().isoformat()}
status: pending
---

## Template: {template['name']}

{template['description']}

## Generated Content

"""

    for platform, post in posts.items():
        if post:
            content += f"### {platform.capitalize()}\n\n{post}\n\n---\n\n"

    content += """
## Instructions

**To Approve:** Move this file to `/Approved` folder
**To Reject:** Move this file to `/Rejected` folder

---

*Generated from template by social-media-manager skill*
"""

    filepath.write_text(content)
    logger.info(f"Created approval request: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description='Generate social media posts from templates')
    parser.add_argument('--template', required=True, help='Template name')
    parser.add_argument('--data', help='JSON data with template variables')
    parser.add_argument('--platforms', help='Comma-separated platforms (default: all)')
    parser.add_argument('--create-approval', action='store_true',
                       help='Create approval request instead of posting')
    parser.add_argument('--list-templates', action='store_true',
                       help='List all available templates')
    parser.add_argument('--output', help='Output file path (optional)')

    args = parser.parse_args()

    load_env()

    # List templates if requested
    if args.list_templates:
        list_templates()
        return

    # Parse data
    if not args.data:
        logger.error("--data is required (use --list-templates to see required variables)")
        return

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON data: {e}")
        return

    # Parse platforms
    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(',')]
    else:
        platforms = ['linkedin', 'facebook', 'instagram', 'twitter']

    # Generate posts
    logger.info(f"Generating posts from template: {args.template}")
    try:
        posts = generate_all_platforms(args.template, data, platforms)
    except Exception as e:
        logger.error(f"Error generating posts: {e}")
        return

    # Output or create approval
    if args.create_approval:
        filepath = create_approval_file(args.template, posts)
        logger.info(f"Approval request created: {filepath}")
    elif args.output:
        output_path = Path(args.output)
        output_content = json.dumps(posts, indent=2)
        output_path.write_text(output_content)
        logger.info(f"Generated posts saved to: {output_path}")
    else:
        # Print to stdout
        print("\n=== Generated Posts ===\n")
        for platform, post in posts.items():
            if post:
                print(f"### {platform.upper()} ###")
                print(post)
                print("\n" + "="*50 + "\n")


if __name__ == '__main__':
    main()

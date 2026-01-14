#!/usr/bin/env python3
"""
LinkedIn Post Generator - Create posts from templates

This script generates LinkedIn posts from predefined templates with variable
substitution, then creates approval requests.

Usage:
    # List available templates
    python generate_post.py --list-templates

    # Generate from template
    python generate_post.py --template achievement \
        --data '{"achievement": "Completed project", "impact": "Saved 20 hours/week"}'

    # Direct template variables (easier than JSON)
    python generate_post.py --template service \
        --service "AI Employee Automation" \
        --benefit "24/7 automated task processing"
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Import linkedin_post for approval creation
import linkedin_post

# Template definitions
TEMPLATES = {
    'achievement': {
        'name': 'Achievement Post',
        'description': 'Celebrate business milestones and wins',
        'template': """🎉 Excited to share: {achievement}!

{details}

Impact: {impact}

{call_to_action}""",
        'variables': ['achievement', 'details', 'impact', 'call_to_action'],
        'defaults': {
            'call_to_action': "What achievements are you celebrating this week?"
        },
        'hashtags': ['Achievement', 'BusinessGrowth', 'Success']
    },

    'service': {
        'name': 'Service Announcement',
        'description': 'Promote new offerings and capabilities',
        'template': """🚀 Introducing: {service}

{description}

Key benefits:
{benefit}

{call_to_action}""",
        'variables': ['service', 'description', 'benefit', 'call_to_action'],
        'defaults': {
            'call_to_action': "Interested? Drop a comment or DM to learn more!"
        },
        'hashtags': ['NewService', 'BusinessAutomation', 'Innovation']
    },

    'thought-leadership': {
        'name': 'Thought Leadership',
        'description': 'Share expertise and insights',
        'template': """💡 {topic}

My take: {insight}

{elaboration}

{question}""",
        'variables': ['topic', 'insight', 'elaboration', 'question'],
        'defaults': {
            'question': "What's your perspective on this?"
        },
        'hashtags': ['ThoughtLeadership', 'FutureOfWork', 'AIAutomation']
    },

    'behind-the-scenes': {
        'name': 'Behind The Scenes',
        'description': 'Humanize your brand',
        'template': """👀 Behind the scenes: {activity}

{description}

{insight}

{engagement_question}""",
        'variables': ['activity', 'description', 'insight', 'engagement_question'],
        'defaults': {
            'engagement_question': "How do you approach this in your work?"
        },
        'hashtags': ['BehindTheScenes', 'WorkCulture', 'TeamWork']
    },

    'engagement': {
        'name': 'Engagement Post',
        'description': 'Drive interaction and discussion',
        'template': """❓ Question for my network: {question}

{context}

{options}

Drop your thoughts in the comments! 👇""",
        'variables': ['question', 'context', 'options'],
        'defaults': {
            'options': ''
        },
        'hashtags': ['CommunityEngagement', 'Discussion', 'YourThoughts']
    },

    'case-study': {
        'name': 'Case Study / Results',
        'description': 'Share success stories and metrics',
        'template': """📊 Case Study: {title}

Challenge: {challenge}

Solution: {solution}

Results: {results}

{takeaway}""",
        'variables': ['title', 'challenge', 'solution', 'results', 'takeaway'],
        'defaults': {
            'takeaway': 'Key learning: Focus on fundamentals and iterate quickly.'
        },
        'hashtags': ['CaseStudy', 'Results', 'BusinessSuccess']
    },

    'tip': {
        'name': 'Quick Tip',
        'description': 'Share actionable advice',
        'template': """💡 Quick tip: {tip_title}

{tip_content}

Why it works: {reason}

Try it this week and let me know how it goes!""",
        'variables': ['tip_title', 'tip_content', 'reason'],
        'defaults': {},
        'hashtags': ['ProductivityTip', 'BusinessTip', 'QuickWin']
    },

    'milestone': {
        'name': 'Business Milestone',
        'description': 'Celebrate company growth and milestones',
        'template': """🎯 Milestone achieved: {milestone}!

When we started: {starting_point}

Where we are now: {current_state}

Grateful for: {gratitude}

{future_outlook}""",
        'variables': ['milestone', 'starting_point', 'current_state', 'gratitude', 'future_outlook'],
        'defaults': {
            'future_outlook': "Excited for what's next!"
        },
        'hashtags': ['Milestone', 'BusinessGrowth', 'Entrepreneurship']
    }
}


def list_templates():
    """Display all available templates."""
    print("📋 Available LinkedIn Post Templates:\n")

    for template_id, template in TEMPLATES.items():
        print(f"  {template_id}")
        print(f"    Name: {template['name']}")
        print(f"    Description: {template['description']}")
        print(f"    Variables: {', '.join(template['variables'])}")
        print(f"    Hashtags: {', '.join(template['hashtags'])}")
        print()


def generate_from_template(template_id, variables):
    """
    Generate post content from template.

    Args:
        template_id: Template identifier
        variables: Dictionary of variable values

    Returns:
        Tuple of (message, hashtags)
    """
    if template_id not in TEMPLATES:
        print(f"❌ Template '{template_id}' not found")
        print(f"   Available templates: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)

    template = TEMPLATES[template_id]

    # Merge with defaults
    merged_vars = {**template.get('defaults', {}), **variables}

    # Check for required variables
    missing = [v for v in template['variables'] if v not in merged_vars]
    if missing:
        print(f"❌ Missing required variables: {', '.join(missing)}")
        print(f"   Required: {', '.join(template['variables'])}")
        sys.exit(1)

    # Generate message
    try:
        message = template['template'].format(**merged_vars)
    except KeyError as e:
        print(f"❌ Template variable error: {e}")
        sys.exit(1)

    hashtags = template['hashtags']

    return message, hashtags


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Post Generator from Templates')

    parser.add_argument('--list-templates', action='store_true',
                        help='List all available templates')
    parser.add_argument('--template', type=str,
                        help='Template ID to use')
    parser.add_argument('--data', type=str,
                        help='JSON string with template variables')

    # Direct variable arguments for common templates
    parser.add_argument('--achievement', type=str, help='Achievement description')
    parser.add_argument('--details', type=str, help='Achievement details')
    parser.add_argument('--impact', type=str, help='Impact/results')
    parser.add_argument('--service', type=str, help='Service name')
    parser.add_argument('--description', type=str, help='Service/activity description')
    parser.add_argument('--benefit', type=str, help='Key benefit')
    parser.add_argument('--topic', type=str, help='Topic for thought leadership')
    parser.add_argument('--insight', type=str, help='Your insight/take')
    parser.add_argument('--elaboration', type=str, help='Elaboration on insight')
    parser.add_argument('--question', type=str, help='Engagement question')
    parser.add_argument('--activity', type=str, help='Behind-the-scenes activity')
    parser.add_argument('--call-to-action', type=str, help='Call to action text')

    parser.add_argument('--create-approval', action='store_true', default=True,
                        help='Create approval request (default: true)')
    parser.add_argument('--post-directly', action='store_true',
                        help='Post directly without approval (not recommended)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show preview without creating approval')

    args = parser.parse_args()

    # List templates
    if args.list_templates:
        list_templates()
        return

    # Generate from template
    if args.template:
        # Collect variables from arguments or JSON data
        if args.data:
            try:
                variables = json.loads(args.data)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in --data: {e}")
                sys.exit(1)
        else:
            # Build variables dict from command line args
            variables = {}
            arg_mapping = {
                'achievement': 'achievement',
                'details': 'details',
                'impact': 'impact',
                'service': 'service',
                'description': 'description',
                'benefit': 'benefit',
                'topic': 'topic',
                'insight': 'insight',
                'elaboration': 'elaboration',
                'question': 'question',
                'activity': 'activity',
                'call_to_action': 'call-to-action'
            }

            for arg_name, var_name in arg_mapping.items():
                value = getattr(args, arg_name.replace('-', '_'), None)
                if value:
                    variables[var_name] = value

        # Generate post
        message, hashtags = generate_from_template(args.template, variables)

        print("📝 Generated Post:")
        print("─" * 60)
        print(message)
        print()
        print(' '.join([f'#{tag}' for tag in hashtags]))
        print("─" * 60)
        print(f"Template: {args.template}")
        print(f"Character count: {len(message)}")
        print()

        # Create approval or post directly
        if args.dry_run:
            print("🧪 DRY RUN - No approval created")
        elif args.post_directly:
            print("⚠️  Posting directly without approval...")
            linkedin_post.create_post(message, hashtags)
        else:
            linkedin_post.create_approval_request(message, hashtags)

        return

    # No valid command
    parser.print_help()


if __name__ == '__main__':
    main()

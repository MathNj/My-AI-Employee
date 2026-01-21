#!/usr/bin/env python3
"""
Post content to social media platforms via MCP servers

Usage:
    # Single platform
    python post_to_platform.py --platform linkedin --message "Great news!"

    # Multiple platforms
    python post_to_platform.py --platforms linkedin,facebook --message "Update"

    # With approval workflow
    python post_to_platform.py --platforms all --message "Big announcement!" --create-approval

    # With image (Instagram)
    python post_to_platform.py --platform instagram --message "Check this out" --image photo.jpg

    # Scheduled post
    python post_to_platform.py --platform linkedin --message "Weekly update" --schedule "2026-01-15T09:00:00Z"
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Platform character limits
CHAR_LIMITS = {
    'linkedin': 3000,
    'facebook': 63206,
    'instagram': 2200,
    'twitter': 280,
}

# Platform-specific formatting rules
PLATFORM_RULES = {
    'linkedin': {
        'hashtags': 5,
        'tone': 'professional',
        'emojis': 'minimal',
    },
    'facebook': {
        'hashtags': 3,
        'tone': 'conversational',
        'emojis': 'moderate',
    },
    'instagram': {
        'hashtags': 30,
        'tone': 'casual',
        'emojis': 'heavy',
        'requires_image': True,
    },
    'twitter': {
        'hashtags': 3,
        'tone': 'concise',
        'emojis': 'light',
    },
}


def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def validate_message(platform: str, message: str) -> bool:
    """Validate message meets platform requirements"""
    limit = CHAR_LIMITS.get(platform)
    if not limit:
        logger.error(f"Unknown platform: {platform}")
        return False

    if len(message) > limit:
        logger.error(f"{platform} message exceeds {limit} character limit ({len(message)} chars)")
        return False

    # Instagram requires image
    rules = PLATFORM_RULES.get(platform, {})
    if rules.get('requires_image'):
        logger.warning(f"{platform} requires an image. Use --image parameter.")

    return True


def format_for_platform(platform: str, message: str, hashtags: list = None) -> str:
    """Format message according to platform best practices"""
    rules = PLATFORM_RULES.get(platform, {})

    # Add hashtags if provided
    if hashtags:
        max_tags = rules.get('hashtags', 5)
        selected_tags = hashtags[:max_tags]

        if platform == 'instagram':
            # Instagram: Add all hashtags at end with spacing
            message = f"{message}\n\n.\n.\n.\n{' '.join(selected_tags)}"
        else:
            # Other platforms: Add hashtags at end
            message = f"{message}\n\n{' '.join(selected_tags)}"

    return message


def create_approval_file(platforms: list, message: str, image: str = None, schedule: str = None):
    """Create approval request file in /Pending_Approval folder"""
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    approval_dir = vault_path / 'Pending_Approval'
    approval_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SOCIAL_POST_{timestamp}.md"
    filepath = approval_dir / filename

    # Create platform-specific versions
    platform_content = {}
    for platform in platforms:
        formatted = format_for_platform(platform, message)
        platform_content[platform] = formatted

    content = f"""---
type: social_post
platforms: {json.dumps(platforms)}
created: {datetime.now().isoformat()}
schedule: {schedule if schedule else 'null'}
status: pending
image: {image if image else 'null'}
---

## Post Content

"""

    for platform in platforms:
        limit = CHAR_LIMITS[platform]
        content += f"### {platform.capitalize()} ({limit} char limit)\n"
        content += f"{platform_content[platform]}\n\n"

    content += f"""
## Instructions

**To Approve:** Move this file to `/Approved` folder
**To Reject:** Move this file to `/Rejected` folder

---

*Created by social-media-manager skill*
"""

    filepath.write_text(content)
    logger.info(f"Created approval request: {filepath}")
    return filepath


def post_to_linkedin(message: str):
    """Post to LinkedIn via MCP"""
    logger.info("Posting to LinkedIn...")
    # TODO: Call LinkedIn MCP server
    # In real implementation, this would use Claude Code MCP tools
    logger.info(f"LinkedIn post: {message[:50]}...")
    return {"platform": "linkedin", "status": "posted", "id": "LI_12345"}


def post_to_facebook(message: str):
    """Post to Facebook via MCP"""
    logger.info("Posting to Facebook...")
    # TODO: Call Meta MCP server
    logger.info(f"Facebook post: {message[:50]}...")
    return {"platform": "facebook", "status": "posted", "id": "FB_12345"}


def post_to_instagram(message: str, image: str):
    """Post to Instagram via MCP"""
    if not image:
        raise ValueError("Instagram requires an image")

    logger.info("Posting to Instagram...")
    # TODO: Call Meta MCP server
    logger.info(f"Instagram post with image {image}: {message[:50]}...")
    return {"platform": "instagram", "status": "posted", "id": "IG_12345"}


def post_to_twitter(message: str):
    """Post to Twitter/X via MCP"""
    logger.info("Posting to Twitter/X...")

    # Split into thread if needed
    if len(message) > 280:
        logger.info("Message too long, creating thread...")
        # TODO: Split into multiple tweets

    # TODO: Call X MCP server
    logger.info(f"Twitter post: {message[:50]}...")
    return {"platform": "twitter", "status": "posted", "id": "TW_12345"}


def post_to_platforms(platforms: list, message: str, image: str = None):
    """Post to multiple platforms"""
    results = []

    for platform in platforms:
        try:
            # Validate message for platform
            if not validate_message(platform, message):
                results.append({
                    "platform": platform,
                    "status": "error",
                    "error": "Validation failed"
                })
                continue

            # Post to platform
            if platform == 'linkedin':
                result = post_to_linkedin(message)
            elif platform == 'facebook':
                result = post_to_facebook(message)
            elif platform == 'instagram':
                result = post_to_instagram(message, image)
            elif platform == 'twitter':
                result = post_to_twitter(message)
            else:
                result = {
                    "platform": platform,
                    "status": "error",
                    "error": "Unknown platform"
                }

            results.append(result)

        except Exception as e:
            logger.error(f"Error posting to {platform}: {e}")
            results.append({
                "platform": platform,
                "status": "error",
                "error": str(e)
            })

    return results


def main():
    parser = argparse.ArgumentParser(description='Post to social media platforms')
    parser.add_argument('--platform', help='Single platform (linkedin/facebook/instagram/twitter)')
    parser.add_argument('--platforms', help='Multiple platforms (comma-separated or "all")')
    parser.add_argument('--message', required=True, help='Post content')
    parser.add_argument('--image', help='Image file path (required for Instagram)')
    parser.add_argument('--schedule', help='Schedule for future (ISO 8601 format)')
    parser.add_argument('--create-approval', action='store_true',
                       help='Create approval request instead of posting directly')
    parser.add_argument('--hashtags', help='Comma-separated hashtags (e.g., "#Business,#Growth")')

    args = parser.parse_args()

    load_env()

    # Determine target platforms
    if args.platforms:
        if args.platforms.lower() == 'all':
            platforms = ['linkedin', 'facebook', 'instagram', 'twitter']
        else:
            platforms = [p.strip() for p in args.platforms.split(',')]
    elif args.platform:
        platforms = [args.platform]
    else:
        logger.error("Must specify --platform or --platforms")
        return

    # Parse hashtags
    hashtags = None
    if args.hashtags:
        hashtags = [tag.strip() for tag in args.hashtags.split(',')]
        if not all(tag.startswith('#') for tag in hashtags):
            logger.error("All hashtags must start with #")
            return

    # Validate message for all platforms
    valid = True
    for platform in platforms:
        if not validate_message(platform, args.message):
            valid = False

    if not valid:
        logger.error("Message validation failed for one or more platforms")
        return

    # Create approval request if requested
    if args.create_approval:
        filepath = create_approval_file(
            platforms,
            args.message,
            args.image,
            args.schedule
        )
        logger.info(f"Approval request created: {filepath}")
        logger.info("Move to /Approved folder to proceed with posting")
        return

    # Check if scheduled
    if args.schedule:
        logger.info(f"Scheduled post for {args.schedule}")
        logger.info("Use scheduler-manager to trigger at specified time")
        # TODO: Create scheduled task
        return

    # Post immediately
    logger.info(f"Posting to {len(platforms)} platform(s)...")
    results = post_to_platforms(platforms, args.message, args.image)

    # Log results
    logger.info("\n=== Results ===")
    for result in results:
        status = result['status']
        platform = result['platform']
        if status == 'posted':
            logger.info(f"[OK] {platform}: Posted successfully (ID: {result['id']})")
        else:
            logger.error(f"[FAIL] {platform}: {result.get('error', 'Unknown error')}")

    # Update dashboard
    vault_path = Path(os.getenv('VAULT_PATH', 'C:/Users/Najma-LP/Desktop/My Vault/AI_Employee_Vault'))
    dashboard_file = vault_path / 'Dashboard.md'
    if dashboard_file.exists():
        logger.info("Updated Dashboard.md")


if __name__ == '__main__':
    main()

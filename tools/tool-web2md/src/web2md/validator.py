"""Content validation - detects paywalls and auth walls."""

from dataclasses import dataclass

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of content validation."""
    is_valid: bool
    reason: str | None = None
    detected_pattern: str | None = None


PAYWALL_PATTERNS = [
    "member-only story",
    "members only",
    "this story is for members",
    "this post is for paid subscribers",
    "this post is for paying subscribers only",
    "upgrade to paid",
    "this post is for paying subscribers",
    "unlock this post",
    "sign in to read",
    "sign up to read more",
    "log in to continue reading",
    "subscribe to continue reading",
    "this content is for subscribers",
    "premium content",
    "exclusive content",
]


def validate_content(html: str, markdown: str, url: str) -> ValidationResult:
    """Validate that content is accessible and not behind a paywall.
    
    Args:
        html: Raw HTML content
        markdown: Converted markdown content
        url: Original URL
        
    Returns:
        ValidationResult indicating if content is valid
    """
    html_lower = html.lower()
    
    # Check for paywall patterns
    for pattern in PAYWALL_PATTERNS:
        if pattern in html_lower:
            return ValidationResult(
                is_valid=False,
                reason=f"Paywall detected: '{pattern}'",
                detected_pattern=pattern
            )

    # Check for auth wall indicators
    auth_class_patterns = ["login", "signin", "signup", "paywall", "auth-wall"]
    auth_indicator_count = sum(
        html_lower.count(f'class="{pattern}"') + html_lower.count(f"class='{pattern}'")
        for pattern in auth_class_patterns
    )

    if auth_indicator_count >= 3:
        logger.debug(f"Found {auth_indicator_count} auth-related class names")
        return ValidationResult(
            is_valid=False,
            reason="Multiple authentication elements detected",
            detected_pattern="auth_forms"
        )

    # Check markdown content quality
    lines = markdown.split("\n")
    content_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter:
            content_lines.append(line)

    content_text = "\n".join(content_lines)
    words = content_text.split()
    content_words = [w for w in words if len(w) > 2 and not w.startswith("[") and not w.startswith("(http")]
    word_count = len(content_words)

    if word_count < 15:
        logger.debug(f"Content has only {word_count} words")
        return ValidationResult(
            is_valid=False,
            reason=f"Content too short ({word_count} words), likely incomplete",
            detected_pattern="short_content",
        )

    # Check auth mention ratio
    auth_mentions = sum(
        1 for pattern in ["sign in", "sign up", "log in", "subscribe", "member"]
        if pattern in content_text.lower()
    )

    if auth_mentions >= 5 and word_count < 150:
        logger.debug(f"High auth mention ratio: {auth_mentions} mentions in {word_count} words")
        return ValidationResult(
            is_valid=False,
            reason="High ratio of authentication prompts to content",
            detected_pattern="high_auth_ratio"
        )

    logger.debug(f"Content validation passed: {word_count} words")
    return ValidationResult(is_valid=True)

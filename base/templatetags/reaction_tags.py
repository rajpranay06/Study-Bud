from django import template
from django.db.models import Count
from collections import defaultdict
from ..models import Message  # Import your Message model

register = template.Library()

@register.filter
def emoji_count(message, emoji_code):
    return message.reactions.filter(emoji=emoji_code).count()

@register.filter
def regroup_by_emoji(reactions):
    """Group reactions by emoji and count them with user list for hover display"""
    emoji_dict = {}
    
    for reaction in reactions:
        emoji = reaction.emoji
        if emoji in emoji_dict:
            emoji_dict[emoji]['count'] += 1
            emoji_dict[emoji]['users'].append(reaction.user.username)
        else:
            emoji_dict[emoji] = {
                'emoji': emoji,
                'count': 1,
                'users': [reaction.user.username]
            }
    
    # Sort by count (most popular first)
    return sorted(emoji_dict.values(), key=lambda x: x['count'], reverse=True)

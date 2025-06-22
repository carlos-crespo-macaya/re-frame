"""Test data generators for API testing."""

import random
from typing import Any
from faker import Faker

fake = Faker()


class ThoughtGenerator:
    """Generate realistic test thoughts for AvPD scenarios."""
    
    # Thought patterns common in AvPD
    CATASTROPHIZING_TEMPLATES = [
        "Everyone will {negative_outcome} if I {action}",
        "I'll definitely {failure} and then {consequence}",
        "This will be a complete {disaster_word}",
        "{social_group} will all {rejection_verb} me",
        "I know I'll {embarrassing_action} and everyone will {judge_verb}",
    ]
    
    MIND_READING_TEMPLATES = [
        "They must think I'm {negative_trait}",
        "Everyone can see that I'm {inadequacy}",
        "They're probably {judging_action} right now",
        "I bet they're thinking '{negative_thought}'",
        "They obviously {negative_assumption} about me",
    ]
    
    AVOIDANCE_TEMPLATES = [
        "I should just {avoidance_action} to avoid {feared_outcome}",
        "It's safer if I don't {social_action}",
        "I'll just {isolation_behavior} instead",
        "Maybe I should cancel {event} because {fear}",
        "I can't handle {situation}, I need to {escape}",
    ]
    
    ALL_OR_NOTHING_TEMPLATES = [
        "I'm completely {absolute_negative}",
        "I never {positive_action} right",
        "Everyone always {negative_behavior} me",
        "Nothing ever {positive_outcome} for me",
        "I'm totally {inadequacy} at everything",
    ]
    
    # Word banks
    NEGATIVE_OUTCOMES = ["judge me", "laugh at me", "reject me", "hate me", "mock me", "abandon me"]
    ACTIONS = ["speak up", "attend the meeting", "go to the party", "share my opinion", "try something new"]
    FAILURES = ["mess up", "fail", "embarrass myself", "say something stupid", "make mistakes"]
    CONSEQUENCES = ["everyone will know", "I'll be humiliated", "they'll never respect me", "I'll be alone forever"]
    DISASTER_WORDS = ["disaster", "catastrophe", "nightmare", "failure", "embarrassment"]
    SOCIAL_GROUPS = ["My coworkers", "Everyone at the party", "The whole team", "All my friends", "The entire class"]
    REJECTION_VERBS = ["reject", "abandon", "exclude", "ignore", "laugh at", "judge"]
    NEGATIVE_TRAITS = ["stupid", "worthless", "incompetent", "boring", "weird", "pathetic", "inadequate"]
    INADEQUACIES = ["failing", "not good enough", "incompetent", "a fraud", "worthless"]
    JUDGING_ACTIONS = ["laughing at me", "talking about me", "judging me", "criticizing me"]
    NEGATIVE_THOUGHTS = ["What a loser", "They don't belong here", "How pathetic", "What's wrong with them"]
    NEGATIVE_ASSUMPTIONS = ["hate me", "think I'm stupid", "want me to leave", "regret inviting me"]
    AVOIDANCE_ACTIONS = ["stay home", "make an excuse", "cancel", "hide", "leave early"]
    FEARED_OUTCOMES = ["rejection", "embarrassment", "judgment", "criticism", "failure"]
    SOCIAL_ACTIONS = ["go to the event", "speak in the meeting", "join the conversation", "make new friends"]
    ISOLATION_BEHAVIORS = ["stay in my room", "work from home forever", "avoid everyone", "eat lunch alone"]
    EVENTS = ["the meeting", "the party", "the presentation", "the date", "the interview"]
    FEARS = ["I might say something wrong", "they'll judge me", "I'll have a panic attack", "I won't know what to say"]
    SITUATIONS = ["social events", "meetings", "phone calls", "group discussions", "presentations"]
    ESCAPES = ["leave", "make an excuse", "hide in the bathroom", "pretend to be sick"]
    ABSOLUTE_NEGATIVES = ["worthless", "hopeless", "useless", "pathetic", "incompetent"]
    POSITIVE_ACTIONS = ["do anything", "say anything", "get anything", "succeed at anything"]
    NEGATIVE_BEHAVIORS = ["rejects", "judges", "criticizes", "ignores", "dislikes"]
    POSITIVE_OUTCOMES = ["works out", "goes well", "succeeds", "turns out okay"]
    
    @classmethod
    def generate_catastrophizing_thought(cls) -> str:
        """Generate a catastrophizing thought."""
        template = random.choice(cls.CATASTROPHIZING_TEMPLATES)
        return template.format(
            negative_outcome=random.choice(cls.NEGATIVE_OUTCOMES),
            action=random.choice(cls.ACTIONS),
            failure=random.choice(cls.FAILURES),
            consequence=random.choice(cls.CONSEQUENCES),
            disaster_word=random.choice(cls.DISASTER_WORDS),
            social_group=random.choice(cls.SOCIAL_GROUPS),
            rejection_verb=random.choice(cls.REJECTION_VERBS),
            embarrassing_action=random.choice(cls.FAILURES),
            judge_verb=random.choice(cls.REJECTION_VERBS),
        )
    
    @classmethod
    def generate_mind_reading_thought(cls) -> str:
        """Generate a mind-reading thought."""
        template = random.choice(cls.MIND_READING_TEMPLATES)
        return template.format(
            negative_trait=random.choice(cls.NEGATIVE_TRAITS),
            inadequacy=random.choice(cls.INADEQUACIES),
            judging_action=random.choice(cls.JUDGING_ACTIONS),
            negative_thought=random.choice(cls.NEGATIVE_THOUGHTS),
            negative_assumption=random.choice(cls.NEGATIVE_ASSUMPTIONS),
        )
    
    @classmethod
    def generate_avoidance_thought(cls) -> str:
        """Generate an avoidance-focused thought."""
        template = random.choice(cls.AVOIDANCE_TEMPLATES)
        return template.format(
            avoidance_action=random.choice(cls.AVOIDANCE_ACTIONS),
            feared_outcome=random.choice(cls.FEARED_OUTCOMES),
            social_action=random.choice(cls.SOCIAL_ACTIONS),
            isolation_behavior=random.choice(cls.ISOLATION_BEHAVIORS),
            event=random.choice(cls.EVENTS),
            fear=random.choice(cls.FEARS),
            situation=random.choice(cls.SITUATIONS),
            escape=random.choice(cls.ESCAPES),
        )
    
    @classmethod
    def generate_all_or_nothing_thought(cls) -> str:
        """Generate an all-or-nothing thought."""
        template = random.choice(cls.ALL_OR_NOTHING_TEMPLATES)
        return template.format(
            absolute_negative=random.choice(cls.ABSOLUTE_NEGATIVES),
            positive_action=random.choice(cls.POSITIVE_ACTIONS),
            negative_behavior=random.choice(cls.NEGATIVE_BEHAVIORS),
            positive_outcome=random.choice(cls.POSITIVE_OUTCOMES),
            inadequacy=random.choice(cls.INADEQUACIES),
        )
    
    @classmethod
    def generate_random_thought(cls) -> str:
        """Generate a random AvPD-related thought."""
        generators = [
            cls.generate_catastrophizing_thought,
            cls.generate_mind_reading_thought,
            cls.generate_avoidance_thought,
            cls.generate_all_or_nothing_thought,
        ]
        return random.choice(generators)()
    
    @classmethod
    def generate_crisis_thought(cls) -> str:
        """Generate a thought that should trigger crisis detection."""
        crisis_phrases = [
            "I don't want to go on anymore",
            "Life isn't worth living like this",
            "I can't take this pain anymore",
            "Everyone would be better off without me",
            "I want to end it all",
            "There's no point in continuing",
        ]
        return random.choice(crisis_phrases)
    
    @classmethod
    def generate_with_context(cls) -> dict[str, str]:
        """Generate a thought with context."""
        thought = cls.generate_random_thought()
        contexts = [
            "This happens every time I try to socialize",
            "I've been feeling this way for weeks",
            "After what happened last time",
            "My therapist suggested I challenge this thought",
            "This started after the incident at work",
            f"I'm {fake.random_int(20, 50)} years old and still struggling with this",
        ]
        return {
            "thought": thought,
            "context": random.choice(contexts)
        }


class ResponseGenerator:
    """Generate expected API responses."""
    
    TECHNIQUES = [
        "cognitive_restructuring",
        "evidence_analysis",
        "decatastrophizing",
        "behavioral_experiments",
        "self_compassion",
    ]
    
    @classmethod
    def generate_success_response(cls, thought: str) -> dict[str, Any]:
        """Generate a successful reframe response."""
        return {
            "success": True,
            "response": f"Let's look at this differently: {thought} This thought might feel true, but...",
            "transparency": {
                "techniques_applied": random.sample(cls.TECHNIQUES, k=random.randint(1, 3)),
                "reasoning_path": [
                    "Identified cognitive distortion",
                    "Applied balanced thinking",
                    "Suggested alternative perspective"
                ],
                "confidence": random.uniform(0.7, 0.95),
            },
            "techniques_used": random.sample(cls.TECHNIQUES, k=random.randint(1, 3)),
        }
    
    @classmethod
    def generate_error_response(cls, error_type: str = "processing") -> dict[str, Any]:
        """Generate an error response."""
        error_messages = {
            "processing": "Failed to process thought",
            "validation": "Invalid input provided",
            "rate_limit": "Rate limit exceeded",
            "toxic_content": "Content flagged as potentially harmful",
        }
        
        return {
            "success": False,
            "response": "I wasn't able to process your thought. Please try rephrasing it.",
            "transparency": {
                "error": error_type,
                "stage": "intake" if error_type == "validation" else "processing",
            },
            "techniques_used": [],
            "error": error_messages.get(error_type, "Unknown error"),
        }
    
    @classmethod
    def generate_crisis_response(cls) -> dict[str, Any]:
        """Generate a crisis detection response."""
        return {
            "success": True,
            "response": "I notice you might be going through a particularly difficult time. Please consider reaching out to a mental health professional or crisis helpline for immediate support. You can call 988 for the Suicide & Crisis Lifeline.",
            "transparency": {
                "crisis_detected": True,
                "resources_provided": True,
            },
            "techniques_used": ["crisis_detection"],
        }


class SessionDataGenerator:
    """Generate session-related test data."""
    
    @classmethod
    def generate_session_id(cls) -> str:
        """Generate a realistic session ID."""
        return f"session-{fake.uuid4()}"
    
    @classmethod
    def generate_session_history(cls, num_interactions: int = 3) -> dict[str, Any]:
        """Generate session history data."""
        session_id = cls.generate_session_id()
        interactions = []
        
        for i in range(num_interactions):
            thought = ThoughtGenerator.generate_random_thought()
            response = ResponseGenerator.generate_success_response(thought)
            
            interactions.append({
                "timestamp": fake.date_time_this_month().isoformat(),
                "thought": thought,
                "response": response["response"],
                "techniques_used": response["techniques_used"],
            })
        
        return {
            "session_id": session_id,
            "created_at": fake.date_time_this_month().isoformat(),
            "last_activity": fake.date_time_this_hour().isoformat(),
            "interactions": interactions,
            "total_interactions": len(interactions),
        }


class PerformanceDataGenerator:
    """Generate performance metrics test data."""
    
    @classmethod
    def generate_performance_metrics(cls) -> dict[str, Any]:
        """Generate realistic performance metrics."""
        return {
            "avg_response_time": random.uniform(0.3, 1.5),
            "p95_response_time": random.uniform(1.0, 3.0),
            "p99_response_time": random.uniform(2.0, 5.0),
            "total_requests": random.randint(100, 10000),
            "success_rate": random.uniform(0.92, 0.99),
            "error_rate": random.uniform(0.01, 0.08),
            "requests_per_minute": random.uniform(5, 50),
            "active_sessions": random.randint(0, 100),
            "cache_hit_rate": random.uniform(0.6, 0.9),
        }
    
    @classmethod
    def generate_error_analysis(cls) -> dict[str, Any]:
        """Generate error analysis data."""
        error_types = ["validation", "processing", "rate_limit", "timeout", "internal"]
        return {
            "total_errors": random.randint(10, 100),
            "error_rate": random.uniform(0.01, 0.05),
            "errors_by_type": {
                error_type: random.randint(0, 30)
                for error_type in error_types
            },
            "common_errors": [
                {
                    "error": "Rate limit exceeded",
                    "count": random.randint(5, 20),
                    "percentage": random.uniform(0.2, 0.5),
                },
                {
                    "error": "Invalid thought format",
                    "count": random.randint(3, 15),
                    "percentage": random.uniform(0.1, 0.3),
                },
            ],
            "error_trend": "decreasing" if random.random() > 0.5 else "stable",
        }


# Convenience functions for quick test data generation
def generate_test_thought() -> str:
    """Generate a single test thought."""
    return ThoughtGenerator.generate_random_thought()


def generate_test_request() -> dict[str, str]:
    """Generate a complete test request."""
    if random.random() < 0.8:
        return {"thought": generate_test_thought()}
    else:
        data = ThoughtGenerator.generate_with_context()
        return {"thought": data["thought"], "context": data["context"]}


def generate_batch_requests(count: int) -> list[dict[str, str]]:
    """Generate multiple test requests."""
    return [generate_test_request() for _ in range(count)]
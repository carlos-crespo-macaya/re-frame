"""Local mental health resources lookup system."""


class LocalResourceProvider:
    """Provides location-based mental health resources."""

    def __init__(self):
        # Common resources by country/region
        self.resources = {
            "US": {
                "national": [
                    {
                        "name": "National Suicide Prevention Lifeline",
                        "number": "988",
                        "available": "24/7",
                    },
                    {
                        "name": "Crisis Text Line",
                        "number": "Text HOME to 741741",
                        "available": "24/7",
                    },
                    {
                        "name": "SAMHSA National Helpline",
                        "number": "1-800-662-4357",
                        "available": "24/7",
                    },
                    {
                        "name": "National Domestic Violence Hotline",
                        "number": "1-800-799-7233",
                        "available": "24/7",
                    },
                    {
                        "name": "Veterans Crisis Line",
                        "number": "1-800-273-8255",
                        "available": "24/7",
                    },
                ],
                "online": [
                    {
                        "name": "Psychology Today Therapist Finder",
                        "url": "psychologytoday.com",
                    },
                    {
                        "name": "SAMHSA Treatment Locator",
                        "url": "findtreatment.samhsa.gov",
                    },
                    {
                        "name": "Open Path Psychotherapy Collective",
                        "url": "openpathcollective.org",
                    },
                ],
            },
            "UK": {
                "national": [
                    {"name": "Samaritans", "number": "116 123", "available": "24/7"},
                    {
                        "name": "Crisis Text Line UK",
                        "number": "Text SHOUT to 85258",
                        "available": "24/7",
                    },
                    {
                        "name": "CALM (Campaign Against Living Miserably)",
                        "number": "0800 58 58 58",
                        "available": "5pm-midnight",
                    },
                    {
                        "name": "Papyrus HOPELineUK",
                        "number": "0800 068 4141",
                        "available": "9am-midnight",
                    },
                ],
                "online": [
                    {
                        "name": "NHS Mental Health Services",
                        "url": "nhs.uk/mental-health",
                    },
                    {"name": "Mind UK", "url": "mind.org.uk"},
                    {"name": "Rethink Mental Illness", "url": "rethink.org"},
                ],
            },
            "CA": {
                "national": [
                    {
                        "name": "Talk Suicide Canada",
                        "number": "1-833-456-4566",
                        "available": "24/7",
                    },
                    {
                        "name": "Crisis Text Line Canada",
                        "number": "Text CONNECT to 686868",
                        "available": "24/7",
                    },
                    {
                        "name": "Kids Help Phone",
                        "number": "1-800-668-6868",
                        "available": "24/7",
                    },
                ],
                "online": [
                    {"name": "Canadian Mental Health Association", "url": "cmha.ca"},
                    {"name": "Wellness Together Canada", "url": "wellnesstogether.ca"},
                ],
            },
            "AU": {
                "national": [
                    {
                        "name": "Lifeline Australia",
                        "number": "13 11 14",
                        "available": "24/7",
                    },
                    {
                        "name": "Beyond Blue",
                        "number": "1300 22 4636",
                        "available": "24/7",
                    },
                    {
                        "name": "Kids Helpline",
                        "number": "1800 55 1800",
                        "available": "24/7",
                    },
                ],
                "online": [
                    {"name": "Head to Health", "url": "headtohealth.gov.au"},
                    {"name": "ReachOut Australia", "url": "au.reachout.com"},
                ],
            },
        }

        # Default international resources
        self.international_resources = {
            "national": [
                {
                    "name": "International Association for Suicide Prevention",
                    "url": "iasp.info/resources/Crisis_Centres",
                }
            ],
            "online": [
                {"name": "Befrienders Worldwide", "url": "befrienders.org"},
                {
                    "name": "Crisis Text Line (via WhatsApp)",
                    "number": "+1 989-200-3674",
                    "available": "Various countries",
                },
                {
                    "name": "7 Cups",
                    "url": "7cups.com",
                    "description": "Free emotional support",
                },
            ],
        }

    def get_resources_by_country(
        self, country_code: str = "US"
    ) -> dict[str, list[dict]]:
        """
        Get mental health resources for a specific country.

        Args:
            country_code: ISO country code (default: US)

        Returns:
            Dictionary of resources by category
        """
        country_resources: dict[str, list[dict]] = self.resources.get(
            country_code.upper(), self.international_resources
        )
        return country_resources

    def format_resources_text(
        self, country_code: str = "US", include_online: bool = True
    ) -> str:
        """
        Format resources as readable text.

        Args:
            country_code: ISO country code
            include_online: Whether to include online resources

        Returns:
            Formatted text of resources
        """
        resources = self.get_resources_by_country(country_code)
        lines = []

        # Add crisis hotlines
        if "national" in resources:
            lines.append("**24/7 Crisis Support:**")
            for resource in resources["national"]:
                availability = (
                    f" ({resource.get('available', '')})"
                    if "available" in resource
                    else ""
                )
                if "number" in resource:
                    lines.append(
                        f"- **{resource['name']}**: {resource['number']}{availability}"
                    )
                else:
                    lines.append(f"- **{resource['name']}**: {resource.get('url', '')}")

        # Add online resources if requested
        if include_online and "online" in resources:
            lines.append("\n**Online Resources:**")
            for resource in resources["online"]:
                description = (
                    f" - {resource.get('description', '')}"
                    if "description" in resource
                    else ""
                )
                lines.append(
                    f"- **{resource['name']}**: {resource.get('url', resource.get('number', ''))}{description}"
                )

        return "\n".join(lines)

    def get_emergency_contacts(self, country_code: str = "US") -> list[dict]:
        """
        Get emergency contact numbers for immediate help.

        Args:
            country_code: ISO country code

        Returns:
            List of emergency contacts
        """
        emergency_numbers = {
            "US": {"emergency": "911", "crisis": "988"},
            "UK": {"emergency": "999", "crisis": "116 123"},
            "CA": {"emergency": "911", "crisis": "1-833-456-4566"},
            "AU": {"emergency": "000", "crisis": "13 11 14"},
            "DEFAULT": {"emergency": "112", "crisis": "Local crisis line"},
        }

        country_emergency = emergency_numbers.get(
            country_code.upper(), emergency_numbers["DEFAULT"]
        )

        return [
            {
                "type": "emergency",
                "number": country_emergency["emergency"],
                "description": "Emergency services",
            },
            {
                "type": "crisis",
                "number": country_emergency["crisis"],
                "description": "Mental health crisis line",
            },
        ]

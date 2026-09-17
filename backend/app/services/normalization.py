"""
Semantic Normalization Service (§13).
Maintains canonical skill taxonomies, alias maps, and semantic equivalence rules.
Enforces strict negative boundaries so distinct technologies are NOT conflated
(e.g., Docker ≠ Kubernetes, React ≠ Next.js, SQL ≠ NoSQL).
"""

import re
from typing import Optional, Set, Dict, List, Tuple


class SemanticNormalizationService:
    """
    Normalizes skills, technologies, and job requirements to canonical representations.
    Provides deterministic alias resolution and equivalence matching.
    """

    # ── Canonical Taxonomy & Aliases ──
    # Maps alias (lowercase) -> Canonical display name
    ALIAS_MAP: Dict[str, str] = {
        # Languages
        "js": "JavaScript",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "python": "Python",
        "python3": "Python",
        "py": "Python",
        "golang": "Go",
        "go": "Go",
        "rust": "Rust",
        "c++": "C++",
        "cpp": "C++",
        "c#": "C#",
        "csharp": "C#",
        "c-sharp": "C#",
        "java": "Java",
        "kotlin": "Kotlin",
        "swift": "Swift",
        "ruby": "Ruby",
        "php": "PHP",
        "scala": "Scala",
        "r": "R",
        "html": "HTML",
        "html5": "HTML",
        "css": "CSS",
        "css3": "CSS",

        # Frontend Frameworks & Libraries
        "react": "React",
        "react.js": "React",
        "reactjs": "React",
        "next.js": "Next.js",
        "nextjs": "Next.js",
        "next": "Next.js",
        "vue": "Vue.js",
        "vue.js": "Vue.js",
        "vuejs": "Vue.js",
        "nuxt": "Nuxt.js",
        "nuxt.js": "Nuxt.js",
        "angular": "Angular",
        "angularjs": "Angular",
        "svelte": "Svelte",
        "sveltekit": "SvelteKit",
        "tailwind": "Tailwind CSS",
        "tailwindcss": "Tailwind CSS",
        "sass": "Sass",
        "scss": "Sass",

        # Backend Frameworks
        "node": "Node.js",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "express": "Express.js",
        "express.js": "Express.js",
        "fastapi": "FastAPI",
        "fast api": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "spring": "Spring Boot",
        "spring boot": "Spring Boot",
        "springboot": "Spring Boot",
        "nest": "NestJS",
        "nest.js": "NestJS",
        "nestjs": "NestJS",
        "asp.net": ".NET",
        ".net": ".NET",
        "dotnet": ".NET",
        ".net core": ".NET",

        # Databases & Caching
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "psql": "PostgreSQL",
        "mysql": "MySQL",
        "mongo": "MongoDB",
        "mongodb": "MongoDB",
        "redis": "Redis",
        "elasticsearch": "Elasticsearch",
        "elastic search": "Elasticsearch",
        "cassandra": "Cassandra",
        "dynamodb": "DynamoDB",
        "dynamo db": "DynamoDB",
        "sqlite": "SQLite",
        "oracle": "Oracle DB",
        "mariadb": "MariaDB",

        # Cloud & DevOps
        "aws": "AWS",
        "amazon web services": "AWS",
        "gcp": "GCP",
        "google cloud": "GCP",
        "google cloud platform": "GCP",
        "azure": "Azure",
        "microsoft azure": "Azure",
        "k8s": "Kubernetes",
        "kubernetes": "Kubernetes",
        "docker": "Docker",
        "docker container": "Docker",
        "terraform": "Terraform",
        "ansible": "Ansible",
        "helm": "Helm",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "continuous integration": "CI/CD",
        "continuous deployment": "CI/CD",
        "github actions": "GitHub Actions",
        "gitlab ci": "GitLab CI",
        "jenkins": "Jenkins",
        "linux": "Linux",
        "unix": "Linux",
        "git": "Git",
        "github": "Git",
        "gitlab": "Git",

        # Architecture & Protocols
        "rest": "REST APIs",
        "restful": "REST APIs",
        "rest apis": "REST APIs",
        "rest api": "REST APIs",
        "graphql": "GraphQL",
        "grpc": "gRPC",
        "microservices": "Microservices",
        "distributed systems": "Distributed Systems",
        "system design": "System Design",
        "event-driven": "Event-Driven Architecture",
        "event driven": "Event-Driven Architecture",
        "kafka": "Apache Kafka",
        "apache kafka": "Apache Kafka",
        "rabbitmq": "RabbitMQ",

        # AI / ML / Data
        "ai": "Artificial Intelligence",
        "artificial intelligence": "Artificial Intelligence",
        "ml": "Machine Learning",
        "machine learning": "Machine Learning",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "llm": "Large Language Models",
        "llms": "Large Language Models",
        "large language models": "Large Language Models",
        "deep learning": "Deep Learning",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "scikit-learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",

        # Methodologies & Soft Skills
        "agile": "Agile",
        "scrum": "Scrum",
        "kanban": "Kanban",
        "unit testing": "Unit Testing",
        "pytest": "PyTest",
        "tdd": "Test-Driven Development",
        "test driven development": "Test-Driven Development",
    }

    # ── Negative Boundaries (§13: DO NOT conflate distinct technologies) ──
    # Sets of technologies that must NEVER be considered equivalent despite common co-occurrence
    NEGATIVE_BOUNDARIES: List[Set[str]] = [
        {"Docker", "Kubernetes"},
        {"React", "Next.js"},
        {"React", "Angular"},
        {"React", "Vue.js"},
        {"Vue.js", "Angular"},
        {"Python", "Java"},
        {"Python", "C++"},
        {"Java", "JavaScript"},
        {"C#", "C++"},
        {"PostgreSQL", "MongoDB"},
        {"MySQL", "MongoDB"},
        {"SQL", "NoSQL"},
        {"AWS", "Azure"},
        {"AWS", "GCP"},
        {"Azure", "GCP"},
        {"REST APIs", "GraphQL"},
        {"REST APIs", "gRPC"},
        {"Apache Kafka", "RabbitMQ"},
        {"FastAPI", "Django"},
        {"FastAPI", "Flask"},
    ]

    def normalize(self, term: str) -> str:
        """
        Normalize a raw term to its canonical representation.
        Example: 'JS' -> 'JavaScript', 'k8s' -> 'Kubernetes'
        """
        if not term:
            return ""
        clean = term.strip().lower()
        clean = re.sub(r'[\s_\-]+', ' ', clean)
        return self.ALIAS_MAP.get(clean, self.ALIAS_MAP.get(term.strip().lower(), term.strip()))

    def get_canonical(self, term: str) -> str:
        """Alias for normalize."""
        return self.normalize(term)

    def are_equivalent(self, term1: str, term2: str) -> bool:
        """
        Check if two terms represent the exact same technology semantically (§13).
        Respects negative boundary constraints.
        """
        if not term1 or not term2:
            return False

        t1_norm = self.normalize(term1)
        t2_norm = self.normalize(term2)

        # Direct canonical match
        if t1_norm.lower() == t2_norm.lower():
            return True

        # Check negative boundaries
        for boundary_pair in self.NEGATIVE_BOUNDARIES:
            if t1_norm in boundary_pair and t2_norm in boundary_pair:
                return False

        return False

    def is_negative_boundary(self, term1: str, term2: str) -> bool:
        """Check if two terms are explicitly forbidden from being equated."""
        t1 = self.normalize(term1)
        t2 = self.normalize(term2)
        for boundary_pair in self.NEGATIVE_BOUNDARIES:
            if t1 in boundary_pair and t2 in boundary_pair:
                return True
        return False

    def match_skill_in_text(self, target_skill: str, text: str) -> bool:
        """
        Determines if a target skill (or any of its known aliases) is present
        in the candidate text with boundary matching (§13).
        """
        if not target_skill or not text:
            return False

        canonical = self.normalize(target_skill)
        text_lower = text.lower()

        # Find all aliases that resolve to this canonical
        matching_aliases = [
            alias for alias, canon in self.ALIAS_MAP.items()
            if canon.lower() == canonical.lower()
        ]
        matching_aliases.append(target_skill.lower())
        matching_aliases.append(canonical.lower())

        for alias in set(matching_aliases):
            # Use regex boundaries (handle non-word boundary chars like c++, c#, .net)
            if alias in ["c++", "cpp"]:
                if re.search(r'(?i)(?:\bcpp\b|\bc\+\+(?!\w))', text):
                    return True
            elif alias in ["c#", "csharp"]:
                if re.search(r'(?i)(?:\bcsharp\b|\bc#(?!\w))', text):
                    return True
            elif alias in [".net", "dotnet"]:
                if re.search(r'(?i)(?:\bdotnet\b|(?<!\w)\.net(?!\w))', text):
                    return True
            elif len(alias) <= 2:
                # Strict word boundary for 1-2 char terms (e.g. 'js', 'go', 'r')
                if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                    return True
            else:
                if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                    return True

        return False

    def extract_normalized_skills(self, text: str) -> Set[str]:
        """Extract all known canonical skills present in the text."""
        if not text:
            return set()

        text_lower = text.lower()
        found = set()

        for alias, canonical in self.ALIAS_MAP.items():
            if alias in ["c++", "cpp"]:
                if re.search(r'(?i)(?:\bcpp\b|\bc\+\+(?!\w))', text):
                    found.add(canonical)
            elif alias in ["c#", "csharp"]:
                if re.search(r'(?i)(?:\bcsharp\b|\bc#(?!\w))', text):
                    found.add(canonical)
            elif alias in [".net", "dotnet"]:
                if re.search(r'(?i)(?:\bdotnet\b|(?<!\w)\.net(?!\w))', text):
                    found.add(canonical)
            elif len(alias) <= 2:
                if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                    found.add(canonical)
            else:
                if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                    found.add(canonical)

        return found


# Global singleton instance
normalization_service = SemanticNormalizationService()

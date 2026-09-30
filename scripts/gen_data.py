"""Generate synthetic resume dataset for training."""
import pandas as pd, random, json

CATEGORIES = {
    "AI/ML": ["Python", "PyTorch", "TensorFlow", "scikit-learn", "NLP", "deep learning",
               "neural networks", "transformers", "MLflow", "Hugging Face", "LLM", "BERT"],
    "Software Development": ["Java", "C++", "Python", "React", "Node.js", "Spring Boot",
                              "microservices", "REST API", "Git", "Docker", "unit testing"],
    "Data Science": ["Python", "R", "Pandas", "NumPy", "Jupyter", "data visualization",
                     "statistics", "SQL", "Tableau", "Power BI", "A/B testing"],
    "Cloud/DevOps": ["AWS", "Azure", "GCP", "Kubernetes", "Docker", "Terraform",
                     "CI/CD", "Jenkins", "Ansible", "Linux", "Bash", "monitoring"],
    "Cybersecurity": ["penetration testing", "SIEM", "firewall", "vulnerability assessment",
                      "network security", "encryption", "OWASP", "incident response", "SOC"],
    "Data Engineering": ["Apache Spark", "Kafka", "Airflow", "dbt", "PostgreSQL", "MySQL",
                          "ETL", "data pipeline", "Hadoop", "BigQuery", "Snowflake"],
}

TEMPLATES = [
    "Experienced {cat} professional with {n} years of experience. Skilled in {s1}, {s2}, and {s3}. "
    "Worked on large-scale projects involving {s4} and {s5}. Strong background in {s6}.",
    "Software engineer specializing in {cat}. Proficient with {s1}, {s2}, {s3}. "
    "Led teams delivering solutions using {s4}. Experience with {s5} and {s6}.",
    "Recent graduate with focus on {cat}. Built projects using {s1} and {s2}. "
    "Familiar with {s3}, {s4}. Internship experience with {s5} and {s6}.",
]

rows = []
for cat, skills in CATEGORIES.items():
    for _ in range(80):  # 80 per class = 480 total
        s = random.sample(skills, min(6, len(skills)))
        text = random.choice(TEMPLATES).format(
            cat=cat, n=random.randint(1, 8),
            s1=s[0], s2=s[1], s3=s[2], s4=s[3], s5=s[4], s6=s[5]
        )
        rows.append({"resume_text": text, "category": cat})

random.shuffle(rows)
df = pd.DataFrame(rows)
n = len(df)
train, val, test = df[:int(n*.7)], df[int(n*.7):int(n*.85)], df[int(n*.85):]

import os; os.makedirs("data/classification", exist_ok=True)
train.to_csv("data/classification/train.csv", index=False)
val.to_csv("data/classification/validation.csv", index=False)
test.to_csv("data/classification/test.csv", index=False)
print(f"train={len(train)}, val={len(val)}, test={len(test)}")

# Also save skill keyword map for extraction
SKILL_KEYWORDS = list({s for skills in CATEGORIES.values() for s in skills})
json.dump(SKILL_KEYWORDS, open("data/skills.json", "w"), indent=2)
print(f"Skills vocab: {len(SKILL_KEYWORDS)}")

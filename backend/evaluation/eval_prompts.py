import ollama


def evaluate_prompt_output(output: str, checks: list) -> dict:
    results = {}

    for check in checks:
        name = check['name']

        if check['type'] == 'contains':
            results[name] = (
                check['value'].lower() in output.lower()
            )

        elif check['type'] == 'not_contains':
            results[name] = (
                check['value'].lower() not in output.lower()
            )

        elif check['type'] == 'word_count':
            count = len(output.split())
            results[name] = (
                check['min'] <= count <= check['max']
            )

        elif check['type'] == 'starts_with':
            results[name] = (
                output.strip().startswith(check['value'])
            )

        elif check['type'] == 'format_match':
            results[name] = (
                check['value'] in output
            )

    score = (
        sum(results.values()) / len(results)
    ) * 5

    return {
        'checks': results,
        'score': round(score, 1)
    }


# ---------------------------------------------------
# Test Data
# ---------------------------------------------------

data = {
    'applicant_name': 'Priya Sharma',
    'monthly_income': 55000,
    'employment_type': 'Salaried',
    'employment_years': 4,
    'city': 'Bangalore',
    'loan_purpose': 'Home Renovation',
    'existing_monthly_emi': 15000,
    'foir': 27.3,
    'requested_emi': 12000,
    'post_loan_foir': 49.1,
    'cibil_score': 730,
    'has_previous_default': 0,
    'num_credit_inquiries_30d': 1,
    'is_night_application': 0
}


# ---------------------------------------------------
# Prompt Evaluations
# ---------------------------------------------------

prompts_and_checks = [

    {
        'name': 'profile_v3',

        'prompt': """
Write the Applicant Profile section of a credit memo.

Name: {applicant_name}
Income: Rs {monthly_income}/month
Employment: {employment_type} for {employment_years} years
City: {city}
Loan Purpose: {loan_purpose}

Rules:
- exactly 3 sentences
- no heading
- no disclaimer
- start with applicant name
""",

        'checks': [

            {
                'name': 'no_disclaimer',
                'type': 'not_contains',
                'value': 'disclaimer'
            },

            {
                'name': 'no_heading',
                'type': 'not_contains',
                'value': 'Applicant Profile:'
            },

            {
                'name': 'mentions_name',
                'type': 'contains',
                'value': 'Priya'
            },

            {
                'name': 'mentions_income',
                'type': 'contains',
                'value': '55,000'
            },

            {
                'name': 'reasonable_length',
                'type': 'word_count',
                'min': 30,
                'max': 100
            }
        ]
    },

    {
        'name': 'risk_v3',

        'prompt': """
Classify this loan application.

CIBIL: {cibil_score}
FOIR: {foir}%
Previous Default: {has_previous_default}
Inquiries 30d: {num_credit_inquiries_30d}

Rules:
- FOIR below 40% = LOW
- FOIR 40-55% = MEDIUM
- FOIR above 55% = HIGH

- CIBIL above 720 = GOOD
- CIBIL 650-720 = AVERAGE
- CIBIL below 650 = POOR

Respond in EXACTLY this format only:

RISK LEVEL: [LOW or MEDIUM or HIGH]
REASON 1: [one sentence]
REASON 2: [one sentence]
""",

        'checks': [

            {
                'name': 'has_risk_level',
                'type': 'contains',
                'value': 'RISK LEVEL:'
            },

            {
                'name': 'has_reason1',
                'type': 'contains',
                'value': 'REASON 1:'
            },

            {
                'name': 'has_reason2',
                'type': 'contains',
                'value': 'REASON 2:'
            },

            {
                'name': 'correct_risk',
                'type': 'contains',
                'value': 'LOW'
            },

            {
                'name': 'no_extra_text',
                'type': 'word_count',
                'min': 10,
                'max': 60
            }
        ]
    }
]


# ---------------------------------------------------
# Run Evaluations
# ---------------------------------------------------

for item in prompts_and_checks:

    print("\n" + "=" * 50)
    print(f"TESTING: {item['name']}")
    print("=" * 50)

    response = ollama.chat(
        model='llama3',
        messages=[
            {
                'role': 'user',
                'content': item['prompt'].format(**data)
            }
        ]
    )

    output = response['message']['content']

    print("\nMODEL OUTPUT:\n")
    print(output)

    result = evaluate_prompt_output(
        output,
        item['checks']
    )

    print("\nCHECK RESULTS:\n")

    for check_name, passed in result['checks'].items():

        status = "PASS" if passed else "FAIL"
        print(f"{check_name}: {status}")

    print(f"\nAUTO SCORE: {result['score']}/5")

    # Save scores to file
    with open("scores.txt", "a") as file:

        file.write(
            f"{item['name']} : "
            f"{result['score']}/5\n"
        )

print("\nAll prompt evaluations completed.")

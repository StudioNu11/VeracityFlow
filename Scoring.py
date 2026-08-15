import json
import threading
from gemini_client import client
from gemini_client_2 import client2
from google.genai import types


MODEL = "gemini-3.5-flash-lite"

MAX_ATTEMPTS = 3
MAX_DIFFERENCE = 10


SYSTEM_PROMPT = """You are VeracityFlow, an expert digital trust and fact verification engine.

Your task is to evaluate the credibility of a claim using ONLY the evidence provided.

Rules:
- Treat the supplied evidence as your ONLY source of truth.
- Do NOT rely on prior knowledge, memory, or assumptions.
- Weigh the quality, consistency, relevance, and agreement of the evidence.
- Ignore sensational language, opinions, and unsupported statements.
- If multiple credible sources agree, increase the trust rating.
- If credible sources directly contradict the claim, decrease the trust rating.
- If the evidence is mixed or conflicting, assign a moderate trust rating.
- If there is insufficient evidence, lower the confidence score.
- Never invent facts or cite information not present in the supplied evidence.
- The reasoning must be objective and exactly 1 sentence.

Scoring Guidelines:

trust_rating (0-100)
0-10   : Demonstrably false.
11-30  : Mostly false with little supporting evidence.
31-49  : More false than true or evidence strongly conflicts.
50     : Inconclusive / balanced evidence.
51-69  : More true than false but with notable caveats.
70-89  : Well supported by multiple credible sources.
90-100 : Overwhelmingly supported by consistent, high-quality evidence.

confidence_score (0-100)
This measures confidence in YOUR assessment, NOT the truth of the claim.

Increase confidence when:
- Multiple independent evidence items agree.
- Evidence is directly relevant.
- Evidence is detailed and specific.
- Evidence is internally consistent.

Decrease confidence when:
- Evidence conflicts.
- Evidence is vague or incomplete.
- Evidence is speculative.
- Evidence is unrelated.
- Too few evidence items are provided.

Output ONLY valid JSON.

The JSON must contain EXACTLY these fields:

{
    "trust_rating": integer,
    "confidence_score": integer,
    "reasoning": "string"
}
"""


def score_once(veracity_input, result_container, index, gemini_client):

    try:
        response = gemini_client.models.generate_content(
            model=MODEL,
            contents=[
                SYSTEM_PROMPT + "\n\n" + veracity_input
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        result = json.loads(response.text)

        trust = result.get("trust_rating")
        confidence = result.get("confidence_score")

        if not isinstance(trust, int) or not 0 <= trust <= 100:
            raise ValueError("Invalid trust_rating")

        if not isinstance(confidence, int) or not 0 <= confidence <= 100:
            raise ValueError("Invalid confidence_score")

        result_container[index] = result

    except Exception as e:
        result_container[index] = e


def run_two_scorers(veracity_input):

    results = [None, None]

    # Scorer 1 → Client 1
    thread1 = threading.Thread(
        target=score_once,
        args=(veracity_input, results, 0, client)
    )

    # Scorer 2 → Client 2
    thread2 = threading.Thread(
        target=score_once,
        args=(veracity_input, results, 1, client2)
    )

    thread1.start()
    thread2.start()

    # Wait for both requests.
    thread1.join()
    thread2.join()

    # Check whether either request failed.
    if isinstance(results[0], Exception):
        raise results[0]

    if isinstance(results[1], Exception):
        raise results[1]

    return results[0], results[1]


def scoring(veracity_input):

    best_pair = None
    best_difference = float("inf")

    for attempt in range(1, MAX_ATTEMPTS + 1):

        result1, result2 = run_two_scorers(veracity_input)

        trust1 = result1["trust_rating"]
        trust2 = result2["trust_rating"]

        difference = abs(trust1 - trust2)

        # Remember the closest pair we've seen.
        if difference < best_difference:
            best_difference = difference
            best_pair = (result1, result2)

        # Good enough agreement.
        if difference <= MAX_DIFFERENCE:

            final_trust = round(
                (trust1 + trust2) / 2
            )

            final_confidence = round(
                (
                    result1["confidence_score"] +
                    result2["confidence_score"]
                ) / 2
            )

            return {
                "trust_rating": final_trust,
                "confidence_score": final_confidence,
                "reasoning": result1["reasoning"]
            }

    # Maximum attempts reached.
    result1, result2 = best_pair

    final_trust = round(
        (
            result1["trust_rating"] +
            result2["trust_rating"]
        ) / 2
    )

    final_confidence = round(
        (
            result1["confidence_score"] +
            result2["confidence_score"]
        ) / 2
    )

    return {
        "trust_rating": final_trust,
        "confidence_score": final_confidence,
        "reasoning": result1["reasoning"]
    }

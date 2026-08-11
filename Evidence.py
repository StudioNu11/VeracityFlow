from concurrent.futures import ThreadPoolExecutor
from tavily_client import tavily

def evidence(data):
    def search_query(query):
        results = tavily.search(query, include_answer=True)
        return {
            "answer": results.get("answer", "")
        }


    with ThreadPoolExecutor(max_workers=4) as executor:
        evidence = list(executor.map(search_query, data["search_queries"]))

    evidence_text = " ".join(
        f"{i+1}. {item['answer']}"
        for i, item in enumerate(evidence)
    )

    veracity_input = (
        f"Claim: {data['claim']} "
        f"Evidence: {evidence_text}"
    ).replace('"', "'")
    print(veracity_input)
    return veracity_input

from intelligence.query_engine import ask

questions = [
    "Which clients are worried about market volatility?",
    "Who discussed inheritance tax?",
    "Which clients mentioned pension fees?"
]

for q in questions:
    print("\n🔍 QUESTION:", q)
    results = ask(q)

    for r in results:
        print("➡", r["client"])

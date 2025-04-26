import agents
import json


queries = [
    "What is the capital of France?",
    "dollar prices",
    "What is the weather like today?",
    "Who won the last World Series?",
    "Explain quantum computing in simple terms.",
    "What are the benefits of meditation?",
    "How do I make a perfect cup of coffee?",
    "What is the meaning of life?",
    "Can you recommend a good book to read?",
    "What is the fastest land animal?",
    "How was the Effiel Tower built?"
]

def test_query_response():
    testResponse = []
    for query in queries:
        print(f"Running test for query: {query}")
        response = agents.run_agents(query)
        testResponse.append(
            {
                "query": query,
                "response": response
            }
        )
    
    with open("testResponse.json", "a") as f:
        json.dump(testResponse, f, indent = 4)


if __name__ == "__main__":
    test_query_response()
    print("All tests completed. Check testResponse.json for results.")
# This script runs a series of test queries against the agent and saves the responses to a JSON file.
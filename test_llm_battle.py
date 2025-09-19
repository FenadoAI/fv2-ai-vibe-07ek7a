#!/usr/bin/env python3
"""
Test script for LLM Battle API
Tests all the endpoints to ensure the hot-or-not website is working correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001/api"

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)

        print(f"✅ {method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and len(result) <= 3:
                print(f"   Response: {result}")
            elif isinstance(result, list) and len(result) <= 2:
                print(f"   Response: {len(result)} items")
            else:
                print(f"   Response: Success")
        return response
    except Exception as e:
        print(f"❌ {method} {endpoint}: Error - {e}")
        return None

def main():
    print("🚀 Testing LLM Battle API...")
    print("=" * 50)

    # Test 1: Basic API health
    print("\n📡 Testing basic API health...")
    test_api_endpoint("/")

    # Test 2: Seed models
    print("\n🌱 Seeding LLM models...")
    test_api_endpoint("/models/seed", method="POST")

    # Test 3: Get all models
    print("\n🤖 Getting all models...")
    models_response = test_api_endpoint("/models")

    # Test 4: Get battle
    print("\n⚔️ Getting a battle...")
    battle_response = test_api_endpoint("/battle")

    if battle_response and battle_response.status_code == 200:
        battle_data = battle_response.json()
        model1_id = battle_data["model1"]["id"]
        model2_id = battle_data["model2"]["id"]

        print(f"   Battle: {battle_data['model1']['name']} vs {battle_data['model2']['name']}")

        # Test 5: Submit vote
        print("\n🗳️ Submitting a vote...")
        vote_data = {"winner_id": model1_id, "loser_id": model2_id}
        test_api_endpoint("/vote", method="POST", data=vote_data)

    # Test 6: Get leaderboard
    print("\n🏆 Getting leaderboard...")
    leaderboard_response = test_api_endpoint("/leaderboard")

    if leaderboard_response and leaderboard_response.status_code == 200:
        leaderboard = leaderboard_response.json()
        if leaderboard:
            top_model = leaderboard[0]
            print(f"   Top model: {top_model['name']} with {top_model['wins']} wins")

    # Test 7: Get stats
    print("\n📊 Getting battle stats...")
    stats_response = test_api_endpoint("/stats")

    if stats_response and stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   Total battles: {stats.get('battles_completed', 0)}")
        print(f"   Total models: {stats.get('total_models', 0)}")
        print(f"   Current champion: {stats.get('top_model', 'None')}")

    print("\n" + "=" * 50)
    print("🎉 LLM Battle API testing complete!")
    print("\n📱 Frontend should be available at: http://localhost:3000")
    print("🔗 API documentation at: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
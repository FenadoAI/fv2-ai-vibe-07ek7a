import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import { Trophy, Zap, Crown, Users, TrendingUp, Brain, Sparkles } from "lucide-react";

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API = `${API_BASE}/api`;

const BattleArena = () => {
  const [battle, setBattle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [showResults, setShowResults] = useState(false);

  const fetchBattle = async () => {
    setLoading(true);
    setShowResults(false);
    try {
      const response = await axios.get(`${API}/battle`);
      setBattle(response.data);
    } catch (e) {
      console.error("Error fetching battle:", e);
    } finally {
      setLoading(false);
    }
  };

  const submitVote = async (winnerId, loserId) => {
    try {
      await axios.post(`${API}/vote`, {
        winner_id: winnerId,
        loser_id: loserId
      });
      setShowResults(true);
      fetchStats();
      // Fetch new battle after a delay
      setTimeout(fetchBattle, 2000);
    } catch (e) {
      console.error("Error submitting vote:", e);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (e) {
      console.error("Error fetching stats:", e);
    }
  };

  useEffect(() => {
    fetchBattle();
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-center">
          <Brain className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold mb-2">Loading Battle...</h2>
          <p className="text-purple-200">Finding worthy opponents</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white">
      {/* Header */}
      <div className="text-center py-8 px-4">
        <div className="flex items-center justify-center mb-4">
          <Brain className="w-12 h-12 mr-3 text-purple-300" />
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">
            LLM Battle
          </h1>
          <Sparkles className="w-12 h-12 ml-3 text-pink-300" />
        </div>
        <p className="text-xl text-purple-200 mb-2">Choose the superior AI model</p>
        <div className="flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center">
            <Trophy className="w-4 h-4 mr-1" />
            <span>{stats.battles_completed || 0} Battles</span>
          </div>
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-1" />
            <span>{stats.total_models || 0} Models</span>
          </div>
          <div className="flex items-center">
            <Crown className="w-4 h-4 mr-1" />
            <span>Champion: {stats.top_model || "TBD"}</span>
          </div>
        </div>
      </div>

      {battle && (
        <div className="max-w-7xl mx-auto px-4 pb-8">
          <div className="grid md:grid-cols-2 gap-8 items-stretch">
            {/* Model 1 */}
            <Card className="bg-white/10 backdrop-blur-lg border-white/20 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
              <CardHeader className="text-center">
                <div className="w-full h-48 mb-4 rounded-lg overflow-hidden">
                  <img
                    src={battle.model1.image_url}
                    alt={battle.model1.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardTitle className="text-2xl font-bold text-white">{battle.model1.name}</CardTitle>
                <CardDescription className="text-purple-200">
                  by {battle.model1.provider}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-200 text-center">{battle.model1.description}</p>

                <div className="flex flex-wrap gap-2 justify-center">
                  {battle.model1.capabilities.map((capability, index) => (
                    <Badge key={index} variant="secondary" className="bg-purple-700/50 text-white">
                      {capability}
                    </Badge>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="bg-white/10 rounded-lg p-3">
                    <div className="text-2xl font-bold text-green-300">{battle.model1.wins}</div>
                    <div className="text-xs text-gray-300">Wins</div>
                  </div>
                  <div className="bg-white/10 rounded-lg p-3">
                    <div className="text-2xl font-bold text-blue-300">{battle.model1.win_rate}%</div>
                    <div className="text-xs text-gray-300">Win Rate</div>
                  </div>
                </div>

                <Button
                  onClick={() => submitVote(battle.model1.id, battle.model2.id)}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 text-lg transition-all duration-300"
                  disabled={showResults}
                >
                  {showResults ? "Vote Recorded!" : "Choose This Model"}
                </Button>
              </CardContent>
            </Card>

            {/* VS Divider */}
            <div className="hidden md:flex absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-full p-6 shadow-2xl">
                <span className="text-2xl font-bold text-white">VS</span>
              </div>
            </div>

            {/* Model 2 */}
            <Card className="bg-white/10 backdrop-blur-lg border-white/20 hover:bg-white/15 transition-all duration-300 transform hover:scale-105">
              <CardHeader className="text-center">
                <div className="w-full h-48 mb-4 rounded-lg overflow-hidden">
                  <img
                    src={battle.model2.image_url}
                    alt={battle.model2.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <CardTitle className="text-2xl font-bold text-white">{battle.model2.name}</CardTitle>
                <CardDescription className="text-purple-200">
                  by {battle.model2.provider}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-200 text-center">{battle.model2.description}</p>

                <div className="flex flex-wrap gap-2 justify-center">
                  {battle.model2.capabilities.map((capability, index) => (
                    <Badge key={index} variant="secondary" className="bg-purple-700/50 text-white">
                      {capability}
                    </Badge>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="bg-white/10 rounded-lg p-3">
                    <div className="text-2xl font-bold text-green-300">{battle.model2.wins}</div>
                    <div className="text-xs text-gray-300">Wins</div>
                  </div>
                  <div className="bg-white/10 rounded-lg p-3">
                    <div className="text-2xl font-bold text-blue-300">{battle.model2.win_rate}%</div>
                    <div className="text-xs text-gray-300">Win Rate</div>
                  </div>
                </div>

                <Button
                  onClick={() => submitVote(battle.model2.id, battle.model1.id)}
                  className="w-full bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700 text-white font-bold py-3 text-lg transition-all duration-300"
                  disabled={showResults}
                >
                  {showResults ? "Vote Recorded!" : "Choose This Model"}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Mobile VS */}
          <div className="md:hidden flex justify-center my-8">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-full p-4">
              <span className="text-xl font-bold text-white">VS</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get(`${API}/leaderboard`);
      setLeaderboard(response.data);
    } catch (e) {
      console.error("Error fetching leaderboard:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-center">
          <Trophy className="w-16 h-16 mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold mb-2">Loading Leaderboard...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <Trophy className="w-16 h-16 mx-auto mb-4 text-yellow-400" />
          <h1 className="text-4xl md:text-5xl font-bold mb-2">Leaderboard</h1>
          <p className="text-purple-200">The ultimate AI model rankings</p>
        </div>

        <div className="space-y-4">
          {leaderboard.map((model, index) => (
            <Card key={model.id} className="bg-white/10 backdrop-blur-lg border-white/20">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl ${
                      index === 0 ? 'bg-yellow-500 text-yellow-900' :
                      index === 1 ? 'bg-gray-300 text-gray-800' :
                      index === 2 ? 'bg-orange-500 text-orange-900' :
                      'bg-purple-600 text-white'
                    }`}>
                      {index + 1}
                    </div>
                  </div>

                  <div className="flex-shrink-0">
                    <img
                      src={model.image_url}
                      alt={model.name}
                      className="w-16 h-16 rounded-lg object-cover"
                    />
                  </div>

                  <div className="flex-grow">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="text-xl font-bold text-white">{model.name}</h3>
                      {index === 0 && <Crown className="w-5 h-5 text-yellow-400" />}
                    </div>
                    <p className="text-purple-200 text-sm">{model.provider}</p>
                  </div>

                  <div className="text-right space-y-1">
                    <div className="text-2xl font-bold text-green-300">{model.wins}</div>
                    <div className="text-sm text-gray-300">wins</div>
                  </div>

                  <div className="text-right space-y-1">
                    <div className="text-2xl font-bold text-blue-300">{model.win_rate}%</div>
                    <div className="text-sm text-gray-300">win rate</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

const Navigation = () => {
  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
      <div className="bg-white/10 backdrop-blur-lg rounded-full p-1 border border-white/20">
        <div className="flex space-x-1">
          <Button
            onClick={() => window.location.href = '/'}
            variant="ghost"
            className="rounded-full px-6 text-white hover:bg-white/20"
          >
            <Zap className="w-4 h-4 mr-2" />
            Battle
          </Button>
          <Button
            onClick={() => window.location.href = '/leaderboard'}
            variant="ghost"
            className="rounded-full px-6 text-white hover:bg-white/20"
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            Leaderboard
          </Button>
        </div>
      </div>
    </div>
  );
};

function App() {
  // Initialize models on first load
  const initializeModels = async () => {
    try {
      await axios.post(`${API}/models/seed`);
      console.log("Models initialized");
    } catch (e) {
      console.error("Error initializing models:", e);
    }
  };

  useEffect(() => {
    initializeModels();
  }, []);

  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<BattleArena />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
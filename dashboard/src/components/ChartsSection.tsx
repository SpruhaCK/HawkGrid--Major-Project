import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, PieChart as PieChartIcon, Globe } from "lucide-react";

const attackTrendData = [
  { time: "00:00", attacks: 12 },
  { time: "02:00", attacks: 8 },
  { time: "04:00", attacks: 5 },
  { time: "06:00", attacks: 15 },
  { time: "08:00", attacks: 22 },
  { time: "10:00", attacks: 18 },
  { time: "12:00", attacks: 35 },
  { time: "14:00", attacks: 45 },
  { time: "16:00", attacks: 38 },
  { time: "18:00", attacks: 42 },
  { time: "20:00", attacks: 28 },
  { time: "22:00", attacks: 20 }
];

const attackTypeData = [
  { name: "SQL Injection", value: 35, color: "#ef4444" },
  { name: "DDoS", value: 25, color: "#f97316" },
  { name: "Phishing", value: 20, color: "#eab308" },
  { name: "Suspicious Login", value: 20, color: "#06b6d4" }
];

const locationData = [
  { country: "Germany", attacks: 45, intensity: "high" },
  { country: "Nigeria", attacks: 38, intensity: "high" },
  { country: "India", attacks: 32, intensity: "medium" },
  { country: "Russia", attacks: 28, intensity: "medium" },
  { country: "China", attacks: 25, intensity: "medium" },
  { country: "Brazil", attacks: 15, intensity: "low" }
];

export function ChartsSection() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Attack Trends Chart */}
      <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-cyan-400" />
            <span>Attack Trends (24h)</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={attackTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="time" 
                stroke="#9ca3af"
                fontSize={12}
              />
              <YAxis 
                stroke="#9ca3af"
                fontSize={12}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f3f4f6'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="attacks" 
                stroke="#06b6d4" 
                strokeWidth={2}
                dot={{ fill: '#06b6d4', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#06b6d4', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Attack Types Pie Chart */}
      <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <PieChartIcon className="h-5 w-5 text-green-400" />
            <span>Attack Types</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={attackTypeData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {attackTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#f3f4f6'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {attackTypeData.map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-gray-300">{item.name}</span>
                </div>
                <span className="text-gray-400">{item.value}%</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* World Map Heatmap */}
      <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="h-5 w-5 text-purple-400" />
            <span>Attack Origins</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {locationData.map((location, index) => {
              const getIntensityColor = (intensity: string) => {
                switch (intensity) {
                  case "high": return "bg-red-500";
                  case "medium": return "bg-orange-500";
                  case "low": return "bg-yellow-500";
                  default: return "bg-gray-500";
                }
              };

              const getIntensityBg = (intensity: string) => {
                switch (intensity) {
                  case "high": return "bg-red-950/30 border-red-500/30";
                  case "medium": return "bg-orange-950/30 border-orange-500/30";
                  case "low": return "bg-yellow-950/30 border-yellow-500/30";
                  default: return "bg-gray-950/30 border-gray-500/30";
                }
              };

              return (
                <div 
                  key={index}
                  className={`flex items-center justify-between p-3 rounded border ${getIntensityBg(location.intensity)}`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${getIntensityColor(location.intensity)}`}></div>
                    <span className="text-gray-300">{location.country}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">{location.attacks} attacks</div>
                    <div className="text-xs text-gray-500 capitalize">{location.intensity}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
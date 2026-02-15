// import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
// import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
// import { TrendingUp, PieChart as PieChartIcon, Globe } from "lucide-react";

// const attackTrendData = [
//   { time: "00:00", attacks: 12 },
//   { time: "02:00", attacks: 8 },
//   { time: "04:00", attacks: 5 },
//   { time: "06:00", attacks: 15 },
//   { time: "08:00", attacks: 22 },
//   { time: "10:00", attacks: 18 },
//   { time: "12:00", attacks: 35 },
//   { time: "14:00", attacks: 45 },
//   { time: "16:00", attacks: 38 },
//   { time: "18:00", attacks: 42 },
//   { time: "20:00", attacks: 28 },
//   { time: "22:00", attacks: 20 }
// ];

// const attackTypeData = [
//   { name: "SQL Injection", value: 35, color: "#ef4444" },
//   { name: "DDoS", value: 25, color: "#f97316" },
//   { name: "Phishing", value: 20, color: "#eab308" },
//   { name: "Suspicious Login", value: 20, color: "#06b6d4" }
// ];

// const locationData = [
//   { country: "Germany", attacks: 45, intensity: "high", target: "aws" },
//   { country: "Nigeria", attacks: 38, intensity: "high", target: "aws" },
//   { country: "India", attacks: 32, intensity: "medium", target: "azure" },
//   { country: "Russia", attacks: 28, intensity: "medium", target: "azure" },
//   { country: "China", attacks: 25, intensity: "medium", target: "aws" },
//   { country: "Brazil", attacks: 15, intensity: "low", target: "azure" }
// ];

// export function ChartsSection() {
//   return (
//     <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//       {/* Attack Trends Chart */}
//       <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
//         <CardHeader>
//           <CardTitle className="flex items-center space-x-2">
//             <TrendingUp className="h-5 w-5 text-cyan-400" />
//             <span>Attack Trends (24h)</span>
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           <ResponsiveContainer width="100%" height={200}>
//             <LineChart data={attackTrendData}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
//               <XAxis 
//                 dataKey="time" 
//                 stroke="#9ca3af"
//                 fontSize={12}
//               />
//               <YAxis 
//                 stroke="#9ca3af"
//                 fontSize={12}
//               />
//               <Tooltip 
//                 contentStyle={{ 
//                   backgroundColor: '#1f2937', 
//                   border: '1px solid #374151',
//                   borderRadius: '8px',
//                   color: '#f3f4f6'
//                 }}
//               />
//               <Line 
//                 type="monotone" 
//                 dataKey="attacks" 
//                 stroke="#06b6d4" 
//                 strokeWidth={2}
//                 dot={{ fill: '#06b6d4', strokeWidth: 2, r: 4 }}
//                 activeDot={{ r: 6, stroke: '#06b6d4', strokeWidth: 2 }}
//               />
//             </LineChart>
//           </ResponsiveContainer>
//         </CardContent>
//       </Card>

//       {/* Attack Types Pie Chart */}
//       <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
//         <CardHeader>
//           <CardTitle className="flex items-center space-x-2">
//             <PieChartIcon className="h-5 w-5 text-green-400" />
//             <span>Attack Types</span>
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           <ResponsiveContainer width="100%" height={200}>
//             <PieChart>
//               <Pie
//                 data={attackTypeData}
//                 cx="50%"
//                 cy="50%"
//                 innerRadius={40}
//                 outerRadius={80}
//                 paddingAngle={5}
//                 dataKey="value"
//               >
//                 {attackTypeData.map((entry, index) => (
//                   <Cell key={`cell-${index}`} fill={entry.color} />
//                 ))}
//               </Pie>
//               <Tooltip 
//                 contentStyle={{ 
//                   backgroundColor: '#1f2937',
//                   border: '1px solid #374151',
//                   borderRadius: '8px',
//                   color: '#ffffff'
//                 }}
//                 itemStyle={{ color: '#ffffff' }}
//               />
//             </PieChart>
//           </ResponsiveContainer>
//           <div className="mt-4 space-y-2">
//             {attackTypeData.map((item, index) => (
//               <div key={index} className="flex items-center justify-between text-sm">
//                 <div className="flex items-center space-x-2">
//                   <div 
//                     className="w-3 h-3 rounded-full" 
//                     style={{ backgroundColor: item.color }}
//                   ></div>
//                   <span className="text-gray-300">{item.name}</span>
//                 </div>
//                 <span className="text-gray-400">{item.value}%</span>
//               </div>
//             ))}
//           </div>
//         </CardContent>
//       </Card>

//       {/* World Map Heatmap */}
//       <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
//         <CardHeader>
//           <CardTitle className="flex items-center space-x-2">
//             <Globe className="h-5 w-5 text-purple-400" />
//             <span>Global Attack Map</span>
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           {/* Legend */}
//           <div className="flex items-center justify-center space-x-4 mb-4 pb-3 border-b border-gray-700/50">
//             <div className="flex items-center space-x-2">
//               <div className="w-3 h-[2px] bg-[#F59E0B]"></div>
//               <span className="text-xs text-gray-400">AWS Traffic</span>
//             </div>
//             <div className="flex items-center space-x-2">
//               <div className="w-3 h-[2px] bg-[#06B6D4]"></div>
//               <span className="text-xs text-gray-400">Azure Traffic</span>
//             </div>
//           </div>

//           <div className="space-y-2">
//             {locationData.map((location, index) => {
//               const getIntensityColor = (intensity: string) => {
//                 switch (intensity) {
//                   case "high": return "bg-[#EF4444]";
//                   case "medium": return "bg-[#F59E0B]";
//                   case "low": return "bg-[#F59E0B]/50";
//                   default: return "bg-gray-500";
//                 }
//               };

//               const getTargetColor = (target: string) => {
//                 return target === "aws" ? "border-[#F59E0B]/50" : "border-[#06B6D4]/50";
//               };

//               const getTargetBg = (target: string) => {
//                 return target === "aws" ? "bg-[#F59E0B]/10" : "bg-[#06B6D4]/10";
//               };

//               const getTrafficLineColor = (target: string) => {
//                 return target === "aws" ? "bg-[#F59E0B]" : "bg-[#06B6D4]";
//               };

//               return (
//                 <div 
//                   key={index}
//                   className={`p-3 rounded-lg border ${getTargetBg(location.target)} ${getTargetColor(location.target)} hover:border-opacity-100 transition-all relative`}
//                 >
//                   {/* Traffic line indicator */}
//                   <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-lg ${getTrafficLineColor(location.target)}`}></div>
                  
//                   <div className="flex items-center justify-between">
//                     <div className="flex items-center space-x-3">
//                       <div className={`w-2 h-2 rounded-full ${getIntensityColor(location.intensity)} shadow-lg`}></div>
//                       <div>
//                         <div className="text-sm text-gray-300">{location.country}</div>
//                         <div className="text-xs text-gray-500">
//                           → {location.target === "aws" ? "AWS Node" : "Azure Node"}
//                         </div>
//                       </div>
//                     </div>
//                     <div className="text-right">
//                       <div className="text-sm font-mono text-gray-300">{location.attacks}</div>
//                       <div className="text-xs text-gray-500 capitalize">{location.intensity}</div>
//                     </div>
//                   </div>
//                 </div>
//               );
//             })}
//           </div>
//         </CardContent>
//       </Card>
//     </div>
//   );
// }

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, PieChart as PieChartIcon, Globe, CalendarDays } from "lucide-react";

// --- STATIC DATA (Global Map - untouched) ---
const locationData = [
  { country: "Germany", attacks: 45, intensity: "high", target: "aws" },
  { country: "Nigeria", attacks: 38, intensity: "high", target: "aws" },
  { country: "India", attacks: 32, intensity: "medium", target: "azure" },
  { country: "Russia", attacks: 28, intensity: "medium", target: "azure" },
  { country: "China", attacks: 25, intensity: "medium", target: "aws" },
  { country: "Brazil", attacks: 15, intensity: "low", target: "azure" }
];

// --- COLORS FOR PIE CHART ---
const PIE_COLORS = ["#ef4444", "#f97316", "#eab308", "#06b6d4", "#8b5cf6", "#10b981"];

// --- HELPER: Get Last 7 Days ---
const getLast7Days = () => {
  const dates = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    dates.push(d.toISOString().split('T')[0]); // YYYY-MM-DD
  }
  return dates.reverse(); // Oldest to Newest
};

export function ChartsSection() {
  const [logs, setLogs] = useState<any[]>([]);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>("");
  
  const [trendData, setTrendData] = useState<any[]>([]);
  const [typeData, setTypeData] = useState<any[]>([]);

  // 1. INITIALIZE DATES
  useEffect(() => {
    const last7 = getLast7Days();
    setAvailableDates(last7);
    setSelectedDate(last7[last7.length - 1]); // Default to Today
  }, []);

  // 2. FETCH LOGS (Polling)
  const fetchLogs = async () => {
    try {
      const response = await fetch("http://localhost:3001/api/live-logs");
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error("Error fetching charts data:", error);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000); // Update charts every 5s
    return () => clearInterval(interval);
  }, []);

  // 3. PROCESS DATA WHEN DATE OR LOGS CHANGE
  useEffect(() => {
    if (!selectedDate || logs.length === 0) return;

    // Filter logs for the selected date
    const dailyLogs = logs.filter((log: any) => {
      const timestamp = log.incident?.timestamp || "";
      return timestamp.startsWith(selectedDate);
    });

    // --- A. PROCESS TRENDS (24h) ---
    // Initialize 24 hours with 0 attacks
    const hoursMap = new Array(24).fill(0).map((_, i) => ({
      time: `${String(i).padStart(2, '0')}:00`,
      attacks: 0
    }));

    dailyLogs.forEach((log: any) => {
      const timestamp = log.incident?.timestamp;
      if (timestamp) {
        const hour = new Date(timestamp).getHours();
        if (hoursMap[hour]) {
          hoursMap[hour].attacks += 1;
        }
      }
    });
    setTrendData(hoursMap);

    // --- B. PROCESS ATTACK TYPES ---
    const typeCount: Record<string, number> = {};
    dailyLogs.forEach((log: any) => {
      const type = log.incident?.attack_type || "Unknown";
      typeCount[type] = (typeCount[type] || 0) + 1;
    });

    const processedTypes = Object.keys(typeCount).map((key, index) => ({
      name: key,
      value: typeCount[key],
      color: PIE_COLORS[index % PIE_COLORS.length]
    })).sort((a, b) => b.value - a.value); // Sort highest first

    setTypeData(processedTypes);

  }, [logs, selectedDate]);


  return (
    <div className="space-y-6">
      
      {/* --- DATE FILTER PANEL --- */}
      <div className="flex items-center space-x-4 overflow-x-auto pb-2 scrollbar-hide">
        <div className="flex items-center text-gray-400 text-sm whitespace-nowrap">
            <CalendarDays className="h-4 w-4 mr-2" />
            <span>Filter Date:</span>
        </div>
        <div className="flex space-x-2">
            {availableDates.map((date) => {
                const isSelected = date === selectedDate;
                const displayDate = new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                const isToday = date === new Date().toISOString().split('T')[0];

                return (
                    <button
                        key={date}
                        onClick={() => setSelectedDate(date)}
                        className={`
                            px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-200 border
                            ${isSelected 
                                ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.3)]" 
                                : "bg-gray-800/50 text-gray-400 border-gray-700 hover:bg-gray-700 hover:text-gray-200"
                            }
                        `}
                    >
                        {isToday ? "Today" : displayDate}
                    </button>
                );
            })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* --- DYNAMIC ATTACK TRENDS CHART --- */}
        <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-cyan-400" />
                <span>Attack Trends (24h)</span>
              </div>
              <span className="text-xs font-mono text-gray-500">{selectedDate}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="time" 
                  stroke="#9ca3af"
                  fontSize={10}
                  tickMargin={10}
                  interval={3} // Show every 3rd hour to avoid clutter
                />
                <YAxis 
                  stroke="#9ca3af"
                  fontSize={10}
                  allowDecimals={false}
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
                  dot={false}
                  activeDot={{ r: 6, stroke: '#06b6d4', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* --- DYNAMIC ATTACK TYPES PIE CHART --- */}
        <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <PieChartIcon className="h-5 w-5 text-green-400" />
                <span>Attack Types</span>
              </div>
              <span className="text-xs font-mono text-gray-500">{selectedDate}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {typeData.length === 0 ? (
                <div className="h-[200px] flex items-center justify-center text-gray-500 text-sm italic">
                    No data for this date
                </div>
            ) : (
                <>
                <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                    <Pie
                    data={typeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    >
                    {typeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                    </Pie>
                    <Tooltip 
                    contentStyle={{ 
                        backgroundColor: '#1f2937',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        color: '#ffffff'
                    }}
                    itemStyle={{ color: '#ffffff' }}
                    />
                </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2 max-h-[100px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700">
                {typeData.map((item, index) => (
                    <div key={index} className="flex items-center justify-between text-sm px-2">
                    <div className="flex items-center space-x-2">
                        <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: item.color }}
                        ></div>
                        <span className="text-gray-300">{item.name}</span>
                    </div>
                    <span className="text-gray-400 font-mono">{item.value}</span>
                    </div>
                ))}
                </div>
                </>
            )}
          </CardContent>
        </Card>

        {/* --- STATIC WORLD MAP (Unchanged) --- */}
        <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-purple-400" />
              <span>Global Attack Map</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Legend */}
            <div className="flex items-center justify-center space-x-4 mb-4 pb-3 border-b border-gray-700/50">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-[2px] bg-[#F59E0B]"></div>
                <span className="text-xs text-gray-400">AWS Traffic</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-[2px] bg-[#06B6D4]"></div>
                <span className="text-xs text-gray-400">Azure Traffic</span>
              </div>
            </div>

            <div className="space-y-2">
              {locationData.map((location, index) => {
                const getIntensityColor = (intensity: string) => {
                  switch (intensity) {
                    case "high": return "bg-[#EF4444]";
                    case "medium": return "bg-[#F59E0B]";
                    case "low": return "bg-[#F59E0B]/50";
                    default: return "bg-gray-500";
                  }
                };

                const getTargetColor = (target: string) => {
                  return target === "aws" ? "border-[#F59E0B]/50" : "border-[#06B6D4]/50";
                };

                const getTargetBg = (target: string) => {
                  return target === "aws" ? "bg-[#F59E0B]/10" : "bg-[#06B6D4]/10";
                };

                const getTrafficLineColor = (target: string) => {
                  return target === "aws" ? "bg-[#F59E0B]" : "bg-[#06B6D4]";
                };

                return (
                  <div 
                    key={index}
                    className={`p-3 rounded-lg border ${getTargetBg(location.target)} ${getTargetColor(location.target)} hover:border-opacity-100 transition-all relative`}
                  >
                    {/* Traffic line indicator */}
                    <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-lg ${getTrafficLineColor(location.target)}`}></div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${getIntensityColor(location.intensity)} shadow-lg`}></div>
                        <div>
                          <div className="text-sm text-gray-300">{location.country}</div>
                          <div className="text-xs text-gray-500">
                            → {location.target === "aws" ? "AWS Node" : "Azure Node"}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-mono text-gray-300">{location.attacks}</div>
                        <div className="text-xs text-gray-500 capitalize">{location.intensity}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
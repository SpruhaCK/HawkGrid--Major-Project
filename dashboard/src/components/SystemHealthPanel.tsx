import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Activity } from "lucide-react";

const systemMetrics = [
  {
    name: "CPU Usage",
    value: 68,
    color: "bg-[#F59E0B]",
    textColor: "text-[#F59E0B]"
  },
  {
    name: "Memory",
    value: 82,
    color: "bg-[#EF4444]",
    textColor: "text-[#EF4444]"
  },
  {
    name: "Network",
    value: 45,
    color: "bg-[#22C55E]",
    textColor: "text-[#22C55E]"
  }
];

export function SystemHealthPanel() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-[#06B6D4]" />
          <span>Orchestrator System Health</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {systemMetrics.map((metric) => (
            <div key={metric.name}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-300">{metric.name}</span>
                <span className={`text-sm font-mono font-medium ${metric.textColor}`}>
                  {metric.value}%
                </span>
              </div>
              <div className="w-full bg-gray-700/50 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full ${metric.color} transition-all duration-500 rounded-full`}
                  style={{ width: `${metric.value}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
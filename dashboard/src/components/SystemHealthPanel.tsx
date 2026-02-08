import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { Activity, Cpu, HardDrive, Wifi, Server, Cloud, Router } from "lucide-react";

const systemMetrics = [
  { name: "CPU Usage", value: 68, icon: Cpu, color: "text-cyan-400" },
  { name: "Memory", value: 82, icon: HardDrive, color: "text-green-400" },
  { name: "Network", value: 45, icon: Wifi, color: "text-purple-400" }
];

const nodeStatus = [
  { name: "AWS Cloud", status: "active", regions: "3 regions online" },
  { name: "Node-7", status: "active", regions: "Data transfer active" },
  { name: "Node-12", status: "active", regions: "Receiving data" },
  { name: "Router-5", status: "warning", regions: "Packet anomaly detected" },
  { name: "Gateway-2", status: "active", regions: "Traffic normal" },
  { name: "Backup-Node", status: "down", regions: "Maintenance mode" }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return { emoji: "🟢", color: "text-green-400" };
    case "warning": return { emoji: "🟡", color: "text-yellow-400" };
    case "down": return { emoji: "🔴", color: "text-red-400" };
    default: return { emoji: "⚪", color: "text-gray-400" };
  }
};

const getProgressColor = (value: number) => {
  if (value >= 80) return "bg-red-500";
  if (value >= 60) return "bg-yellow-500";
  return "bg-green-500";
};

export function SystemHealthPanel() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-green-400" />
          <span>System Health</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* System Metrics */}
        <div className="space-y-4">
          <h4 className="text-sm text-gray-400 uppercase tracking-wide">Performance Metrics</h4>
          {systemMetrics.map((metric, index) => {
            const IconComponent = metric.icon;
            return (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <IconComponent className={`h-4 w-4 ${metric.color}`} />
                    <span className="text-sm text-gray-300">{metric.name}</span>
                  </div>
                  <span className="text-sm text-gray-400">{metric.value}%</span>
                </div>
                <div className="relative">
                  <Progress value={metric.value} className="h-2" />
                  <div 
                    className={`absolute top-0 left-0 h-2 rounded-full transition-all duration-300 ${getProgressColor(metric.value)}`}
                    style={{ width: `${metric.value}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Node Status */}
        <div className="space-y-3">
          <h4 className="text-sm text-gray-400 uppercase tracking-wide">Node Status</h4>
          <div className="space-y-2">
            {nodeStatus.map((node, index) => {
              const statusInfo = getStatusColor(node.status);
              return (
                <div 
                  key={index}
                  className="flex items-center justify-between p-2 rounded bg-gray-800/30 border border-gray-700/30"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-sm">{statusInfo.emoji}</span>
                    <div>
                      <div className="text-sm text-gray-300">{node.name}</div>
                      <div className="text-xs text-gray-500">{node.regions}</div>
                    </div>
                  </div>
                  <div className={`text-xs uppercase tracking-wide ${statusInfo.color}`}>
                    {node.status}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
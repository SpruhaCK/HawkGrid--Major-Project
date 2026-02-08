import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Activity, CheckCircle, AlertTriangle, Router, Database } from "lucide-react";

const logEntries = [
  {
    id: 1,
    message: "AWS Cloud active – 3 regions online",
    type: "normal",
    icon: CheckCircle,
    time: "14:25:12"
  },
  {
    id: 2,
    message: "User 'admin1' logged in from 192.168.1.45",
    type: "normal",
    icon: Activity,
    time: "14:26:34"
  },
  {
    id: 3,
    message: "Node-7 transferring data to Node-12",
    type: "normal",
    icon: Database,
    time: "14:28:15"
  },
  {
    id: 4,
    message: "Router-5 detected unusual packet flow",
    type: "anomaly",
    icon: AlertTriangle,
    time: "14:30:47"
  },
  {
    id: 5,
    message: "IP 203.98.112.7 flagged for anomaly",
    type: "anomaly",
    icon: AlertTriangle,
    time: "14:32:21"
  }
];

export function SystemLogsPanel() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-cyan-400" />
          <span>System Logs</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {logEntries.map((entry) => {
            const IconComponent = entry.icon;
            const isAnomaly = entry.type === "anomaly";
            
            return (
              <div
                key={entry.id}
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                  isAnomaly
                    ? "bg-red-950/30 border-red-500/30 hover:bg-red-950/40"
                    : "bg-gray-800/30 border-gray-600/30 hover:bg-gray-800/40"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <IconComponent 
                    className={`h-4 w-4 ${
                      isAnomaly ? "text-red-400" : "text-green-400"
                    }`} 
                  />
                  <span className={`${isAnomaly ? "text-red-300" : "text-gray-300"}`}>
                    {entry.message}
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-xs text-gray-500 font-mono">
                    {entry.time}
                  </span>
                  {isAnomaly && (
                    <Badge variant="destructive" className="bg-red-600/20 text-red-400 border-red-500/30">
                      Anomaly
                    </Badge>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
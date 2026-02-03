import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { AlertTriangle, Clock, MapPin } from "lucide-react";

const threatAlerts = [
  {
    id: 1,
    severity: "Critical",
    type: "DDoS Attempt",
    source: "102.56.87.90",
    location: "Nigeria",
    time: "16:11:47",
    color: "bg-red-600/20 text-red-400 border-red-500/30",
    bgColor: "bg-red-950/30 border-red-500/30"
  },
  {
    id: 2,
    severity: "High",
    type: "SQL Injection",
    source: "185.24.76.11",
    location: "Germany",
    time: "14:32:05",
    color: "bg-orange-600/20 text-orange-400 border-orange-500/30",
    bgColor: "bg-orange-950/30 border-orange-500/30"
  },
  {
    id: 3,
    severity: "Medium",
    type: "Suspicious Login",
    source: "45.67.89.101",
    location: "India",
    time: "18:22:03",
    color: "bg-yellow-600/20 text-yellow-400 border-yellow-500/30",
    bgColor: "bg-yellow-950/30 border-yellow-500/30"
  }
];

const getSeverityEmoji = (severity: string) => {
  switch (severity) {
    case "Critical": return "🔴";
    case "High": return "🟠";
    case "Medium": return "🟡";
    default: return "⚪";
  }
};

export function ThreatAlertsPanel() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <span>Threat Alerts</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {threatAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border transition-all hover:scale-[1.02] ${alert.bgColor}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getSeverityEmoji(alert.severity)}</span>
                  <Badge className={alert.color}>
                    {alert.severity}
                  </Badge>
                </div>
                <div className="flex items-center space-x-1 text-xs text-gray-400">
                  <Clock className="h-3 w-3" />
                  <span className="font-mono">{alert.time}</span>
                </div>
              </div>
              
              <h4 className="font-medium text-gray-200 mb-2">{alert.type}</h4>
              
              <div className="space-y-1 text-sm">
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400">Source:</span>
                  <span className="font-mono text-cyan-400">{alert.source}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-3 w-3 text-gray-400" />
                  <span className="text-gray-300">{alert.location}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
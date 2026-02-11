import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { AlertTriangle, Clock, MapPin, Brain, Activity, Check, Shield } from "lucide-react";

const threatAlerts = [
  {
    id: 1,
    severity: "Critical",
    type: "Volumetric DDoS Detected",
    target: "AWS-Production-Web-1",
    source: "192.168.0.100",
    location: "Nigeria",
    time: "16:11:47",
    color: "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30",
    bgColor: "bg-[#EF4444]/10 border-[#EF4444]/30",
    mlConfidence: 99.8,
    mlModel: "Random Forest Engine",
    mitigationAction: "WAF Block Rule Initiated on IP 192.168.0.100",
    mitigationStep: 2 // 0=Detected, 1=Analyzing, 2=Mitigating, 3=Resolved
  },
  {
    id: 2,
    severity: "High",
    type: "SQL Injection Pattern",
    target: "Database-Gateway-2",
    source: "185.24.76.11",
    location: "Germany",
    time: "14:32:05",
    color: "bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30",
    bgColor: "bg-[#F59E0B]/10 border-[#F59E0B]/30",
    mlConfidence: 98.4,
    mlModel: "Neural Network Classifier",
    mitigationAction: "IP Blacklist Updated",
    mitigationStep: 1
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
          <AlertTriangle className="h-5 w-5 text-[#EF4444]" />
          <span>Active Threat Analysis</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {threatAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border transition-all hover:border-opacity-100 ${alert.bgColor} relative overflow-hidden`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getSeverityEmoji(alert.severity)}</span>
                  <Badge className={alert.color}>
                    {alert.severity}
                  </Badge>
                  <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                    <Brain className="h-3 w-3 mr-1" />
                    ML: {alert.mlConfidence}%
                  </Badge>
                </div>
                <div className="flex items-center space-x-1 text-xs text-gray-400">
                  <Clock className="h-3 w-3" />
                  <span className="font-mono">{alert.time}</span>
                </div>
              </div>
              
              <h4 className="font-medium text-gray-200 mb-2">{alert.type}</h4>
              
              <div className="space-y-2 text-sm mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400">Target:</span>
                  <span className="font-mono text-[#06B6D4]">{alert.target}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400">Source IP:</span>
                  <span className="font-mono text-gray-300">{alert.source}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-3 w-3 text-gray-400" />
                  <span className="text-gray-300">{alert.location}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400 text-xs">Detected by:</span>
                  <span className="text-gray-300 text-xs">{alert.mlModel}</span>
                </div>
              </div>

              {/* Mitigation Timeline */}
              <div className="pt-3 border-t border-gray-700/50">
                <div className="text-xs text-gray-400 mb-3">Mitigation Timeline:</div>
                <div className="flex items-center justify-between mb-3">
                  {/* Step 1: Detected */}
                  <div className="flex flex-col items-center flex-1">
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
                      alert.mitigationStep >= 0 
                        ? "bg-[#22C55E]/20 border-[#22C55E] text-[#22C55E]" 
                        : "bg-gray-700/20 border-gray-600 text-gray-500"
                    }`}>
                      <Check className="h-4 w-4" />
                    </div>
                    <div className={`text-xs mt-1 ${alert.mitigationStep >= 0 ? "text-[#22C55E]" : "text-gray-500"}`}>
                      Detected
                    </div>
                  </div>

                  <div className={`flex-1 h-[2px] mx-1 ${alert.mitigationStep >= 1 ? "bg-[#22C55E]" : "bg-gray-700"}`}></div>

                  {/* Step 2: Analyzing */}
                  <div className="flex flex-col items-center flex-1">
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
                      alert.mitigationStep >= 1
                        ? "bg-[#06B6D4]/20 border-[#06B6D4] text-[#06B6D4]" 
                        : "bg-gray-700/20 border-gray-600 text-gray-500"
                    }`}>
                      {alert.mitigationStep >= 1 ? <Check className="h-4 w-4" /> : <Activity className="h-4 w-4" />}
                    </div>
                    <div className={`text-xs mt-1 ${alert.mitigationStep >= 1 ? "text-[#06B6D4]" : "text-gray-500"}`}>
                      Analyzing
                    </div>
                  </div>

                  <div className={`flex-1 h-[2px] mx-1 ${alert.mitigationStep >= 2 ? "bg-[#F59E0B]" : "bg-gray-700"}`}></div>

                  {/* Step 3: Mitigating */}
                  <div className="flex flex-col items-center flex-1">
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
                      alert.mitigationStep === 2
                        ? "bg-[#F59E0B]/20 border-[#F59E0B] text-[#F59E0B] animate-pulse" 
                        : alert.mitigationStep > 2
                        ? "bg-[#22C55E]/20 border-[#22C55E] text-[#22C55E]"
                        : "bg-gray-700/20 border-gray-600 text-gray-500"
                    }`}>
                      {alert.mitigationStep > 2 ? <Check className="h-4 w-4" /> : <Shield className="h-4 w-4" />}
                    </div>
                    <div className={`text-xs mt-1 ${
                      alert.mitigationStep === 2 
                        ? "text-[#F59E0B]" 
                        : alert.mitigationStep > 2
                        ? "text-[#22C55E]"
                        : "text-gray-500"
                    }`}>
                      Mitigating
                    </div>
                  </div>

                  <div className={`flex-1 h-[2px] mx-1 ${alert.mitigationStep >= 3 ? "bg-[#22C55E]" : "bg-gray-700"}`}></div>

                  {/* Step 4: Resolved */}
                  <div className="flex flex-col items-center flex-1">
                    <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
                      alert.mitigationStep >= 3
                        ? "bg-[#22C55E]/20 border-[#22C55E] text-[#22C55E]" 
                        : "bg-gray-700/20 border-gray-600 text-gray-500"
                    }`}>
                      <Check className="h-4 w-4" />
                    </div>
                    <div className={`text-xs mt-1 ${alert.mitigationStep >= 3 ? "text-[#22C55E]" : "text-gray-500"}`}>
                      Resolved
                    </div>
                  </div>
                </div>

                {/* Action Text */}
                <div className="mt-3 p-2 rounded bg-gray-900/50 border border-gray-700/50">
                  <div className="text-xs text-gray-400">
                    <span className="text-[#F59E0B]">Action:</span> {alert.mitigationAction}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
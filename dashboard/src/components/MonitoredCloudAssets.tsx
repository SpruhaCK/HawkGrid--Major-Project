import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Cloud, Server } from "lucide-react";

const cloudAssets = [
  {
    id: 1,
    provider: "AWS",
    name: "HawkGrid-Linux-Victim",
    region: "us-east-1",
    ip: "34.200.x.x",
    status: "under_attack",
    icon: Cloud,
    color: "text-[#F59E0B]",
    bgColor: "bg-[#F59E0B]/10",
    borderColor: "border-[#F59E0B]/30"
  },
  {
    id: 2,
    provider: "Azure",
    name: "HawkGrid-Win-Victim",
    region: "Central India",
    ip: "52.172.x.x",
    status: "secure",
    icon: Cloud,
    color: "text-[#06B6D4]",
    bgColor: "bg-[#06B6D4]/10",
    borderColor: "border-[#06B6D4]/30"
  }
];

export function MonitoredCloudAssets() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Server className="h-5 w-5 text-[#06B6D4]" />
          <span>Monitored Cloud Assets</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {cloudAssets.map((asset) => {
          const IconComponent = asset.icon;
          return (
            <div
              key={asset.id}
              className={`p-4 rounded-lg border ${asset.bgColor} ${asset.borderColor} hover:border-opacity-100 transition-all`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <IconComponent className={`h-8 w-8 ${asset.color}`} />
                  <div>
                    <div className={`text-xs uppercase tracking-wider font-mono ${asset.color} mb-1`}>
                      {asset.provider}
                    </div>
                    <div className="text-base font-medium text-gray-200">
                      {asset.name}
                    </div>
                  </div>
                </div>
                <Badge 
                  className={
                    asset.status === "under_attack"
                      ? "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30"
                      : "bg-[#22C55E]/20 text-[#22C55E] border-[#22C55E]/30"
                  }
                >
                  {asset.status === "under_attack" ? "🔴 UNDER ATTACK" : "🟢 SECURE"}
                </Badge>
              </div>

              <div className="space-y-1 text-sm">
                <div className="flex items-center space-x-2 text-gray-400">
                  <span>{asset.region}</span>
                  <span>|</span>
                  <span className="font-mono text-gray-300">IP: {asset.ip}</span>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

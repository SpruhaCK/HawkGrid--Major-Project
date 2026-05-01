import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Cloud, Server } from "lucide-react";

// The shape of our dynamic data coming from FastAPI
interface DynamicAsset {
  ip: string;
  provider: string;
  name: string;
  region: string;
}

export function MonitoredCloudAssets() {
  const [assets, setAssets] = useState<DynamicAsset[]>([]);
  const [attackStates, setAttackStates] = useState<Record<string, boolean>>({});

  // 1. Fetch dynamic instances from your FastAPI backend
  const fetchAssets = async () => {
    try {
      const response = await fetch("http://localhost:8000/status");
      const data = await response.json();
      if (data.assets) {
        setAssets(data.assets);
      }
    } catch (error) {
      console.error("Failed to fetch assets from API. Is FastAPI running on port 8000?", error);
    }
  };

  // 2. Scan live logs to see if any discovered IP is currently under attack
  const checkAttacks = async () => {
    try {
      const response = await fetch("http://localhost:3001/api/live-logs");
      const logs = await response.json();
      
      const now = new Date().getTime();
      const currentAttackStates: Record<string, boolean> = {};

      logs.forEach((log: any) => {
        const incident = log.incident || {};
        const logTime = new Date(incident.timestamp || 0).getTime();
        const timeDiff = (now - logTime) / 1000;
        const dstIp = incident.dst_ip;

        // If an attack (not NORMAL traffic) happened in the last 15 seconds, mark IP as Anomalous
        if (timeDiff < 15 && incident.attack_type && incident.attack_type !== "NORMAL") {
          if (dstIp) {
            currentAttackStates[dstIp] = true;
          }
        }
      });

      setAttackStates(currentAttackStates);
    } catch (error) {
      console.error("Failed to fetch live logs", error);
    }
  };

  useEffect(() => {
    // Initial fetch on load
    fetchAssets();
    checkAttacks();

    // Set up polling intervals
    const assetInterval = setInterval(fetchAssets, 5000);   // Check for new VMs every 5s
    const attackInterval = setInterval(checkAttacks, 1500); // Check for attacks every 1.5s

    return () => {
      clearInterval(assetInterval);
      clearInterval(attackInterval);
    };
  }, []);

  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm w-full">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Server className="h-5 w-5 text-[#06B6D4]" />
          <span>Monitored Cloud Assets</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        
        {assets.length === 0 && (
          <div className="text-gray-400 text-sm italic text-center py-4">
            Scanning for active cloud instances...
          </div>
        )}

        {assets.map((asset, index) => {
          // Check if this specific IP is in the attack state map
          const isUnderAttack = attackStates[asset.ip] === true;

          // Azure Blue for Secure, Threat Red for Anomalous
          const currentBg = isUnderAttack ? "bg-[#EF4444]/10" : "bg-[#06B6D4]/10";
          const currentBorder = isUnderAttack ? "border-[#EF4444]/50" : "border-[#06B6D4]/30";
          const currentIconColor = isUnderAttack ? "text-[#EF4444]" : "text-[#06B6D4]";

          return (
            <div
              key={`${asset.ip}-${index}`}
              className={`p-4 rounded-lg border ${currentBg} ${currentBorder} hover:border-opacity-100 transition-all duration-300`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <Cloud className={`h-8 w-8 ${currentIconColor}`} />
                  <div>
                    <div className={`text-xs uppercase tracking-wider font-mono ${currentIconColor} mb-1`}>
                      {asset.provider}
                    </div>
                    <div className="text-base font-medium text-gray-200">
                      {asset.name}
                    </div>
                  </div>
                </div>

                <Badge 
                  className={
                    isUnderAttack
                      ? "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30 animate-pulse"
                      : "bg-[#06B6D4]/20 text-[#06B6D4] border-[#06B6D4]/30"
                  }
                >
                  {isUnderAttack ? "🔴 ANOMALOUS" : "🟢 SECURE"}
                </Badge>
              </div>

              <div className="space-y-1 text-sm">
                <div className="flex items-center space-x-2 text-gray-400">
                  <span>{asset.region}</span>
                  <span>|</span>
                  <span className="font-mono text-gray-300">
                    IP: <span className={isUnderAttack ? "text-[#EF4444]" : "text-[#06B6D4]"}>
                      {asset.ip}
                    </span>
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
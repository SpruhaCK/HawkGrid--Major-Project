// import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
// import { Badge } from "./ui/badge";
// import { Cloud, Server } from "lucide-react";

// const cloudAssets = [
//   {
//     id: 1,
//     provider: "AWS",
//     name: "HawkGrid-Linux-Victim",
//     region: "us-east-1",
//     ip: "34.200.x.x",
//     status: "under_attack",
//     icon: Cloud,
//     color: "text-[#F59E0B]",
//     bgColor: "bg-[#F59E0B]/10",
//     borderColor: "border-[#F59E0B]/30"
//   },
//   {
//     id: 2,
//     provider: "Azure",
//     name: "HawkGrid-Win-Victim",
//     region: "Central India",
//     ip: "52.172.x.x",
//     status: "secure",
//     icon: Cloud,
//     color: "text-[#06B6D4]",
//     bgColor: "bg-[#06B6D4]/10",
//     borderColor: "border-[#06B6D4]/30"
//   }
// ];

// export function MonitoredCloudAssets() {
//   return (
//     <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
//       <CardHeader>
//         <CardTitle className="flex items-center space-x-2">
//           <Server className="h-5 w-5 text-[#06B6D4]" />
//           <span>Monitored Cloud Assets</span>
//         </CardTitle>
//       </CardHeader>
//       <CardContent className="space-y-4">
//         {cloudAssets.map((asset) => {
//           const IconComponent = asset.icon;
//           return (
//             <div
//               key={asset.id}
//               className={`p-4 rounded-lg border ${asset.bgColor} ${asset.borderColor} hover:border-opacity-100 transition-all`}
//             >
//               <div className="flex items-start justify-between mb-3">
//                 <div className="flex items-center space-x-3">
//                   <IconComponent className={`h-8 w-8 ${asset.color}`} />
//                   <div>
//                     <div className={`text-xs uppercase tracking-wider font-mono ${asset.color} mb-1`}>
//                       {asset.provider}
//                     </div>
//                     <div className="text-base font-medium text-gray-200">
//                       {asset.name}
//                     </div>
//                   </div>
//                 </div>
//                 <Badge 
//                   className={
//                     asset.status === "under_attack"
//                       ? "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30"
//                       : "bg-[#22C55E]/20 text-[#22C55E] border-[#22C55E]/30"
//                   }
//                 >
//                   {asset.status === "under_attack" ? "🔴 UNDER ATTACK" : "🟢 SECURE"}
//                 </Badge>
//               </div>

//               <div className="space-y-1 text-sm">
//                 <div className="flex items-center space-x-2 text-gray-400">
//                   <span>{asset.region}</span>
//                   <span>|</span>
//                   <span className="font-mono text-gray-300">IP: {asset.ip}</span>
//                 </div>
//               </div>
//             </div>
//           );
//         })}
//       </CardContent>
//     </Card>
//   );
// }


import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Cloud, Server, ShieldCheck, ShieldAlert } from "lucide-react";

// Static definitions (Now with 3 Assets)
const STATIC_ASSETS = [
  {
    id: "aws-asset-01",
    provider: "AWS",
    name: "HawkGrid-Linux-Victim",
    region: "us-east-1",
    defaultIp: "Waiting for Traffic...", // Will update dynamically
    icon: Cloud,
    // Broad keywords to match Node ID, Cloud Provider, or IP from logs
    keywords: ["linux", "ip-10-0-1", "10.0.1.90", "aws"], 
    baseColor: "text-[#F59E0B]",
    baseBg: "bg-[#F59E0B]/10",
    baseBorder: "border-[#F59E0B]/30"
  },
  {
    id: "aws-asset-02", // NEW: AWS Windows Asset
    provider: "AWS",
    name: "HawkGrid-Win-Victim",
    region: "us-east-1",
    defaultIp: "Waiting for Traffic...",
    icon: Cloud,
    keywords: ["windows", "win", "ip-10-0-2", "10.0.1.91"],
    baseColor: "text-[#F59E0B]",
    baseBg: "bg-[#F59E0B]/10",
    baseBorder: "border-[#F59E0B]/30"
  },
  {
    id: "azure-asset-01",
    provider: "Azure",
    name: "HawkGrid-Win-Victim",
    region: "Central India",
    defaultIp: "52.172.x.x", // Static fallback if needed
    icon: Cloud,
    keywords: ["azure", "10.0.2.4"],
    baseColor: "text-[#06B6D4]",
    baseBg: "bg-[#06B6D4]/10",
    baseBorder: "border-[#06B6D4]/30"
  }
];

export function MonitoredCloudAssets() {
  const [assetData, setAssetData] = useState<Record<string, { status: string; ip: string }>>({});

  const checkAssetStatus = async () => {
    try {
      const response = await fetch("http://localhost:3001/api/live-logs");
      const logs = await response.json();
      
      const now = new Date().getTime();
      const currentData: Record<string, { status: string; ip: string }> = {};

      // Initialize defaults
      STATIC_ASSETS.forEach(asset => {
        currentData[asset.id] = { status: "secure", ip: asset.defaultIp };
      });

      // Scan logs
      logs.forEach((log: any) => {
        const incident = log.incident || {};
        const logTime = new Date(incident.timestamp || 0).getTime();
        const timeDiff = (now - logTime) / 1000;

        // Normalize matching fields
        const target = (incident.node_id || "").toLowerCase();
        const provider = (incident.cloud_provider || "").toLowerCase();
        // Capture the EXACT IP from the ledger's "dst_ip" field
        const dstIp = incident.dst_ip; 

        STATIC_ASSETS.forEach(asset => {
          // Check for match in NodeID, Provider, or even the IP itself
          const isMatch = asset.keywords.some(k => 
            target.includes(k) || provider.includes(k) || (dstIp && dstIp.includes(k))
          );

          if (isMatch) {
            // 1. UPDATE IP: Always trust the ledger's dst_ip if present
            if (dstIp && dstIp !== "Unknown") {
                currentData[asset.id].ip = dstIp;
            }

            // 2. UPDATE STATUS: If log is recent (< 30s), set to UNDER ATTACK
            if (timeDiff < 30) {
                currentData[asset.id].status = "under_attack";
            }
          }
        });
      });

      // Preserve state (don't revert valid IPs to "Waiting...")
      setAssetData(prev => {
        const merged = { ...currentData };
        Object.keys(prev).forEach(key => {
            if (merged[key].ip === "Waiting for Traffic..." && prev[key].ip !== "Waiting for Traffic...") {
                merged[key].ip = prev[key].ip;
            }
        });
        return merged;
      });

    } catch (error) {
      console.error("Failed to sync asset status", error);
    }
  };

  useEffect(() => {
    checkAssetStatus();
    const interval = setInterval(checkAssetStatus, 2000); 
    return () => clearInterval(interval);
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
        {STATIC_ASSETS.map((asset) => {
          const data = assetData[asset.id] || { status: "secure", ip: asset.defaultIp };
          const isUnderAttack = data.status === "under_attack";
          const IconComponent = asset.icon;

          // Styles: Switch to Red if Under Attack, else keep original Asset Color
          const currentBg = isUnderAttack ? "bg-[#EF4444]/10" : asset.baseBg;
          const currentBorder = isUnderAttack ? "border-[#EF4444]/50" : asset.baseBorder;
          const currentIconColor = isUnderAttack ? "text-[#EF4444]" : asset.baseColor;

          return (
            <div
              key={asset.id}
              className={`p-4 rounded-lg border ${currentBg} ${currentBorder} hover:border-opacity-100 transition-all duration-300`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <IconComponent className={`h-8 w-8 ${currentIconColor}`} />
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
                      : "bg-[#22C55E]/20 text-[#22C55E] border-[#22C55E]/30"
                  }
                >
                  {isUnderAttack ? "🔴 UNDER ATTACK" : "🟢 SECURE"}
                </Badge>
              </div>

              <div className="space-y-1 text-sm">
                <div className="flex items-center space-x-2 text-gray-400">
                  <span>{asset.region}</span>
                  <span>|</span>
                  <span className="font-mono text-gray-300">
                    IP: <span className={isUnderAttack ? "text-[#EF4444]" : "text-[#06B6D4]"}>{data.ip}</span>
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
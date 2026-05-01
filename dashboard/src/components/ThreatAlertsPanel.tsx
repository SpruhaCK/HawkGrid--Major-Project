import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { AlertTriangle, Clock, MapPin, Brain, Activity, Check, Shield, Download } from "lucide-react";

// --- CONFIGURATION ---
const getSeverityConfig = (score: number, attackType: string) => {
  let severity = "Medium";
  let color = "bg-[#06B6D4]/20 text-[#06B6D4] border-[#06B6D4]/30"; 
  let bgColor = "bg-[#06B6D4]/10 border-[#06B6D4]/30";
  let emoji = "🟡";

  const type = attackType?.toLowerCase() || "";
  
  if (score >= 4 || type.includes("ddos") || type.includes("dos") || type.includes("exploits")) {
    severity = "Critical";
    color = "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30"; 
    bgColor = "bg-[#EF4444]/10 border-[#EF4444]/30";
    emoji = "🔴";
  } else if (score >= 3 || type.includes("brute") || type.includes("fuzzers") || type.includes("analysis")) {
    severity = "High";
    color = "bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30"; 
    bgColor = "bg-[#F59E0B]/10 border-[#F59E0B]/30";
    emoji = "🟠";
  }
  return { severity, color, bgColor, emoji };
};

const getMockCountry = (ip: string) => {
  const countries = ["Germany", "Nigeria", "Russia", "China", "United States", "Brazil", "India"];
  const sum = ip.split('.').reduce((a, b) => a + parseInt(b || "0"), 0);
  return countries[sum % countries.length];
};

export function ThreatAlertsPanel() {
  const [attacks, setAttacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(Date.now());

  // Ticks every 500ms to recalculate if traffic has stopped
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(Date.now()), 500);
    return () => clearInterval(timer);
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await fetch(`http://localhost:3001/api/live-logs?_t=${Date.now()}`);
      const rawData = await response.json();
      const now = Date.now();

      // UI: We only care about attacks that happened in the last 60 seconds for the active dashboard
      const recentLogs = rawData.filter((b: any) => {
        if (!b.incident?.timestamp) return false;
        return (now - new Date(b.incident.timestamp).getTime()) < 60000;
      });

      const attackStats: Record<string, { firstSeen: number, lastSeen: number, action: string, data: any }> = {};

      // Sort Oldest to Newest to accurately capture 'firstSeen'
      recentLogs.sort((a: any, b: any) => new Date(a.incident?.timestamp).getTime() - new Date(b.incident?.timestamp).getTime());

      recentLogs.forEach((block: any) => {
        const incident = block.incident;
        if (!incident?.attack_type || incident.attack_type === "NORMAL") return;
        
        const ip = incident.src_ip;
        if (!ip) return;

        const groupKey = `${ip}-${incident.attack_type}`;
        const logTime = new Date(incident.timestamp).getTime();
        const actionStr = block.response_action || "";

        if (!attackStats[groupKey]) {
          attackStats[groupKey] = { firstSeen: logTime, lastSeen: logTime, action: actionStr, data: block };
        } else {
          attackStats[groupKey].lastSeen = logTime; 
          if (actionStr && actionStr !== "UNKNOWN" && actionStr !== "NONE") {
            attackStats[groupKey].action = actionStr; 
          }
          attackStats[groupKey].data = block;
        }
      });

      // UI: Convert to array and take only the 2 most recently active attacks
      const topAttacks = Object.values(attackStats)
        .sort((a, b) => b.lastSeen - a.lastSeen)
        .slice(0, 2);

      const processedAttacks = topAttacks.map((stat) => {
        const incident = stat.data.incident;
        const score = incident.owasp_risk_score || incident.anomaly_score || 0;
        const provider = (incident.cloud_provider || "aws").toLowerCase();
        const { severity, color, bgColor, emoji } = getSeverityConfig(score, incident.attack_type);
        
        return {
          id: `${incident.src_ip}-${incident.attack_type}`,
          firstSeen: stat.firstSeen,
          lastSeen: stat.lastSeen,
          backendAction: stat.action,
          time: new Date(stat.lastSeen).toLocaleTimeString(),
          type: incident.attack_type,
          source: incident.src_ip,
          target: provider === "azure" ? `Azure-VM (${incident.dst_ip})` : `AWS-Node (${incident.dst_ip})`,
          severity, color, bgColor, emoji,
          location: getMockCountry(incident.src_ip),
          mlModel: "Random Forest Engine",
        };
      });

      setAttacks(processedAttacks);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching threat alerts:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 1500);
    return () => clearInterval(interval);
  }, []);

  // 🚨 UPGRADED: This now fetches the ENTIRE log history directly from the backend!
  const downloadCSV = async () => {
    try {
      // 1. Fetch the absolute full log history from the API
      const response = await fetch(`http://localhost:3001/api/live-logs?_t=${Date.now()}`);
      const fullHistory = await response.json();

      // 2. Sort newest to oldest
      fullHistory.sort((a: any, b: any) => {
        return new Date(b.incident?.timestamp || 0).getTime() - new Date(a.incident?.timestamp || 0).getTime();
      });

      // 3. Process every single valid attack log
      const allAttacks = fullHistory
        .filter((block: any) => block.incident?.attack_type && block.incident.attack_type !== "NORMAL")
        .map((block: any) => {
          const incident = block.incident || {};
          const score = incident.owasp_risk_score || incident.anomaly_score || 0;
          const provider = (incident.cloud_provider || "aws").toLowerCase();
          const { severity } = getSeverityConfig(score, incident.attack_type);
          
          const targetName = provider === "azure" 
            ? `Azure-VM (${incident.dst_ip || 'Unknown'})` 
            : `AWS-Node (${incident.dst_ip || 'Unknown'})`;

          return {
            time: new Date(incident.timestamp).toLocaleTimeString(),
            type: incident.attack_type,
            source: incident.src_ip || "Unknown",
            target: targetName,
            severity: severity,
            location: getMockCountry(incident.src_ip || "0.0.0.0"),
            action: block.response_action || "Pending"
          };
        });

      if (allAttacks.length === 0) return;

      // 4. Generate the CSV file with ALL data
      const headers = ["Time", "Attack Type", "Source IP", "Target", "Severity", "Location", "Backend Action"];
      const csvContent = [
        headers.join(","),
        ...allAttacks.map((a: any) => `"${a.time}","${a.type}","${a.source}","${a.target}","${a.severity}","${a.location}","${a.action}"`)
      ].join("\n");

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `hawkgrid_full_threat_history_${new Date().getTime()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

    } catch (error) {
      console.error("Failed to download full CSV history", error);
    }
  };

  const calculateRealTimeStep = (firstSeen: number, lastSeen: number, backendAction: string) => {
    const timeSinceLastPacket = (currentTime - lastSeen) / 1000;
    const timeSinceFirstPacket = (currentTime - firstSeen) / 1000;
    
    const isBlocked = backendAction.includes("SUCCESS") || backendAction.includes("BLOCK") || backendAction.includes("HIVE_MIND");

    if (isBlocked) {
      if (timeSinceLastPacket <= 3) {
        return 2; // Mitigating (Rule is propagating)
      } else {
        return 3; // Resolved (Traffic has flatlined)
      }
    } else {
      if (timeSinceFirstPacket > 1.5) return 1; // Analyzing
      return 0; // Detected
    }
  };

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
          {loading ? (
            <div className="text-center text-gray-500 py-8">Analyzing network packets...</div>
          ) : attacks.length === 0 ? (
            <div className="text-center text-[#22C55E] py-8 font-mono">No active threats. Systems secure.</div>
          ) : (
            attacks.map((alert) => {
              const currentStep = calculateRealTimeStep(alert.firstSeen, alert.lastSeen, alert.backendAction);
              
              const dynamicAction = currentStep >= 3
                ? `Layer 4 firewall blocking successful on IP ${alert.source}`
                : `Layer 4 firewall blocking initiated on IP ${alert.source}`;

              return (
                <div key={alert.id} className={`p-4 rounded-lg border transition-all hover:border-opacity-100 ${alert.bgColor} relative overflow-hidden`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{alert.emoji}</span>
                      <Badge className={alert.color}>{alert.severity}</Badge>
                      <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                        <Brain className="h-3 w-3 mr-1" />
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

                  <div className="pt-3 border-t border-gray-700/50">
                    <div className="text-xs text-gray-400 mb-3">Mitigation Timeline:</div>
                    <div className="flex items-center justify-between mb-3">
                      
                      <div className="flex flex-col items-center flex-1">
                        <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${currentStep >= 0 ? "bg-[#22C55E]/20 border-[#22C55E] text-[#22C55E]" : "bg-gray-700/20 border-gray-600 text-gray-500"}`}>
                          <Check className="h-4 w-4" />
                        </div>
                        <div className={`text-xs mt-1 ${currentStep >= 0 ? "text-[#22C55E]" : "text-gray-500"}`}>Detected</div>
                      </div>

                      <div className={`flex-1 h-[2px] mx-1 ${currentStep >= 1 ? "bg-[#22C55E]" : "bg-gray-700"}`}></div>

                      <div className="flex flex-col items-center flex-1">
                        <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${currentStep >= 1 ? "bg-[#06B6D4]/20 border-[#06B6D4] text-[#06B6D4]" : "bg-gray-700/20 border-gray-600 text-gray-500"}`}>
                          {currentStep >= 1 ? <Check className="h-4 w-4" /> : <Activity className="h-4 w-4" />}
                        </div>
                        <div className={`text-xs mt-1 ${currentStep >= 1 ? "text-[#06B6D4]" : "text-gray-500"}`}>Analyzing</div>
                      </div>

                      <div className={`flex-1 h-[2px] mx-1 ${currentStep >= 2 ? "bg-[#F59E0B]" : "bg-gray-700"}`}></div>

                      <div className="flex flex-col items-center flex-1">
                        <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${currentStep === 2 ? "bg-[#F59E0B]/20 border-[#F59E0B] text-[#F59E0B] animate-pulse" : currentStep > 2 ? "bg-[#22C55E]/20 border-[#22C55E] text-[#22C55E]" : "bg-gray-700/20 border-gray-600 text-gray-500"}`}>
                          {currentStep > 2 ? <Check className="h-4 w-4" /> : <Shield className="h-4 w-4" />}
                        </div>
                        <div className={`text-xs mt-1 ${currentStep === 2 ? "text-[#F59E0B]" : currentStep > 2 ? "text-[#22C55E]" : "text-gray-500"}`}>Mitigating</div>
                      </div>

                      <div className={`flex-1 h-[2px] mx-1 ${currentStep >= 3 ? "bg-[#22C55E]" : "bg-gray-700"}`}></div>

                      <div className="flex flex-col items-center flex-1">
                        <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${currentStep >= 3 ? "bg-[#22C55E]/20 border-[#22C55E] text-[#22C55E]" : "bg-gray-700/20 border-gray-600 text-gray-500"}`}>
                          <Check className="h-4 w-4" />
                        </div>
                        <div className={`text-xs mt-1 ${currentStep >= 3 ? "text-[#22C55E]" : "text-gray-500"}`}>Resolved</div>
                      </div>
                    </div>

                    <div className="mt-3 p-2 rounded bg-gray-900/50 border border-gray-700/50">
                      <div className="text-xs text-gray-400">
                        <span className="text-[#F59E0B]">Action:</span> {dynamicAction}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}

          {/* Export Button */}
          <div className="flex justify-end pt-2 mt-4">
            <button onClick={downloadCSV} className="flex items-center space-x-2 bg-[#06B6D4]/10 hover:bg-[#06B6D4]/20 border border-[#06B6D4]/50 text-[#06B6D4] px-4 py-2 rounded shadow transition-all duration-200 text-sm font-semibold">
              <Download className="h-4 w-4" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
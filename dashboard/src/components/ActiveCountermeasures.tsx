import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ShieldCheck, Loader2, CheckCircle, Shield } from "lucide-react";

const getTimeAgo = (timestamp: string) => {
  const seconds = Math.floor((new Date().getTime() - new Date(timestamp).getTime()) / 1000);
  if (seconds < 5) return "Just now";
  if (seconds < 60) return `${seconds} secs ago`;
  const mins = Math.floor(seconds / 60);
  return `${mins} min${mins > 1 ? 's' : ''} ago`;
};

const formatActionText = (statusString: string, ip: string, provider: string) => {
  if (statusString === "HIVE_MIND_SUCCESS") return `Global Hive Mind Block: ${ip}`;
  if (statusString === "ALERT_ONLY_WHITELISTED_IP") return `HawkGrid Shield: Bypassed ${ip}`;
  if (statusString === "SUCCESS") return `Block IP ${ip} (${provider} WAF)`;
  return `Mitigation Executed on ${ip}`;
};

export function ActiveCountermeasures() {
  const [measures, setMeasures] = useState<any[]>([]);
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  const fetchCountermeasures = async () => {
    try {
      // 🚨 CACHE BUSTER ADDED: Forces browser to fetch fresh data every time
      const response = await fetch(`http://localhost:3001/api/live-logs?_t=${Date.now()}`);
      const rawData = await response.json();

      rawData.sort((a: any, b: any) => {
        return new Date(b.incident?.timestamp || 0).getTime() - new Date(a.incident?.timestamp || 0).getTime();
      });

      const processedMeasures: any[] = [];

      rawData.forEach((block: any, index: number) => {
        const incident = block.incident || {};
        const statusString = block.response_action || "UNKNOWN";
        
        // 🚨 FIXED: Skip non-actions correctly based on your API's string format
        if (statusString === "NORMAL_TRAFFIC" || statusString === "SIMULATED_SUCCESS" || statusString === "UNKNOWN") return;

        const timestamp = incident.timestamp || new Date().toISOString();
        const srcIp = incident.src_ip || "Unknown IP";
        const provider = (incident.cloud_provider || "CLOUD").toUpperCase();

        const ageInSeconds = (now - new Date(timestamp).getTime()) / 1000;
        const isInProgress = ageInSeconds < 4;
        const isShield = statusString === "ALERT_ONLY_WHITELISTED_IP";

        let status = "success";
        let statusText = "Success ✅";
        let statusColor = "text-[#22C55E]"; 
        let StatusIcon = CheckCircle; 
        let animate = false;

        if (isInProgress && !isShield) {
          status = "in_progress";
          statusText = "In Progress...";
          statusColor = "text-[#F59E0B]"; 
          StatusIcon = Loader2;
          animate = true;
        } else if (isShield) {
          status = "shield";
          statusText = "Presenter Protected 🛡️";
          statusColor = "text-[#06B6D4]"; 
          StatusIcon = Shield; 
        }

        processedMeasures.push({
          id: block.hash || index.toString(),
          action: formatActionText(statusString, srcIp, provider),
          status,
          statusText,
          statusColor,
          statusIcon: StatusIcon,
          timeStr: timestamp,
          animate
        });
      });

      setMeasures(processedMeasures.slice(0, 4));
    } catch (error) {
      console.error("Error fetching countermeasures:", error);
    }
  };

  useEffect(() => {
    fetchCountermeasures();
    const interval = setInterval(fetchCountermeasures, 2000);
    return () => clearInterval(interval);
  }, [now]);

  return (
    <Card className="bg-[#111827] border-gray-800 shadow-xl w-full">
      <CardHeader className="border-b border-gray-800 pb-4">
        <CardTitle className="flex items-center space-x-2 text-gray-100">
          <ShieldCheck className="h-5 w-5 text-[#06B6D4]" />
          <span>Active Countermeasures</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {measures.length === 0 ? (
            <div className="text-center text-gray-500 py-8 text-sm">
              No defensive actions required recently.
            </div>
          ) : (
            measures.map((measure) => {
              const StatusIcon = measure.statusIcon;
              let dotColor = "bg-[#22C55E] border-[#22C55E]"; 
              if (measure.status === "in_progress") dotColor = "bg-[#F59E0B] border-[#F59E0B] animate-pulse";
              if (measure.status === "shield") dotColor = "bg-[#06B6D4] border-[#06B6D4]";

              return (
                <div key={measure.id} className="relative pl-6 pb-5 border-l-2 border-gray-700 last:border-l-0 last:pb-0">
                  <div className={`absolute left-[-5px] top-1 w-3 h-3 rounded-full border-2 ${dotColor}`}></div>
                  <div className="space-y-2">
                    <div className="text-sm font-bold text-gray-200">{measure.action}</div>
                    <div className="flex items-center justify-between">
                      <div className={`flex items-center space-x-1 text-sm font-medium ${measure.statusColor}`}>
                        <StatusIcon className={`h-4 w-4 ${measure.animate ? "animate-spin" : ""}`} />
                        <span>{measure.statusText}</span>
                      </div>
                      <div className="text-xs text-gray-500 font-mono">{getTimeAgo(measure.timeStr)}</div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </CardContent>
    </Card>
  );
}
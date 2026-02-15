import { useState } from "react";
import { Download, CheckCircle2, Loader2 } from "lucide-react";
import { Button } from "./ui/button";

// --- SEVERITY HELPER (Needed for the report text) ---
const getSeverityLevel = (score: number, attackType: string) => {
  const type = attackType?.toLowerCase() || "";
  if (score > 0.7 || type.includes("ddos") || type.includes("dos") || type.includes("amplification")) {
    return "Critical";
  } else if (score > 0.4 || type.includes("brute") || type.includes("injection") || type.includes("stuffing")) {
    return "High";
  }
  return "Medium";
};

export function DownloadReportButton() {
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle");

  const handleDownload = async () => {
    setStatus("loading");

    try {
      // 1. Fetch the latest RAW logs from the bridge
      const response = await fetch("http://localhost:3001/api/live-logs");
      const rawData = await response.json();

      // 2. Sort Oldest -> Newest (Required for correct grouping)
      rawData.sort((a: any, b: any) => {
        const tA = new Date(a.incident?.timestamp || 0).getTime();
        const tB = new Date(b.incident?.timestamp || 0).getTime();
        return tA - tB;
      });

      // 3. AGGREGATION LOGIC (Same as your Dashboard Table)
      const aggregatedAttacks: any[] = [];
      let currentGroup: any = null;

      rawData.forEach((block: any) => {
        const incident = block.incident || {};
        const raw = incident.raw_event || {};
        
        const timestamp = incident.timestamp || new Date().toISOString();
        const attackType = incident.attack_type || "Unknown Anomaly";
        const srcIp = incident.src_ip || "Unknown";
        const dstIp = incident.dst_ip || "Unknown IP";
        const assetName = incident.node_id || "Unknown Asset"; 
        const score = incident.anomaly_score || 0;
        
        const prevHash = block.previous_hash || "GENESIS";
        const currHash = block.hash || "PENDING";
        const actionStatus = block.status || "LOGGED"; 

        const packetCount = raw.API_Call_Freq ? Math.floor(raw.API_Call_Freq) : 1;

        // Check if same attack group (Time window: 30s)
        const isSameGroup = currentGroup && 
                            currentGroup.attackType === attackType &&
                            currentGroup.sourceIP === srcIp &&
                            currentGroup.targetAsset === assetName &&
                            (new Date(timestamp).getTime() - new Date(currentGroup.rawEndTime).getTime() < 30000); 

        if (isSameGroup) {
          // Update existing group
          currentGroup.rawEndTime = timestamp;
          currentGroup.packetSum += packetCount;
          
          const startTimeStr = currentGroup.rawStartTime.split('T')[1]?.split('.')[0];
          const endTimeStr = timestamp.split('T')[1]?.split('.')[0];
          currentGroup.timestampDisplay = `${startTimeStr} - ${endTimeStr}`;
          
          // Update technical details to latest
          currentGroup.details.currentHash = currHash;
          currentGroup.details.score = score;
          currentGroup.details.egress = raw.Network_Egress_MB || currentGroup.details.egress;
          currentGroup.details.failedAuth = raw.Failed_Auth_Count || currentGroup.details.failedAuth;

        } else {
          // Push previous group and start new one
          if (currentGroup) aggregatedAttacks.push(currentGroup);

          const level = getSeverityLevel(score, attackType);
          const timeStr = timestamp.split('T')[1]?.split('.')[0] || timestamp;

          currentGroup = {
            timestampDisplay: timeStr, // Initial single timestamp
            rawStartTime: timestamp,
            rawEndTime: timestamp,
            attackType: attackType,
            sourceIP: srcIp,
            targetAsset: assetName,
            severity: level,
            packetSum: packetCount,
            details: {
              destIp: dstIp,
              assetName: assetName,
              score: score,
              apiFreq: raw.API_Call_Freq || 0,
              failedAuth: raw.Failed_Auth_Count || 0,
              egress: raw.Network_Egress_MB || 0,
              response: actionStatus,
              prevHash: prevHash,
              currentHash: currHash
            }
          };
        }
      });

      // Don't forget the last one
      if (currentGroup) aggregatedAttacks.push(currentGroup);
      
      // Reverse to show newest first in the CSV
      const finalReportData = aggregatedAttacks.reverse();

      // 4. GENERATE CSV
      const headers = [
        "Duration", "Attack Type", "Source IP", "Target Asset", "Severity", 
        "Blocked Requests", "Anomaly Score", "API Freq", "Failed Auth Count", 
        "Network Egress (MB)", "Response Action", "Previous Hash", "Current Hash"
      ];

      const csvRows = [
        headers.join(","),
        ...finalReportData.map(row => {
          const d = row.details;
          return [
            `"${row.timestampDisplay}"`,
            row.attackType,
            row.sourceIP,
            d.assetName,
            row.severity,
            row.packetSum,
            d.score,
            d.apiFreq,
            d.failedAuth,
            d.egress,
            d.response,
            d.prevHash,
            d.currentHash
          ].join(",");
        })
      ];

      const csvContent = csvRows.join("\n");
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `HawkGrid_Forensic_Report_${new Date().toISOString().slice(0,10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // 5. Success State
      setStatus("success");
      setTimeout(() => setStatus("idle"), 3000); // Reset after 3 seconds

    } catch (error) {
      console.error("Download failed:", error);
      alert("Failed to download report. Is the backend running?");
      setStatus("idle");
    }
  };

  return (
    <Button 
      onClick={handleDownload}
      disabled={status === "loading"}
      className={`
        relative overflow-hidden group
        bg-gradient-to-r from-cyan-600 to-blue-600 
        hover:from-cyan-700 hover:to-blue-700 
        text-white px-8 py-6 text-lg font-semibold rounded-xl 
        shadow-lg hover:shadow-cyan-500/25 
        transition-all duration-300 border border-cyan-500/30
        ${status === "success" ? "ring-2 ring-green-500 ring-offset-2 ring-offset-slate-900" : ""}
      `}
    >
      <div className="flex items-center gap-3">
        {status === "loading" ? (
          <Loader2 className="h-6 w-6 animate-spin" />
        ) : status === "success" ? (
          <CheckCircle2 className="h-6 w-6 text-green-300 animate-in zoom-in" />
        ) : (
          <Download className="h-6 w-6 group-hover:scale-110 transition-transform duration-200" />
        )}
        
        <span>
          {status === "loading" ? "Generating Report..." : 
           status === "success" ? "Report Downloaded!" : 
           "Download Full Forensic Report"}
        </span>
      </div>
    </Button>
  );
}
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { AlertCircle, Clock } from "lucide-react";

// --- CONFIGURATION ---
const getSeverityConfig = (score: number, attackType: string) => {
  let level = "Medium";
  let color = "bg-[#06B6D4]/20 text-[#06B6D4] border-[#06B6D4]/30"; // Blue

  const type = attackType?.toLowerCase() || "";
  
  if (score > 0.7 || type.includes("ddos") || type.includes("dos") || type.includes("amplification")) {
    level = "Critical";
    color = "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30"; // Red
  } else if (score > 0.4 || type.includes("brute") || type.includes("injection") || type.includes("stuffing")) {
    level = "High";
    color = "bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30"; // Amber
  }
  return { level, color };
};

export function AttackAnalysisSection() {
  const [attacks, setAttacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    try {
      const response = await fetch("http://localhost:3001/api/live-logs");
      const rawData = await response.json();

      // Sort Oldest -> Newest for correct grouping
      rawData.sort((a: any, b: any) => {
        const tA = new Date(a.incident?.timestamp || 0).getTime();
        const tB = new Date(b.incident?.timestamp || 0).getTime();
        return tA - tB;
      });

      const aggregatedAttacks: any[] = [];
      let currentGroup: any = null;

      rawData.forEach((block: any, index: number) => {
        const incident = block.incident || {};
        const raw = incident.raw_event || {};
        
        const timestamp = incident.timestamp || new Date().toISOString();
        const attackType = incident.attack_type || "Unknown Anomaly";
        const srcIp = incident.src_ip || "Unknown";
        const assetName = incident.node_id || "Unknown Asset"; 
        const score = incident.anomaly_score || 0;
        
        const currHash = block.hash || "PENDING";
        const packetCount = raw.API_Call_Freq ? Math.floor(raw.API_Call_Freq) : 1;

        // Grouping Logic (30s window)
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
          currentGroup.packetsBlocked = `${currentGroup.packetSum} Reqs`;

        } else {
          // Push previous group
          if (currentGroup) aggregatedAttacks.push(currentGroup);

          const { level, color } = getSeverityConfig(score, attackType);
          const timeStr = timestamp.split('T')[1]?.split('.')[0] || timestamp;

          currentGroup = {
            id: currHash || index,
            rawStartTime: timestamp,
            rawEndTime: timestamp,
            timestampDisplay: timeStr,
            attackType: attackType,
            sourceIP: srcIp,
            targetAsset: assetName,
            severity: level,
            severityColor: color,
            packetSum: packetCount,
            packetsBlocked: `${packetCount} Reqs`
          };
        }
      });

      // Push final group
      if (currentGroup) aggregatedAttacks.push(currentGroup);

      // Reverse to show Newest First
      setAttacks(aggregatedAttacks.reverse());
      setLoading(false);

    } catch (error) {
      console.error("Error fetching logs:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-[#EF4444]" />
          <span>Detailed Attack Analysis (Live)</span>
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-gray-700 hover:bg-transparent">
                <TableHead className="text-gray-400 w-[180px]">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>Duration</span>
                  </div>
                </TableHead>
                <TableHead className="text-gray-400">Attack Type</TableHead>
                <TableHead className="text-gray-400">Source IP</TableHead>
                <TableHead className="text-gray-400">Target Asset</TableHead>
                <TableHead className="text-gray-400">Severity</TableHead>
                <TableHead className="text-gray-400 text-right">Blocked</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {attacks.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                    {loading ? "Connecting to Live Ledger..." : "No active threats detected."}
                  </TableCell>
                </TableRow>
              ) : (
                // Show only top 10 rows
                attacks.slice(0, 10).map((attack) => (
                  <TableRow key={attack.id} className="border-gray-700 hover:bg-gray-700/30 transition-colors">
                    <TableCell className="font-mono text-xs text-gray-300 whitespace-nowrap">
                      {attack.timestampDisplay}
                    </TableCell>
                    <TableCell className="text-gray-200 font-medium">
                      {attack.attackType}
                    </TableCell>
                    <TableCell className="font-mono text-sm text-[#06B6D4]">
                      {attack.sourceIP}
                    </TableCell>
                    <TableCell className="text-gray-300 text-sm">
                      {attack.targetAsset}
                    </TableCell>
                    <TableCell>
                      <Badge className={`${attack.severityColor} border`}>
                        {attack.severity}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-sm text-right text-gray-300">
                      {attack.packetsBlocked}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
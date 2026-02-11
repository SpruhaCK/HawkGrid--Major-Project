import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { AlertCircle } from "lucide-react";

const attackData = [
  {
    id: 1,
    timestamp: "2026-02-10 16:11:47",
    attackType: "Volumetric DDoS",
    sourceIP: "192.168.0.100",
    targetAsset: "AWS-Production-Web-1",
    location: "Nigeria",
    severity: "Critical",
    severityColor: "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30",
    packetsBlocked: "2.4M"
  },
  {
    id: 2,
    timestamp: "2026-02-10 14:32:05",
    attackType: "SQL Injection",
    sourceIP: "185.24.76.11",
    targetAsset: "Database-Gateway-2",
    location: "Germany",
    severity: "High",
    severityColor: "bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30",
    packetsBlocked: "847"
  },
  {
    id: 3,
    timestamp: "2026-02-10 13:18:22",
    attackType: "SSH Brute Force",
    sourceIP: "203.45.128.94",
    targetAsset: "Azure-Backend-Server",
    location: "China",
    severity: "High",
    severityColor: "bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30",
    packetsBlocked: "12.3K"
  },
  {
    id: 4,
    timestamp: "2026-02-10 11:45:10",
    attackType: "Port Scan",
    sourceIP: "78.142.19.200",
    targetAsset: "AWS-API-Gateway",
    location: "Russia",
    severity: "Medium",
    severityColor: "bg-[#06B6D4]/20 text-[#06B6D4] border-[#06B6D4]/30",
    packetsBlocked: "3.2K"
  },
  {
    id: 5,
    timestamp: "2026-02-10 09:23:55",
    attackType: "XSS Attempt",
    sourceIP: "45.89.173.44",
    targetAsset: "Web-Application-Firewall",
    location: "Ukraine",
    severity: "Medium",
    severityColor: "bg-[#06B6D4]/20 text-[#06B6D4] border-[#06B6D4]/30",
    packetsBlocked: "156"
  },
  {
    id: 6,
    timestamp: "2026-02-10 07:50:31",
    attackType: "Credential Stuffing",
    sourceIP: "91.203.45.78",
    targetAsset: "User-Auth-Service",
    location: "Brazil",
    severity: "High",
    severityColor: "bg-[#F59E0B]/20 text-[#F59E0B] border-[#F59E0B]/30",
    packetsBlocked: "8.7K"
  },
  {
    id: 7,
    timestamp: "2026-02-10 05:12:08",
    attackType: "DNS Amplification",
    sourceIP: "172.56.203.101",
    targetAsset: "DNS-Resolver-01",
    location: "India",
    severity: "Critical",
    severityColor: "bg-[#EF4444]/20 text-[#EF4444] border-[#EF4444]/30",
    packetsBlocked: "1.8M"
  }
];

export function AttackAnalysisSection() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-[#EF4444]" />
          <span>Detailed Attack Analysis</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-gray-700 hover:bg-transparent">
                <TableHead className="text-gray-400">Timestamp</TableHead>
                <TableHead className="text-gray-400">Attack Type</TableHead>
                <TableHead className="text-gray-400">Source IP</TableHead>
                <TableHead className="text-gray-400">Target Asset</TableHead>
                <TableHead className="text-gray-400">Location</TableHead>
                <TableHead className="text-gray-400">Severity</TableHead>
                <TableHead className="text-gray-400 text-right">Packets Blocked</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {attackData.map((attack) => (
                <TableRow key={attack.id} className="border-gray-700 hover:bg-gray-700/30">
                  <TableCell className="font-mono text-sm text-gray-300">
                    {attack.timestamp}
                  </TableCell>
                  <TableCell className="text-gray-200 font-medium">
                    {attack.attackType}
                  </TableCell>
                  <TableCell className="font-mono text-sm text-[#06B6D4]">
                    {attack.sourceIP}
                  </TableCell>
                  <TableCell className="text-gray-300">
                    {attack.targetAsset}
                  </TableCell>
                  <TableCell className="text-gray-300">
                    {attack.location}
                  </TableCell>
                  <TableCell>
                    <Badge className={attack.severityColor}>
                      {attack.severity}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono text-sm text-right text-gray-300">
                    {attack.packetsBlocked}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
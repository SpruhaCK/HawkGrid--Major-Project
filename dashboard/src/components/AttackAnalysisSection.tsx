import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Shield, MapPin, Clock } from "lucide-react";

const attackData = [
  {
    id: 1,
    attackType: "SQL Injection",
    time: "14:32:05",
    ip: "185.24.76.11",
    location: "Frankfurt, Germany",
    severity: "High",
    severityColor: "bg-orange-600/20 text-orange-400 border-orange-500/30"
  },
  {
    id: 2,
    attackType: "DDoS Attempt",
    time: "16:11:47",
    ip: "102.56.87.90",
    location: "Lagos, Nigeria",
    severity: "Critical",
    severityColor: "bg-red-600/20 text-red-400 border-red-500/30"
  },
  {
    id: 3,
    attackType: "Suspicious Login",
    time: "18:22:03",
    ip: "45.67.89.101",
    location: "New Delhi, India",
    severity: "Medium",
    severityColor: "bg-yellow-600/20 text-yellow-400 border-yellow-500/30"
  }
];

export function AttackAnalysisSection() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-red-400" />
          <span>Detailed Attack Analysis</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-gray-700">
                <TableHead className="text-gray-300">Attack Type</TableHead>
                <TableHead className="text-gray-300">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>Time</span>
                  </div>
                </TableHead>
                <TableHead className="text-gray-300">IP Address</TableHead>
                <TableHead className="text-gray-300">
                  <div className="flex items-center space-x-1">
                    <MapPin className="h-4 w-4" />
                    <span>Location</span>
                  </div>
                </TableHead>
                <TableHead className="text-gray-300">Severity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {attackData.map((attack) => (
                <TableRow key={attack.id} className="border-gray-700 hover:bg-gray-800/30">
                  <TableCell className="font-medium text-gray-200">
                    {attack.attackType}
                  </TableCell>
                  <TableCell className="font-mono text-sm text-gray-400">
                    {attack.time}
                  </TableCell>
                  <TableCell className="font-mono text-sm text-cyan-400">
                    {attack.ip}
                  </TableCell>
                  <TableCell className="text-gray-300">
                    {attack.location}
                  </TableCell>
                  <TableCell>
                    <Badge className={attack.severityColor}>
                      {attack.severity}
                    </Badge>
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
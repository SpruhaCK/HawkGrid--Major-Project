import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ShieldCheck, Loader2, CheckCircle2, Send } from "lucide-react";

const countermeasures = [
  {
    id: 1,
    action: "Block IP 192.168.0.100 (AWS WAF)",
    status: "in_progress",
    statusText: "In Progress...",
    statusColor: "text-[#F59E0B]",
    statusIcon: Loader2,
    time: "Just now",
    animate: true
  },
  {
    id: 2,
    action: "Isolate Azure VM (Node-7)",
    status: "success",
    statusText: "Success ✅",
    statusColor: "text-[#22C55E]",
    statusIcon: CheckCircle2,
    time: "1 min ago",
    animate: false
  },
  {
    id: 3,
    action: "Snapshot Forensic Volume",
    status: "success",
    statusText: "Success ✅",
    statusColor: "text-[#22C55E]",
    statusIcon: CheckCircle2,
    time: "4 mins ago",
    animate: false
  },
  {
    id: 4,
    action: "Send Slack Alert to Admin",
    status: "sent",
    statusText: "Sent 📨",
    statusColor: "text-[#06B6D4]",
    statusIcon: Send,
    time: "5 mins ago",
    animate: false
  }
];

export function ActiveCountermeasures() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <ShieldCheck className="h-5 w-5 text-[#06B6D4]" />
          <span>Active Countermeasures</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {countermeasures.map((measure, index) => {
            const StatusIcon = measure.statusIcon;
            return (
              <div
                key={measure.id}
                className="relative pl-6 pb-4 border-l-2 border-gray-700 last:border-l-0 last:pb-0"
              >
                {/* Timeline dot */}
                <div 
                  className={`absolute left-[-5px] top-1 w-3 h-3 rounded-full border-2 ${
                    measure.status === "in_progress" 
                      ? "bg-[#F59E0B] border-[#F59E0B] animate-pulse" 
                      : measure.status === "success"
                      ? "bg-[#22C55E] border-[#22C55E]"
                      : "bg-[#06B6D4] border-[#06B6D4]"
                  }`}
                ></div>

                {/* Content */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-200">
                    {measure.action}
                  </div>
                  <div className="flex items-center justify-between">
                    <div className={`flex items-center space-x-1 text-sm font-medium ${measure.statusColor}`}>
                      <StatusIcon className={`h-4 w-4 ${measure.animate ? "animate-spin" : ""}`} />
                      <span>{measure.statusText}</span>
                    </div>
                    <div className="text-xs text-gray-400 font-mono">
                      {measure.time}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

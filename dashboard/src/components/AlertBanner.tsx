import { AlertTriangle } from "lucide-react";
import { Alert, AlertDescription } from "./ui/alert";

export function AlertBanner() {
  return (
    <div className="relative overflow-hidden">
      <Alert className="border-red-500/50 bg-red-950/30 backdrop-blur-sm">
        <AlertTriangle className="h-4 w-4 text-red-400" />
        <AlertDescription className="text-red-300">
          <div className="animate-pulse">
            ⚠️ Anomalous activity detected – Action required
          </div>
        </AlertDescription>
      </Alert>
    </div>
  );
}
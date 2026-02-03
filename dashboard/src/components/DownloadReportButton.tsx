import { Download } from "lucide-react";
import { Button } from "./ui/button";

export function DownloadReportButton() {
  const handleDownload = () => {
    // Simulate download functionality
    alert("Report download initiated...");
  };

  return (
    <Button 
      onClick={handleDownload}
      className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white px-8 py-3 rounded-lg shadow-lg hover:shadow-cyan-500/25 transition-all duration-200 border border-cyan-500/30"
    >
      <Download className="h-5 w-5 mr-2" />
      Download Full Report
    </Button>
  );
}
import { Shield } from "lucide-react";

export function Header() {
  return (
    <header className="mb-8">
      <div className="flex items-center space-x-3">
        <div className="relative">
          <Shield className="h-10 w-10 text-cyan-400" />
          <div className="absolute inset-0 bg-cyan-400 blur-lg opacity-30"></div>
        </div>
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-green-400 bg-clip-text text-transparent">
            HawkGrid
          </h1>
          <p className="text-gray-400 text-sm">Security Operations Center</p>
        </div>
      </div>
    </header>
  );
}
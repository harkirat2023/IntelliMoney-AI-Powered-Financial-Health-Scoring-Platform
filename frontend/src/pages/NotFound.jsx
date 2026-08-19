import { Link } from "react-router-dom";
import { Compass } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50/30 via-white to-white flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center mx-auto mb-6">
          <Compass size={28} className="text-emerald-600" />
        </div>
        <p className="text-sm font-semibold tracking-widest text-emerald-600 uppercase mb-2">404</p>
        <h1 className="text-3xl md:text-4xl font-bold text-neutral-900 tracking-tight mb-3">
          Page not found
        </h1>
        <p className="text-neutral-500 mb-8">
          The page you're looking for doesn't exist or may have moved.
        </p>
        <Link
          to="/"
          className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition-colors"
        >
          Back to home
        </Link>
      </div>
    </div>
  );
}
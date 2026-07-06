import { Outlet } from "react-router-dom";
import { Navbar } from "../sections/Navbar";
import { Footer } from "../sections/Footer";

export function LandingLayout() {
  return (
    <div className="landing-page min-h-screen bg-white font-sans antialiased">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

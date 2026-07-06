import { Link } from "react-router-dom";
import { BrainCircuit, Mail, MapPin, Phone, ArrowRight } from "lucide-react";

const footerLinks = [
  {
    label: "Product",
    links: [
      { label: "Features", href: "/features" },
      { label: "How It Works", href: "/#how-it-works" },
      { label: "FAQ", href: "/#faq" },
    ],
  },
  {
    label: "Resources",
    links: [
      { label: "Privacy Policy", href: "/privacy" },
      { label: "Terms of Service", href: "/terms" },
      { label: "Contact Us", href: "/contact" },
    ],
  },
  {
    label: "Company",
    links: [
      { label: "About Us", href: "/about" },
      { label: "Contact", href: "/contact" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="bg-neutral-900 text-neutral-300">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-2 font-bold text-xl text-white mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center">
                <BrainCircuit size={18} className="text-white" />
              </div>
              IntelliMoney
            </Link>
            <p className="text-sm text-neutral-400 leading-relaxed max-w-sm">
              India&apos;s first AI-powered financial intelligence platform. Smart budgeting, real-time insights, and an AI copilot to transform how you manage money.
            </p>
            <div className="flex flex-col gap-2 mt-4 text-sm text-neutral-400">
              <div className="flex items-center gap-2">
                <MapPin size={14} />
                <span>Bangalore, Karnataka, India</span>
              </div>
              <div className="flex items-center gap-2">
                <Mail size={14} />
                <span>hello@intellimoney.in</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone size={14} />
                <span>+91 1800-123-4567</span>
              </div>
            </div>
            <div className="mt-6">
              <p className="text-xs text-neutral-500 mb-2">Stay updated</p>
              <div className="flex">
                <input
                  type="email"
                  placeholder="Your email"
                  className="flex-1 px-3 py-2 text-xs bg-neutral-800 border border-neutral-700 rounded-l-lg text-neutral-300 placeholder-neutral-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30 transition-all"
                />
                <button className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-r-lg transition-all hover:shadow-lg hover:shadow-emerald-600/20 active:scale-95" aria-label="Subscribe">
                  <ArrowRight size={14} className="text-white" />
                </button>
              </div>
            </div>
          </div>
          {footerLinks.map((group) => (
            <div key={group.label}>
              <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">{group.label}</h4>
              <ul className="space-y-3">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <Link to={link.href} className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-12 pt-8 border-t border-neutral-800 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-neutral-500">&copy; {new Date().getFullYear()} IntelliMoney. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <Link to="/privacy" className="text-sm text-neutral-500 hover:text-neutral-300 transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="text-sm text-neutral-500 hover:text-neutral-300 transition-colors">Terms of Service</Link>
            <Link to="/contact" className="text-sm text-neutral-500 hover:text-neutral-300 transition-colors">Contact Us</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

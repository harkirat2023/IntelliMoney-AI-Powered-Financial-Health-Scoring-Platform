import { useState } from "react";
import { SectionHeading } from "../components/ui/SectionHeading";
import { Card } from "../components/ui/Card";
import { FadeIn } from "../components/animations/FadeIn";
import { Button } from "../components/ui/Button";
import { Mail, MapPin, Phone, Send, CheckCircle } from "lucide-react";

export function ContactPage() {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <FadeIn>
          <SectionHeading
            label="Contact"
            title="We'd Love to Hear From You"
            description="Have a question, suggestion, or just want to say hello? Drop us a message."
          />
        </FadeIn>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mt-12">
          <FadeIn>
            <Card variant="default">
              {submitted ? (
                <div className="text-center py-12">
                  <CheckCircle size={48} className="text-emerald-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-neutral-900 mb-2">Message Sent!</h3>
                  <p className="text-sm text-neutral-500">We'll get back to you within 24 hours.</p>
                  <Button variant="ghost" size="sm" className="mt-4" onClick={() => setSubmitted(false)}>
                    Send Another Message
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="contact-name" className="block text-sm font-medium text-neutral-700 mb-1">Name</label>
                      <input id="contact-name" type="text" required className="w-full px-3 py-2.5 text-sm border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500" placeholder="Your name" />
                    </div>
                    <div>
                      <label htmlFor="contact-email" className="block text-sm font-medium text-neutral-700 mb-1">Email</label>
                      <input id="contact-email" type="email" required className="w-full px-3 py-2.5 text-sm border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500" placeholder="you@example.com" />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="contact-subject" className="block text-sm font-medium text-neutral-700 mb-1">Subject</label>
                    <input id="contact-subject" type="text" required className="w-full px-3 py-2.5 text-sm border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500" placeholder="How can we help?" />
                  </div>
                  <div>
                    <label htmlFor="contact-message" className="block text-sm font-medium text-neutral-700 mb-1">Message</label>
                    <textarea id="contact-message" rows={5} required className="w-full px-3 py-2.5 text-sm border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 resize-none" placeholder="Tell us more..." />
                  </div>
                  <Button type="submit" variant="primary" className="w-full">
                    <Send size={16} />
                    Send Message
                  </Button>
                </form>
              )}
            </Card>
          </FadeIn>

          <FadeIn direction="right" delay={0.2}>
            <div className="space-y-4">
              {[
                { icon: Mail, label: "Email", value: "hello@intellimoney.in", detail: "We reply within 24 hours" },
                { icon: Phone, label: "Phone", value: "+91 1800-123-4567", detail: "Mon-Fri, 9 AM - 6 PM IST" },
                { icon: MapPin, label: "Office", value: "Bangalore, Karnataka, India", detail: "Koramangala, 560034" },
              ].map((item) => (
                <div key={item.label} className="flex items-start gap-3 p-4 bg-neutral-50 rounded-xl">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0">
                    <item.icon size={18} className="text-emerald-600" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-neutral-400">{item.label}</div>
                    <div className="text-sm font-semibold text-neutral-900">{item.value}</div>
                    <div className="text-xs text-neutral-400">{item.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </FadeIn>
        </div>
      </div>
    </div>
  );
}

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Activity, ShieldCheck, Cpu } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col bg-slate-950 text-white selection:bg-blue-500/30">
      
      {/* Navbar */}
      <nav className="w-full border-b border-white/10 bg-slate-950/50 backdrop-blur-md fixed top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="font-bold text-xl tracking-tighter flex items-center gap-2">
                <div className="h-6 w-6 bg-blue-600 rounded-md"></div>
                OptiRetina
            </div>
            <Link href="/login">
                <Button variant="ghost" className="text-sm font-medium hover:text-blue-400 hover:bg-transparent">
                    Staff Login
                </Button>
            </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-24 pb-12 md:pt-32 md:pb-20 lg:pt-48 lg:pb-32 px-6 overflow-hidden">
        {/* Abstract Background */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl pointer-events-none">
            <div className="absolute top-[20%] left-[10%] w-[300px] h-[300px] md:w-[500px] md:h-[500px] bg-blue-600/20 rounded-full blur-[80px] md:blur-[120px] mix-blend-screen animate-pulse"></div>
            <div className="absolute top-[30%] right-[10%] w-[250px] h-[250px] md:w-[400px] md:h-[400px] bg-teal-500/10 rounded-full blur-[60px] md:blur-[100px] mix-blend-screen"></div>
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-900/30 border border-blue-500/30 text-blue-300 text-xs font-medium mb-6">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                </span>
                Now powered by ResNet50
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-7xl font-bold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
                AI-Driven Vision <br/>
                <span className="text-blue-500">Diagnostics</span>
            </h1>
            
            <p className="text-base md:text-lg text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed px-4">
                Early detection of Diabetic Retinopathy made accessible. Upload fundus images and get instant, explainable grading reports.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link href="/login" className="w-full sm:w-auto">
                    <Button className="w-full sm:w-auto bg-blue-600 hover:bg-blue-500 text-white px-8 h-12 rounded-full font-medium transition-all hover:scale-105 shadow-lg shadow-blue-900/20">
                        Start Analysis <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </Link>
                <Link href="#features" className="w-full sm:w-auto">
                    <Button variant="outline" className="w-full sm:w-auto border-white/10 bg-white/5 hover:bg-white/10 text-white h-12 rounded-full px-8 backdrop-blur-sm">
                        Learn More
                    </Button>
                </Link>
            </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 bg-slate-900/50 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
            <div className="grid md:grid-cols-3 gap-8">
                <FeatureCard 
                    icon={<Cpu className="h-6 w-6 text-blue-400" />}
                    title="Deep Learning"
                    desc="Utilizes ResNet50 architecture for high-accuracy medical imaging inference."
                />
                <FeatureCard 
                    icon={<Activity className="h-6 w-6 text-teal-400" />}
                    title="Grad-CAM"
                    desc="Visual explainability overlays that highlight the specific regions contributing to the diagnosis."
                />
                <FeatureCard 
                    icon={<ShieldCheck className="h-6 w-6 text-indigo-400" />}
                    title="Secure & Private"
                    desc="Patient data is processed securely with options for local deployment to ensure strict privacy."
                />
            </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-white/5 text-center text-slate-600 text-sm">
        <p>&copy; 2024 OptiRetina System. For Research Use Only.</p>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
    return (
        <div className="p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
            <div className="h-12 w-12 bg-white/5 rounded-xl flex items-center justify-center mb-4">
                {icon}
            </div>
            <h3 className="text-xl font-semibold mb-2 text-white">{title}</h3>
            <p className="text-slate-400 leading-relaxed">
                {desc}
            </p>
        </div>
    )
}

import { Sidebar, MobileSidebar } from "@/components/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar />
      <main className="flex-1 w-full md:ml-64 transition-all duration-300 ease-in-out">
        <div className="md:hidden h-16 flex items-center px-4 border-b border-slate-200 bg-white sticky top-0 z-10 w-full">
            <MobileSidebar />
            <span className="font-bold text-lg text-slate-800 tracking-tight ml-2">OptiRetina</span>
        </div>
        <div className="p-4 md:p-8 max-w-7xl mx-auto">
            {children}
        </div>
      </main>
    </div>
  );
}

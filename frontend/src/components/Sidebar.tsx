'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Upload, History, LogOut, LayoutDashboard, Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { UserButton } from "@clerk/nextjs";
import { useState } from "react";

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Sidebar({ className }: SidebarProps) {
  return (
    <div className={cn("hidden md:flex h-screen w-64 bg-white border-r border-slate-200 flex-col p-4 fixed left-0 top-0 z-20", className)}>
       <SidebarContent />
    </div>
  )
}

export function MobileSidebar() {
    const [open, setOpen] = useState(false);

    return (
        <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden">
                    <Menu className="h-6 w-6" />
                </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-64 bg-white">
                <SheetHeader className="px-4 pt-4 text-left">
                    <SheetTitle>Menu</SheetTitle>
                </SheetHeader>
                <div className="flex flex-col h-full p-4 pt-2">
                    <SidebarContent onNavigate={() => setOpen(false)} />
                </div>
            </SheetContent>
        </Sheet>
    )
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
    const pathname = usePathname();

    const handleNavigation = () => {
        if (onNavigate) {
            onNavigate();
        }
    };

    return (
        <>
            <div className="mb-10 px-2 mt-4 flex items-center space-x-3">
                <div className="h-9 w-9 bg-blue-600 rounded-xl flex items-center justify-center shadow-md shadow-blue-200">
                    <LayoutDashboard className="h-5 w-5 text-white" />
                </div>
                <span className="font-bold text-xl text-slate-800 tracking-tight">OptiRetina</span>
            </div>
       
            <nav className="flex-1 space-y-1">
                <p className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Menu</p>
                <NavItem onClick={handleNavigation} href="/dashboard" icon={<Home size={18} />} label="Overview" active={pathname === '/dashboard'} />
                <NavItem onClick={handleNavigation} href="/dashboard/upload" icon={<Upload size={18} />} label="New Analysis" active={pathname === '/dashboard/upload'} />
                <NavItem onClick={handleNavigation} href="/dashboard/history" icon={<History size={18} />} label="Patient History" active={pathname?.startsWith('/dashboard/history')} />
            </nav>
       
            <div className="mt-auto pt-6 border-t border-slate-100">
                <div className="flex items-center gap-3 px-3 mb-4">
                    <UserButton 
                        afterSignOutUrl="/login" 
                        showName={true}
                        appearance={{
                            elements: {
                                userButtonBox: "flex flex-row-reverse",
                                userButtonOuterIdentifier: "font-medium text-slate-700 text-sm",
                                userButtonTrigger: "focus:shadow-none"
                            }
                        }}
                    />
                    <div className="text-xs hidden">
                         {/* Fallback layout if UserButton name not shown well */}
                    </div>
                </div>
            </div>
        </>
    )
}

function NavItem({ href, icon, label, active, onClick }: { href: string, icon: React.ReactNode, label: string, active?: boolean, onClick?: () => void }) {
    return (
        <Link href={href} onClick={onClick} className={cn(
            "flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium",
            active 
              ? "bg-blue-50 text-blue-700" 
              : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
        )}>
            {icon}
            <span>{label}</span>
        </Link>
    )
}

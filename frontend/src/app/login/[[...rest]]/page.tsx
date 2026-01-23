'use client';

import { SignIn } from '@clerk/nextjs';
import { Eye } from 'lucide-react';

export default function LoginPage() {
  return (
    <div className="flex min-h-screen bg-slate-900">
      {/* Left Side - Hero / Branding */}
      <div className="hidden lg:flex flex-col justify-center items-center w-1/2 p-12 bg-gradient-to-br from-blue-900 to-slate-900 text-white relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
             <div className="absolute top-[-20%] left-[-20%] w-[80%] h-[80%] bg-blue-500 rounded-full blur-[150px]"></div>
             <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] bg-teal-500 rounded-full blur-[150px]"></div>
        </div>
        
        <div className="z-10 text-center">
            <div className="mb-6 flex justify-center">
                <div className="h-20 w-20 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <Eye className="h-10 w-10 text-white" />
                </div>
            </div>
            <h1 className="text-5xl font-bold mb-4 tracking-tight">OptiRetina</h1>
            <p className="text-lg text-blue-100 max-w-md mx-auto leading-relaxed">
                Empowering early diagnosis of Diabetic Retinopathy with state-of-the-art AI.
            </p>
        </div>
      </div>

      {/* Right Side - Login Form - Clerk */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50 dark:bg-slate-900">
        <SignIn 
            appearance={{
                elements: {
                    card: "shadow-2xl border-0 bg-white/80 backdrop-blur-sm",
                    headerTitle: "text-2xl font-bold text-center text-slate-900",
                    headerSubtitle: "text-slate-500",
                    socialButtonsBlockButton: "border-slate-200 hover:bg-slate-50 text-slate-600",
                    formButtonPrimary: "bg-blue-700 hover:bg-blue-800 transition-all duration-200 py-3",
                    footerActionLink: "text-blue-600 hover:text-blue-500"
                }
            }}
            fallbackRedirectUrl="/dashboard"
        />
      </div>
    </div>
  );
}

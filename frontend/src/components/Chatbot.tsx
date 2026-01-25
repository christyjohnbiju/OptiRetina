import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { AlertCircle, Send, User, Bot, Sparkles, Loader2 } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";

interface ChatbotProps {
  prediction: string;
  confidence: number;
  tips: string[];
}

interface Message {
  role: "user" | "bot";
  content: string;
  timestamp: Date;
}

const QUICK_QUESTIONS = [
  "What is my current condition?",
  "Is this stage reversible?",
  "What food should I avoid?",
  "What precautions should I take?",
  "Should I see a doctor urgently?"
];

export function Chatbot({ prediction, confidence, tips }: ChatbotProps) {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      content: `Hello. I see you have been diagnosed with **${prediction.replace('_', ' ')}**. How can I assist you with your recovery or precautions today?`,
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
        scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = { role: "user", content: text, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const token = await getToken();
      const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
      
      const context = {
        prediction,
        confidence,
        tips
      };

      const res = await axios.post(`${API_URL}/chatbot/query`, {
        query: text,
        context: context
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const botMsg: Message = { 
        role: "bot", 
        content: res.data.response,
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, botMsg]);

    } catch (error) {
      console.error("Chat error", error);
      setMessages((prev) => [...prev, { 
        role: "bot", 
        content: "I apologize, but I'm having trouble connecting right now. Please try again later.",
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="flex flex-col h-[80vh] sm:h-[600px] border-blue-100 shadow-md">
      <CardHeader className="bg-slate-50 border-b pb-4">
        <CardTitle className="flex items-center text-blue-700">
            <Sparkles className="w-5 h-5 mr-2" />
            Medical Assistant
        </CardTitle>
        <CardDescription>
            Ask questions about your diagnosis and lifestyle. <br/>
            <span className="text-xs text-orange-600 font-medium flex items-center mt-1">
                <AlertCircle className="w-3 h-3 mr-1"/>
                AI advice is not a substitute for professional medical consultation.
            </span>
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-hidden p-4">
        <div className="h-full flex flex-col space-y-4 overflow-y-auto pr-2 custom-scrollbar">
            {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`flex items-start max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${m.role === 'user' ? 'bg-blue-600 ml-2' : 'bg-green-600 mr-2'}`}>
                            {m.role === 'user' ? <User className="w-4 h-4 text-white"/> : <Bot className="w-4 h-4 text-white"/>}
                        </div>
                        <div className={`p-3 rounded-lg text-sm ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-800 border'}`}>
                            <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
                            <span className={`text-[10px] mt-1 block opacity-70 ${m.role === 'user' ? 'text-blue-100' : 'text-slate-400'}`}>
                                {m.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </span>
                        </div>
                    </div>
                </div>
            ))}
            {loading && (
                <div className="flex justify-start">
                    <div className="bg-slate-50 border rounded-lg p-3 flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                        <span className="text-xs text-slate-500">Assistant is thinking...</span>
                    </div>
                </div>
            )}
            <div ref={scrollRef} />
        </div>
      </CardContent>

      <div className="p-2 bg-slate-50 border-t">
         {/* Quick Questions */}
        <div className="flex gap-2 overflow-x-auto pb-2 px-2 no-scrollbar mb-2">
            {QUICK_QUESTIONS.map((q, i) => (
                <Button 
                    key={i} 
                    variant="outline" 
                    size="sm" 
                    className="whitespace-nowrap rounded-full text-xs h-7 bg-white hover:bg-blue-50 hover:text-blue-600 border-slate-200"
                    onClick={() => handleSend(q)}
                    disabled={loading}
                >
                    {q}
                </Button>
            ))}
        </div>

        <CardFooter className="p-2 pt-0">
            <form 
                className="flex w-full space-x-2"
                onSubmit={(e) => {
                    e.preventDefault();
                    handleSend(input);
                }}
            >
                <Input 
                    placeholder="Type your health question..." 
                    value={input} 
                    onChange={(e) => setInput(e.target.value)} 
                    disabled={loading}
                    className="flex-1"
                />
                <Button type="submit" size="icon" disabled={loading || !input.trim()} className="shrink-0 bg-blue-600 hover:bg-blue-700">
                    <Send className="h-4 w-4" />
                </Button>
            </form>
        </CardFooter>
      </div>
    </Card>
  );
}

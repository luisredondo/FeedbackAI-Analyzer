"use client";

import { Database, FileText, Loader2, Send } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface DatasetInfo {
  filename: string;
  recordCount: number;
  lastUpdated: string;
  fileSize: string;
  status: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [datasetInfo, setDatasetInfo] = useState<DatasetInfo | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch dataset info on mount
  useEffect(() => {
    const fetchDatasetInfo = async () => {
      try {
        const response = await fetch('http://localhost:8000/dataset-info');
        if (response.ok) {
          const data = await response.json();
          setDatasetInfo(data);
        } else {
          // Fallback if backend is not available
          setDatasetInfo({
            filename: "feedback_corpus.csv",
            recordCount: 0,
            lastUpdated: "Backend not connected",
            fileSize: "Unknown",
            status: "Disconnected"
          });
        }
      } catch (error) {
        console.error('Error fetching dataset info:', error);
        setDatasetInfo({
          filename: "feedback_corpus.csv", 
          recordCount: 0,
          lastUpdated: "Backend not connected",
          fileSize: "Unknown",
          status: "Connection failed"
        });
      }
    };

    fetchDatasetInfo();
    
    // Add welcome message
    setMessages([{
      id: '1',
      text: "Hello! I'm your AI feedback analyzer. I can help you explore and understand customer feedback patterns, sentiment analysis, feature requests, and much more. What would you like to know about your data?",
      isUser: false,
      timestamp: new Date()
    }]);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call your Python backend here
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || "I apologize, but I couldn't process your request at the moment.",
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble connecting to the analysis service. Please make sure the backend is running on localhost:8000.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 p-6">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            FeedbackAI Analyzer
          </h1>
          <p className="text-gray-600 text-sm">
            Intelligent customer feedback analysis powered by AI
          </p>
        </div>

        {/* Dataset Information */}
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <div className="flex items-center mb-3">
            <Database className="w-5 h-5 text-blue-600 mr-2" />
            <h2 className="font-semibold text-gray-900">Data Source</h2>
          </div>
          
          {datasetInfo ? (
            <div className="space-y-2">
              <div className="flex items-center text-sm">
                <FileText className="w-4 h-4 text-gray-500 mr-2" />
                <span className="font-medium text-gray-700">
                  {datasetInfo.filename}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <p>{datasetInfo.recordCount} feedback records</p>
                <p>Size: {datasetInfo.fileSize}</p>
                <p>Updated: {datasetInfo.lastUpdated}</p>
                <div className="flex items-center mt-2">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    datasetInfo.status === 'Loaded' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className={`text-xs ${
                    datasetInfo.status === 'Loaded' ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {datasetInfo.status}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-500">Loading dataset info...</div>
          )}
        </div>

        {/* Feature Highlights */}
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">What you can ask:</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <div className="p-3 bg-gray-50 rounded">
              "What are the most common complaints?"
            </div>
            <div className="p-3 bg-gray-50 rounded">
              "Show me positive feedback trends"
            </div>
            <div className="p-3 bg-gray-50 rounded">
              "What features do users request most?"
            </div>
            <div className="p-3 bg-gray-50 rounded">
              "Analyze sentiment over time"
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Chat with your feedback data
          </h2>
          <p className="text-sm text-gray-600">
            Ask questions about customer feedback, patterns, and insights
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl px-4 py-3 rounded-lg ${
                  message.isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.text}</p>
                <p className={`text-xs mt-2 ${
                  message.isUser ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 text-gray-900 max-w-3xl px-4 py-3 rounded-lg">
                <div className="flex items-center">
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  <span>Analyzing your feedback data...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="bg-white border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your feedback data..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
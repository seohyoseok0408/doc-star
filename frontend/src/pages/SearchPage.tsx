import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { apiPost } from "@/utils/apiClient";

interface Message {
  text: string;
  sender: "user" | "ai";
}

interface SearchAskResponse {
  answer: string;
  sources: SourceItem[];
  latency_ms: number;
}

interface SourceItem {
  document_id: number;
  chunk_id: number | null;
  chunk_index: number | null;
  score: number;
  text: string | null;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false); // New state for dynamic layout
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (hasSearched) {
      scrollToBottom();
    }
  }, [messages, hasSearched]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setHasSearched(true); // Set to true after the first search
    const userMessage: Message = { text: query, sender: "user" };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setQuery("");
    setLoading(true);
    setError(null);

    try {
      const data = await apiPost<SearchAskResponse>("/api/search/ask", {
        question: query,
        top_k: 3,
      });

      const sourceText =
        data.sources.length > 0
          ? `\n\n참고 문서: ${data.sources
              .map((s) => `문서${s.document_id} (유사도 ${(s.score * 100).toFixed(0)}%)`)
              .join(", ")}`
          : "";

      const aiMessage: Message = { text: data.answer + sourceText, sender: "ai" };
      setMessages((prevMessages) => [...prevMessages, aiMessage]);
    } catch (err) {
      const errorMessage = (err as Error).message || "응답을 처리하는 중 오류가 발생했습니다.";
      setError(errorMessage);
      const errorMessageForChat: Message = { text: `오류: ${errorMessage}`, sender: "ai" };
      setMessages((prevMessages) => [...prevMessages, errorMessageForChat]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-4">
      {!hasSearched ? (
        // Initial Landing State: Centered search bar and intro
        <div className="flex flex-col flex-grow items-center justify-center container mx-auto max-w-3xl">
          <h1 className="text-4xl font-bold mb-4 text-center">무엇을 찾아드릴까요?</h1>
          <p className="text-lg text-gray-600 mb-8 text-center">
            문서 내용을 기반으로 AI가 답변을 제공합니다.
          </p>
          <div className="flex w-full items-center space-x-2 border rounded-lg p-2">
            <Input
              type="text"
              placeholder="궁금한 점을 입력하세요..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleSearch();
                }
              }}
              disabled={loading}
              className="flex-grow"
            />
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? "전송 중..." : "전송"}
            </Button>
          </div>
        </div>
      ) : (
        // Post-Search State: Chat-like interface
        <>
          <div className="container mx-auto max-w-3xl flex-grow overflow-y-auto pb-4 custom-scrollbar">
            <h1 className="text-3xl font-bold mb-6 text-center">Document Search</h1>

            <div className="flex flex-col space-y-4">
              {messages.length === 0 && !loading && !error && (
                <p className="text-center text-gray-500">
                  궁금한 점을 입력하고 문서 검색을 시작하세요.
                </p>
              )}

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <Card
                    className={`max-w-[70%] p-3 rounded-lg shadow-md ${
                      message.sender === "user"
                        ? "bg-blue-500 text-white"
                        : "bg-gray-200 text-gray-800"
                    }`}
                  >
                    <CardContent className="p-0">
                      <p>{message.text}</p>
                    </CardContent>
                  </Card>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <Card className="max-w-[70%] p-3 rounded-lg shadow-md bg-gray-200 text-gray-800">
                    <CardContent className="p-0">
                      <p>AI가 답변을 생성 중입니다...</p>
                    </CardContent>
                  </Card>
                </div>
              )}
              {error && (
                <div className="flex justify-start">
                  <Card className="max-w-[70%] p-3 rounded-lg shadow-md bg-red-100 text-red-800 border border-red-400">
                    <CardContent className="p-0">
                      <p>오류: {error}</p>
                    </CardContent>
                  </Card>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="container mx-auto max-w-3xl pt-4 mb-8">
            <div className="flex w-full items-center space-x-2 border rounded-lg p-2">
              <Input
                type="text"
                placeholder="메시지를 입력하세요..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleSearch();
                  }
                }}
                disabled={loading}
              />
              <Button onClick={handleSearch} disabled={loading}>
                {loading ? "전송 중..." : "전송"}
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

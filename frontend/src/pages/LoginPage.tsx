import axios from "axios";
import { LoginForm } from "@/components/login-form";
import { extractErrorInfo, type ApiResponse } from "@/utils/apiClient";
import { extractTokenFromHeader } from "@/utils/auth";
import { setToken } from "@/utils/auth";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      const res = await axios.post<ApiResponse<unknown>>(
        `${import.meta.env.VITE_BACKEND_API_BASE_URL}/login`,
        formData,
        {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const accessToken = extractTokenFromHeader(res);

      if (accessToken) {
        setToken(accessToken);
        navigate("/", { replace: true });
      } else {
        alert("로그인 처리 중 문제가 발생했습니다.");
      }
    } catch (error) {
      const { message } = extractErrorInfo(error);
      alert(`로그인 실패: ${message}`);
    }
  };
  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <LoginForm
        className="w-full max-w-sm"
        formData={formData}
        onChange={(e) => {
          setFormData({
            ...formData,
            [e.target.id]: e.target.value,
          });
        }}
        onSubmit={handleSubmit}
      />
    </div>
  );
}

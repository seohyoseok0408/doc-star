import { useState } from "react";
import { SignupForm } from "@/components/signup-form";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { extractErrorInfo } from "@/utils/apiClient";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    nickname: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }

    try {
      const body = {
        username: formData.username,
        password: formData.password,
        nickname: formData.nickname,
        email: formData.email,
      };
      await axios.post(`${import.meta.env.VITE_BACKEND_API_BASE_URL}/user`, body, {
        headers: { "Content-Type": "application/json" },
      });

      alert("회원가입 성공! 로그인해주세요.");
      navigate("/login", { replace: true });
    } catch (error) {
      const { message } = extractErrorInfo(error);
      alert(`회원가입 실패: ${message}`);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <SignupForm
        className="w-full max-w-sm"
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
      />
    </div>
  );
}

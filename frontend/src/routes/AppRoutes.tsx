import { Routes, Route } from "react-router-dom";

import Home from "@/pages/Home";
import RegisterPage from "@/pages/RegisterPage";
import LoginPage from "@/pages/LoginPage";
import ProtectedRoute from "./ProtectedRoute";
import NotFound from "@/pages/NotFound";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        {/* ProtectedRoute가 인증 후 <Layout>을 렌더링하고, 
           이 자식 라우트들은 <Layout> 내부의 <Outlet />에 표시 */}
        <Route path="/" element={<Home />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

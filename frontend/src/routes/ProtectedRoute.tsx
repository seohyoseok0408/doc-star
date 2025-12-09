import { Navigate, Outlet } from "react-router-dom";
import { isAuthenticated } from "@/utils/auth";
import Layout from "@/layout/Layout";

export default function ProtectedRoute() {
  const authenticated = isAuthenticated();

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Layout>
      <Outlet />
    </Layout>
  );
}

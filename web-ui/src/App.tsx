import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/Login";
import ProjectsPage from "./pages/Projects";
import { getToken } from "./api/client";
import type { ReactNode } from "react";

function Protected({ children }: { children: ReactNode }) {
  const token = getToken();
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/projects" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/projects"
        element={
          <Protected>
            <ProjectsPage />
          </Protected>
        }
      />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  );
}

import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import SummarizePage from "./pages/SummarizePage";
import HistoryPage from "./pages/HistoryPage";
import { getAccessToken } from "./api/auth";
import { ToastProvider } from "./components/ToastProvider";

function ProtectedRoute({ children }) {
  return getAccessToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/summarize"
          element={
            <ProtectedRoute>
              <SummarizePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/summarize" replace />} />
      </Routes>
    </ToastProvider>
  );
}

import { Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import Dashboard from "./pages/Dashboard";
import ScanQR from "./pages/ScanQR";
import Inbound from "./pages/Inbound";
import Outbound from "./pages/Outbound";
import WarehouseMap from "./pages/WarehouseMap";
import Reports from "./pages/Reports";

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scan" element={<ScanQR />} />
        <Route path="/inbound" element={<Inbound />} />
        <Route path="/outbound" element={<Outbound />} />
        <Route path="/warehouse-map" element={<WarehouseMap />} />
        <Route path="/reports" element={<Reports />} />
      </Route>
    </Routes>
  );
}
